"""
Tests for the web interface
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock

from llamavault.web.app import app as flask_app
from llamavault.vault import Vault


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_vault(temp_dir):
    """Create a test vault"""
    vault = Vault(vault_dir=temp_dir, password="test-password")
    vault.init(force=True)
    
    # Add some sample credentials
    vault.add_credential("api_key", "test-api-key")
    vault.add_credential("db_password", "test-db-password", metadata={"service": "postgres"})
    
    return vault


@pytest.fixture
def app(temp_dir):
    """Create a Flask test client"""
    flask_app.config.update({
        "TESTING": True,
        "VAULT_DIR": temp_dir,
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
    })
    
    with flask_app.test_client() as client:
        yield client


class TestWebApp:
    """Test the web interface"""
    
    def test_login_redirect(self, app):
        """Test that unauthenticated requests redirect to login"""
        response = app.get("/")
        assert response.status_code == 302
        assert "/login" in response.location
    
    def test_login_page(self, app):
        """Test that the login page loads"""
        response = app.get("/login")
        assert response.status_code == 200
        assert b"Unlock Vault" in response.data
    
    def test_login_success(self, app, test_vault, temp_dir):
        """Test successful login"""
        response = app.post("/login", data={
            "password": "test-password",
            "remember": False,
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Dashboard" in response.data
        assert b"Total Credentials" in response.data
        assert b"2" in response.data  # Should show 2 credentials
    
    def test_login_failure(self, app, test_vault):
        """Test login with wrong password"""
        response = app.post("/login", data={
            "password": "wrong-password",
            "remember": False,
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Invalid password" in response.data
    
    @patch("llamavault.web.app.get_vault")
    def test_credentials_list(self, mock_get_vault, app, test_vault):
        """Test the credentials list page"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.get("/credentials")
        assert response.status_code == 200
        assert b"Credentials" in response.data
        assert b"api_key" in response.data
        assert b"db_password" in response.data
    
    @patch("llamavault.web.app.get_vault")
    def test_credential_detail(self, mock_get_vault, app, test_vault):
        """Test viewing a credential detail"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.get("/credentials/api_key")
        assert response.status_code == 200
        assert b"Edit Credential: api_key" in response.data
        assert b"test-api-key" in response.data
    
    @patch("llamavault.web.app.get_vault")
    def test_add_credential(self, mock_get_vault, app, test_vault):
        """Test adding a new credential"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.post("/credentials/new", data={
            "name": "new_credential",
            "value": "new-value",
            "metadata": '{"service": "test"}',
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"new_credential" in response.data
        
        # Verify the credential was added to the vault
        cred = test_vault.get_credential("new_credential")
        assert cred == "new-value"
    
    @patch("llamavault.web.app.get_vault")
    def test_update_credential(self, mock_get_vault, app, test_vault):
        """Test updating an existing credential"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.post("/credentials/api_key", data={
            "name": "api_key",
            "value": "updated-value",
            "metadata": '{"service": "updated"}',
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"api_key updated successfully" in response.data
        
        # Verify the credential was updated in the vault
        cred = test_vault.get_credential("api_key")
        assert cred == "updated-value"
    
    @patch("llamavault.web.app.get_vault")
    def test_delete_credential(self, mock_get_vault, app, test_vault):
        """Test deleting a credential"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.post("/credentials/api_key/delete", follow_redirects=True)
        
        assert response.status_code == 200
        assert b"api_key deleted successfully" in response.data
        
        # Verify the credential was removed from the vault
        assert "api_key" not in test_vault.get_all_credentials()
    
    @patch("llamavault.web.app.get_vault")
    def test_export_form(self, mock_get_vault, app, test_vault):
        """Test the export form page"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.get("/export")
        
        assert response.status_code == 200
        assert b"Export Credentials" in response.data
        assert b"Convert credential names to uppercase" in response.data
    
    @patch("llamavault.web.app.get_vault")
    def test_backup_form(self, mock_get_vault, app, test_vault):
        """Test the backup form page"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.get("/backup")
        
        assert response.status_code == 200
        assert b"Backup Vault" in response.data
        assert b"Create Backup" in response.data
    
    def test_logout(self, app):
        """Test logging out"""
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.get("/logout", follow_redirects=True)
        
        assert response.status_code == 200
        assert b"You have been logged out" in response.data
        
        # Verify session was cleared
        with app.session_transaction() as session:
            assert "vault_password" not in session
    
    @patch("llamavault.web.app.get_vault")
    def test_api_list_credentials(self, mock_get_vault, app, test_vault):
        """Test the API endpoint for listing credentials"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.get("/api/credentials")
        
        assert response.status_code == 200
        assert response.json.get("api_key") is not None
        assert response.json.get("db_password") is not None
        # Values should not be included in the list endpoint
        assert "value" not in response.json.get("api_key")
        assert "metadata" in response.json.get("db_password")
    
    @patch("llamavault.web.app.get_vault")
    def test_api_get_credential(self, mock_get_vault, app, test_vault):
        """Test the API endpoint for getting a credential"""
        # Mock the get_vault function to return our test vault
        mock_get_vault.return_value = test_vault
        
        # Set the session to simulate being logged in
        with app.session_transaction() as session:
            session["vault_password"] = "test-password"
        
        response = app.get("/api/credentials/api_key")
        
        assert response.status_code == 200
        assert response.json.get("name") == "api_key"
        assert response.json.get("value") == "test-api-key" 