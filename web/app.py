#!/usr/bin/env python3
"""
LlamaVault Web Interface

This module provides a Flask-based web interface for managing credentials in LlamaVault.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from llamavault.core import LlamaVault, CredentialType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llamavault.web")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("LLAMAVAULT_SECRET_KEY", os.urandom(24).hex())
CORS(app)

# Initialize vault
vault_path = os.environ.get("LLAMAVAULT_PATH")
vault = LlamaVault(vault_path)

# User management (simple file-based for demonstration)
users_file = Path(vault_path or "~/.llamavault").expanduser() / "users.json"
if not users_file.exists():
    # Create default admin user if no users file exists
    with open(users_file, "w") as f:
        json.dump({
            "admin": {
                "password": generate_password_hash("changeme"),
                "role": "admin"
            }
        }, f, indent=2)
    logger.info(f"Created default admin user (username: admin, password: changeme)")

# Load users
with open(users_file, "r") as f:
    users = json.load(f)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login", next=request.url))
        if users.get(session["username"], {}).get("role") != "admin":
            flash("Admin privileges required", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    """Landing page."""
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in users and check_password_hash(users[username]["password"], password):
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        
        flash("Invalid username or password", "danger")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout route."""
    session.pop("username", None)
    flash("You have been logged out", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard."""
    credentials = vault.list_credentials()
    return render_template("dashboard.html", credentials=credentials)


@app.route("/credentials")
@login_required
def list_credentials():
    """List all credentials."""
    tag = request.args.get("tag")
    cred_type = request.args.get("type")
    
    try:
        credentials = vault.list_credentials(tag=tag, cred_type=cred_type)
        return jsonify({"success": True, "credentials": credentials})
    except Exception as e:
        logger.error(f"Error listing credentials: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/credentials/<name>")
@login_required
def get_credential(name):
    """Get a specific credential."""
    try:
        credential = vault.get_credential(name)
        return jsonify({"success": True, "credential": credential})
    except Exception as e:
        logger.error(f"Error retrieving credential: {e}")
        return jsonify({"success": False, "error": str(e)}), 404


@app.route("/credentials", methods=["POST"])
@login_required
def add_credential():
    """Add a new credential."""
    try:
        data = request.json
        
        name = data.get("name")
        value = data.get("value")
        cred_type = CredentialType(data.get("type", "api_key"))
        tags = data.get("tags")
        metadata = data.get("metadata")
        
        vault.add_credential(name, value, cred_type, tags, metadata)
        
        return jsonify({"success": True, "message": f"Credential '{name}' added successfully"})
    except Exception as e:
        logger.error(f"Error adding credential: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/credentials/<name>", methods=["PUT"])
@login_required
def update_credential(name):
    """Update a credential's value."""
    try:
        data = request.json
        new_value = data.get("value")
        
        vault.rotate_credential(name, new_value)
        
        return jsonify({"success": True, "message": f"Credential '{name}' updated successfully"})
    except Exception as e:
        logger.error(f"Error updating credential: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/credentials/<name>", methods=["DELETE"])
@login_required
def remove_credential(name):
    """Remove a credential."""
    try:
        vault.remove_credential(name)
        return jsonify({"success": True, "message": f"Credential '{name}' removed successfully"})
    except Exception as e:
        logger.error(f"Error removing credential: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/users")
@admin_required
def list_users():
    """List all users (admin only)."""
    return jsonify({"success": True, "users": [{"username": u, "role": d["role"]} for u, d in users.items()]})


@app.route("/users", methods=["POST"])
@admin_required
def add_user():
    """Add a new user (admin only)."""
    try:
        data = request.json
        
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "user")
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password are required"}), 400
            
        if username in users:
            return jsonify({"success": False, "error": f"User '{username}' already exists"}), 400
            
        users[username] = {
            "password": generate_password_hash(password),
            "role": role
        }
        
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
            
        return jsonify({"success": True, "message": f"User '{username}' added successfully"})
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/users/<username>", methods=["DELETE"])
@admin_required
def remove_user(username):
    """Remove a user (admin only)."""
    try:
        if username not in users:
            return jsonify({"success": False, "error": f"User '{username}' not found"}), 404
            
        if username == session.get("username"):
            return jsonify({"success": False, "error": "Cannot delete your own account"}), 400
            
        del users[username]
        
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
            
        return jsonify({"success": True, "message": f"User '{username}' removed successfully"})
    except Exception as e:
        logger.error(f"Error removing user: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/analyze", methods=["POST"])
@login_required
def analyze_repo():
    """Analyze a repository for configuration patterns."""
    try:
        data = request.json
        repo_path = data.get("repo_path")
        
        if not repo_path:
            return jsonify({"success": False, "error": "Repository path is required"}), 400
            
        analysis = vault.analyze_configuration(repo_path)
        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        logger.error(f"Error analyzing repository: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/generate", methods=["POST"])
@login_required
def generate_config():
    """Generate configuration for a repository."""
    try:
        data = request.json
        repo_path = data.get("repo_path")
        format = data.get("format", "env")
        
        if not repo_path:
            return jsonify({"success": False, "error": "Repository path is required"}), 400
            
        config = vault.generate_configuration(repo_path, format)
        return jsonify({"success": True, "config": config})
    except Exception as e:
        logger.error(f"Error generating configuration: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


def main():
    """Run the Flask application."""
    host = os.environ.get("LLAMAVAULT_HOST", "127.0.0.1")
    port = int(os.environ.get("LLAMAVAULT_PORT", 5000))
    debug = os.environ.get("LLAMAVAULT_DEBUG", "false").lower() == "true"
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main() 