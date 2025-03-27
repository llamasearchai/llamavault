"""
Web interface for LlamaVault credential management
"""

import os
import json
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional as OptionalValidator
from werkzeug.security import generate_password_hash, check_password_hash

from ..vault import Vault
from ..exceptions import VaultError, CredentialNotFoundError, AuthenticationError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llamavault.web")

# Create Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("LLAMAVAULT_SECRET_KEY", secrets.token_hex(32))
app.config["VAULT_DIR"] = os.environ.get("LLAMAVAULT_DIR")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Setup CSRF protection
csrf = CSRFProtect(app)

# Form definitions
class LoginForm(FlaskForm):
    password = PasswordField("Vault Password", validators=[DataRequired()])
    remember = BooleanField("Remember Password (30 minutes)")
    submit = SubmitField("Unlock Vault")

class CredentialForm(FlaskForm):
    name = StringField("Credential Name", validators=[DataRequired(), Length(min=1, max=128)])
    value = StringField("Value", validators=[DataRequired()])
    metadata = TextAreaField("Metadata (JSON)", validators=[OptionalValidator()])
    submit = SubmitField("Save Credential")

# Helper functions
def get_vault() -> Optional[Vault]:
    """Get vault instance using the password stored in session"""
    if "vault_password" not in session:
        return None
    
    try:
        vault = Vault(
            vault_dir=app.config.get("VAULT_DIR"),
            password=session["vault_password"]
        )
        return vault
    except Exception as e:
        logger.error(f"Error creating vault instance: {e}")
        flash(f"Error accessing vault: {e}", "danger")
        return None

def requires_auth(f):
    """Decorator to require authentication"""
    def decorated(*args, **kwargs):
        if "vault_password" not in session:
            flash("Please unlock the vault first", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# Routes
@app.route("/", methods=["GET"])
def index():
    """Home page / dashboard"""
    # If not authenticated, redirect to login
    if "vault_password" not in session:
        return redirect(url_for("login"))
    
    vault = get_vault()
    if not vault:
        return redirect(url_for("login"))
    
    try:
        credentials = vault.get_all_credentials()
        # Count credentials
        credential_count = len(credentials)
        # Get stats
        oldest = None
        newest = None
        
        for cred in credentials.values():
            if oldest is None or (cred.created_at and cred.created_at < oldest.created_at):
                oldest = cred
            if newest is None or (cred.created_at and cred.created_at > newest.created_at):
                newest = cred
        
        return render_template(
            "dashboard.html",
            credential_count=credential_count,
            credentials=credentials,
            oldest=oldest,
            newest=newest
        )
    except VaultError as e:
        flash(f"Error accessing vault: {e}", "danger")
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    form = LoginForm()
    
    if form.validate_on_submit():
        password = form.password.data
        remember = form.remember.data
        
        try:
            # Try to unlock the vault
            vault = Vault(
                vault_dir=app.config.get("VAULT_DIR"),
                password=password
            )
            
            # Store password in session
            session["vault_password"] = password
            
            # Set session expiration
            if remember:
                app.permanent_session_lifetime = timedelta(minutes=30)
                session.permanent = True
            else:
                app.permanent_session_lifetime = timedelta(minutes=5)
                session.permanent = True
            
            # Get next URL if set
            next_url = request.args.get("next", url_for("index"))
            
            flash("Vault unlocked successfully", "success")
            return redirect(next_url)
        
        except AuthenticationError:
            flash("Invalid password", "danger")
        except VaultError as e:
            flash(f"Error unlocking vault: {e}", "danger")
    
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Logout and clear session"""
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))

@app.route("/credentials", methods=["GET"])
@requires_auth
def list_credentials():
    """List all credentials"""
    vault = get_vault()
    if not vault:
        return redirect(url_for("login"))
    
    try:
        credentials = vault.get_all_credentials()
        return render_template("credentials.html", credentials=credentials)
    except VaultError as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for("index"))

@app.route("/credentials/new", methods=["GET", "POST"])
@requires_auth
def new_credential():
    """Create a new credential"""
    form = CredentialForm()
    
    if form.validate_on_submit():
        name = form.name.data
        value = form.value.data
        metadata_str = form.metadata.data
        
        vault = get_vault()
        if not vault:
            return redirect(url_for("login"))
        
        try:
            # Parse metadata if provided
            metadata = {}
            if metadata_str:
                try:
                    metadata = json.loads(metadata_str)
                    if not isinstance(metadata, dict):
                        flash("Metadata must be a JSON object", "danger")
                        return render_template("credential_form.html", form=form, is_new=True)
                except json.JSONDecodeError:
                    flash("Invalid JSON in metadata field", "danger")
                    return render_template("credential_form.html", form=form, is_new=True)
            
            # Add credential
            vault.add_credential(name, value, metadata=metadata)
            
            flash(f"Credential '{name}' added successfully", "success")
            return redirect(url_for("list_credentials"))
        except VaultError as e:
            flash(f"Error: {e}", "danger")
    
    return render_template("credential_form.html", form=form, is_new=True)

@app.route("/credentials/<name>", methods=["GET", "POST"])
@requires_auth
def edit_credential(name):
    """Edit an existing credential"""
    vault = get_vault()
    if not vault:
        return redirect(url_for("login"))
    
    try:
        # Get existing credential
        cred = vault.get_credential_object(name)
        
        # Create form
        form = CredentialForm(obj=cred)
        
        # Set initial values
        if request.method == "GET":
            form.name.data = name
            form.value.data = cred.value
            if cred.metadata:
                form.metadata.data = json.dumps(cred.metadata, indent=2)
        
        if form.validate_on_submit():
            # Update credential
            new_name = form.name.data
            new_value = form.value.data
            metadata_str = form.metadata.data
            
            # Parse metadata if provided
            metadata = {}
            if metadata_str:
                try:
                    metadata = json.loads(metadata_str)
                    if not isinstance(metadata, dict):
                        flash("Metadata must be a JSON object", "danger")
                        return render_template("credential_form.html", form=form, is_new=False)
                except json.JSONDecodeError:
                    flash("Invalid JSON in metadata field", "danger")
                    return render_template("credential_form.html", form=form, is_new=False)
            
            # Handle name change
            if new_name != name:
                # Remove old credential and add new one
                vault.remove_credential(name)
                vault.add_credential(new_name, new_value, metadata=metadata)
                flash(f"Credential renamed from '{name}' to '{new_name}'", "success")
            else:
                # Update value and metadata
                vault.update_credential(name, new_value, metadata=metadata)
                flash(f"Credential '{name}' updated successfully", "success")
            
            return redirect(url_for("list_credentials"))
        
        return render_template("credential_form.html", form=form, is_new=False, name=name)
    
    except CredentialNotFoundError:
        flash(f"Credential '{name}' not found", "danger")
        return redirect(url_for("list_credentials"))
    except VaultError as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for("list_credentials"))

@app.route("/credentials/<name>/delete", methods=["POST"])
@requires_auth
def delete_credential(name):
    """Delete a credential"""
    vault = get_vault()
    if not vault:
        return redirect(url_for("login"))
    
    try:
        vault.remove_credential(name)
        flash(f"Credential '{name}' deleted successfully", "success")
    except CredentialNotFoundError:
        flash(f"Credential '{name}' not found", "danger")
    except VaultError as e:
        flash(f"Error: {e}", "danger")
    
    return redirect(url_for("list_credentials"))

@app.route("/export", methods=["GET", "POST"])
@requires_auth
def export_env():
    """Export credentials to a .env file"""
    if request.method == "POST":
        uppercase = request.form.get("uppercase", "1") == "1"
        
        vault = get_vault()
        if not vault:
            return redirect(url_for("login"))
        
        try:
            # Generate env content
            env_content = vault.export_env_string(uppercase=uppercase)
            
            # Return as file download
            response = app.response_class(
                env_content,
                mimetype="text/plain",
                headers={"Content-Disposition": "attachment;filename=.env"}
            )
            return response
        except VaultError as e:
            flash(f"Error exporting credentials: {e}", "danger")
    
    return render_template("export.html")

@app.route("/backup", methods=["GET", "POST"])
@requires_auth
def backup():
    """Backup the vault"""
    if request.method == "POST":
        vault = get_vault()
        if not vault:
            return redirect(url_for("login"))
        
        try:
            backup_path = vault.backup()
            flash(f"Backup created successfully at {backup_path}", "success")
        except VaultError as e:
            flash(f"Error creating backup: {e}", "danger")
    
    return render_template("backup.html")

@app.route("/api/credentials", methods=["GET"])
@requires_auth
def api_list_credentials():
    """API endpoint to list all credentials"""
    vault = get_vault()
    if not vault:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        credentials = vault.get_all_credentials()
        result = {}
        
        for name, cred in credentials.items():
            result[name] = {
                "created_at": cred.created_at.isoformat() if cred.created_at else None,
                "updated_at": cred.updated_at.isoformat() if cred.updated_at else None,
                "last_accessed": cred.last_accessed.isoformat() if cred.last_accessed else None,
                "metadata": cred.metadata,
                # Don't include the actual value for security
            }
        
        return jsonify(result)
    except VaultError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/credentials/<name>", methods=["GET"])
@requires_auth
def api_get_credential(name):
    """API endpoint to get a credential"""
    vault = get_vault()
    if not vault:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        cred = vault.get_credential_object(name)
        result = {
            "name": name,
            "value": cred.value,
            "created_at": cred.created_at.isoformat() if cred.created_at else None,
            "updated_at": cred.updated_at.isoformat() if cred.updated_at else None,
            "last_accessed": cred.last_accessed.isoformat() if cred.last_accessed else None,
            "metadata": cred.metadata,
        }
        
        return jsonify(result)
    except CredentialNotFoundError:
        return jsonify({"error": f"Credential '{name}' not found"}), 404
    except VaultError as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template("error.html", error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template("error.html", error_code=500, error_message="Server error"), 500

if __name__ == "__main__":
    app.run(debug=True) 