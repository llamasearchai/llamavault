"""
Tests for the Vault class
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch

from llamavault.vault import Vault
from llamavault.exceptions import (
    AuthenticationError,
    CredentialNotFoundError,
    ConfigurationError,
    VaultError
)


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
    return vault


class TestVault:
    """Test the Vault class"""

    def test_init_vault(self, temp_dir):
        """Test initializing a new vault"""
        vault = Vault(vault_dir=temp_dir, password="test-password")
        vault.init()

        # Check that the vault directory exists
        vault_path = Path(temp_dir) / Vault.DEFAULT_VAULT_FILE
        config_path = Path(temp_dir) / Vault.DEFAULT_CONFIG_FILE

        assert vault_path.exists()
        assert config_path.exists()

        # Check that the config file has the correct format
        with open(config_path, "r") as f:
            config = json.load(f)
            assert "salt" in config
            assert "version" in config

    def test_init_existing_vault(self, test_vault, temp_dir):
        """Test initializing a vault that already exists"""
        # Try to initialize again without force
        with pytest.raises(VaultError):
            vault = Vault(vault_dir=temp_dir, password="test-password")
            vault.init()

        # Initialize with force
        vault = Vault(vault_dir=temp_dir, password="test-password")
        vault.init(force=True)

        # Check that the vault was re-initialized
        vault_path = Path(temp_dir) / Vault.DEFAULT_VAULT_FILE
        config_path = Path(temp_dir) / Vault.DEFAULT_CONFIG_FILE
        
        assert vault_path.exists()
        assert config_path.exists()

    def test_add_and_get_credential(self, test_vault):
        """Test adding and retrieving a credential"""
        # Add a credential
        test_vault.add_credential("test-key", "test-value")

        # Get the credential
        value = test_vault.get_credential("test-key")
        assert value == "test-value"

        # Get the credential object
        cred = test_vault.get_credential_object("test-key")
        assert cred.value == "test-value"
        assert cred.created_at is not None
        assert cred.updated_at is not None
        assert cred.last_accessed is not None

    def test_add_credential_with_metadata(self, test_vault):
        """Test adding a credential with metadata"""
        metadata = {"service": "test", "expiry": "2023-12-31"}
        test_vault.add_credential("test-key", "test-value", metadata=metadata)

        # Get the credential object
        cred = test_vault.get_credential_object("test-key")
        assert cred.metadata == metadata

    def test_get_nonexistent_credential(self, test_vault):
        """Test retrieving a credential that doesn't exist"""
        with pytest.raises(CredentialNotFoundError):
            test_vault.get_credential("nonexistent-key")

    def test_remove_credential(self, test_vault):
        """Test removing a credential"""
        # Add a credential
        test_vault.add_credential("test-key", "test-value")

        # Remove the credential
        test_vault.remove_credential("test-key")

        # Try to get the credential
        with pytest.raises(CredentialNotFoundError):
            test_vault.get_credential("test-key")

    def test_remove_nonexistent_credential(self, test_vault):
        """Test removing a credential that doesn't exist"""
        with pytest.raises(CredentialNotFoundError):
            test_vault.remove_credential("nonexistent-key")

    def test_update_credential(self, test_vault):
        """Test updating a credential"""
        # Add a credential
        test_vault.add_credential("test-key", "test-value")

        # Update the credential
        test_vault.update_credential("test-key", "new-value")

        # Get the credential
        value = test_vault.get_credential("test-key")
        assert value == "new-value"

    def test_update_credential_with_metadata(self, test_vault):
        """Test updating a credential with metadata"""
        # Add a credential
        metadata = {"service": "test"}
        test_vault.add_credential("test-key", "test-value", metadata=metadata)

        # Update the credential with new metadata
        new_metadata = {"service": "test", "environment": "prod"}
        test_vault.update_credential("test-key", "test-value", metadata=new_metadata)

        # Get the credential object
        cred = test_vault.get_credential_object("test-key")
        assert cred.metadata == new_metadata

    def test_update_nonexistent_credential(self, test_vault):
        """Test updating a credential that doesn't exist"""
        with pytest.raises(CredentialNotFoundError):
            test_vault.update_credential("nonexistent-key", "new-value")

    def test_get_all_credentials(self, test_vault):
        """Test retrieving all credentials"""
        # Add some credentials
        test_vault.add_credential("key1", "value1")
        test_vault.add_credential("key2", "value2")
        test_vault.add_credential("key3", "value3")

        # Get all credentials
        credentials = test_vault.get_all_credentials()
        
        assert len(credentials) == 3
        assert "key1" in credentials
        assert "key2" in credentials
        assert "key3" in credentials
        assert credentials["key1"].value == "value1"
        assert credentials["key2"].value == "value2"
        assert credentials["key3"].value == "value3"

    def test_wrong_password(self, temp_dir):
        """Test opening a vault with the wrong password"""
        # Create a vault
        vault = Vault(vault_dir=temp_dir, password="correct-password")
        vault.init(force=True)
        
        # Try to open with wrong password
        with pytest.raises(AuthenticationError):
            Vault(vault_dir=temp_dir, password="wrong-password")

    def test_export_env_string(self, test_vault):
        """Test exporting credentials as environment variables"""
        # Add some credentials
        test_vault.add_credential("api_key", "secret123")
        test_vault.add_credential("database_url", "postgres://user:pass@localhost/db")
        
        # Export as environment variables
        env_string = test_vault.export_env_string(uppercase=True)
        
        assert "API_KEY=secret123" in env_string
        assert "DATABASE_URL=postgres://user:pass@localhost/db" in env_string
        
        # Export with lowercase
        env_string = test_vault.export_env_string(uppercase=False)
        
        assert "api_key=secret123" in env_string
        assert "database_url=postgres://user:pass@localhost/db" in env_string

    def test_export_env_file(self, test_vault, temp_dir):
        """Test exporting credentials to an env file"""
        # Add some credentials
        test_vault.add_credential("api_key", "secret123")
        test_vault.add_credential("database_url", "postgres://user:pass@localhost/db")
        
        # Export to a file
        env_file = os.path.join(temp_dir, ".env")
        test_vault.export_env_file(env_file)
        
        # Check the file contents
        with open(env_file, "r") as f:
            content = f.read()
            assert "API_KEY=secret123" in content
            assert "DATABASE_URL=postgres://user:pass@localhost/db" in content

    def test_backup(self, test_vault, temp_dir):
        """Test creating a backup"""
        # Add a credential
        test_vault.add_credential("test-key", "test-value")
        
        # Create a backup
        backup_dir = os.path.join(temp_dir, "backups")
        backup_path = test_vault.backup(backup_dir=backup_dir)
        
        # Check that the backup file exists
        assert os.path.exists(backup_path)
        
        # Make sure we can restore from the backup
        # First, clear the vault
        test_vault.init(force=True)
        
        # Add a different credential to confirm the restore works
        test_vault.add_credential("different-key", "different-value")
        
        # TODO: Implement restore functionality and test it here
        # test_vault.restore(backup_path)
        # value = test_vault.get_credential("test-key")
        # assert value == "test-value"
        # with pytest.raises(CredentialNotFoundError):
        #     test_vault.get_credential("different-key")

    def test_change_password(self, test_vault, temp_dir):
        """Test changing the vault password"""
        # Add a credential
        test_vault.add_credential("test-key", "test-value")
        
        # Change the password
        test_vault.change_password("new-password")
        
        # Try to open with old password
        with pytest.raises(AuthenticationError):
            Vault(vault_dir=temp_dir, password="test-password")
        
        # Open with new password
        vault = Vault(vault_dir=temp_dir, password="new-password")
        
        # Verify the credential is still there
        value = vault.get_credential("test-key")
        assert value == "test-value" 