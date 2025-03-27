"""
Tests for the CLI
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from click.testing import CliRunner

from llamavault.cli import cli


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def cli_runner():
    """Create a Click CLI runner"""
    return CliRunner()


class TestCLI:
    """Test the CLI"""

    def test_help(self, cli_runner):
        """Test the help command"""
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "LlamaVault - Secure credential management" in result.output

    def test_version(self, cli_runner):
        """Test the version option"""
        result = cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "LlamaVault version:" in result.output

    def test_init(self, cli_runner, temp_dir, monkeypatch):
        """Test initializing a vault"""
        # Mock getpass to return a password
        monkeypatch.setattr("getpass.getpass", lambda prompt: "test-password")
        
        result = cli_runner.invoke(cli, ["--vault-dir", temp_dir, "init"])
        assert result.exit_code == 0
        assert "Vault initialized successfully" in result.output
        
        # Check that the vault files were created
        assert os.path.exists(os.path.join(temp_dir, "vault.json"))
        assert os.path.exists(os.path.join(temp_dir, "config.json"))

    def test_add_and_get(self, cli_runner, temp_dir, monkeypatch):
        """Test adding and retrieving a credential"""
        # Mock getpass to return passwords
        monkeypatch.setattr("getpass.getpass", lambda prompt: "test-password" if "New" in prompt else "test-value" if "Enter value" in prompt else "test-password")
        
        # Initialize the vault
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "init"])
        
        # Add a credential
        result = cli_runner.invoke(cli, ["--vault-dir", temp_dir, "add", "test-key"])
        assert result.exit_code == 0
        assert "Added credential: test-key" in result.output
        
        # Get the credential
        result = cli_runner.invoke(cli, ["--vault-dir", temp_dir, "get", "test-key"])
        assert result.exit_code == 0
        assert "test-key: test-value" in result.output

    def test_list(self, cli_runner, temp_dir, monkeypatch):
        """Test listing credentials"""
        # Mock getpass to return passwords
        monkeypatch.setattr("getpass.getpass", lambda prompt: "test-password" if "New" in prompt or "Vault password" in prompt else "test-value1" if "Enter value for 'key1'" in prompt else "test-value2" if "Enter value for 'key2'" in prompt else "test-password")
        
        # Initialize the vault
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "init"])
        
        # Add some credentials
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "add", "key1"])
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "add", "key2"])
        
        # List credentials
        result = cli_runner.invoke(cli, ["--vault-dir", temp_dir, "list"])
        assert result.exit_code == 0
        assert "key1" in result.output
        assert "key2" in result.output

    def test_remove(self, cli_runner, temp_dir, monkeypatch):
        """Test removing a credential"""
        # Mock getpass to return passwords
        monkeypatch.setattr("getpass.getpass", lambda prompt: "test-password" if "New" in prompt or "Vault password" in prompt else "test-value" if "Enter value" in prompt else "test-password")
        
        # Mock confirm
        monkeypatch.setattr("rich.prompt.Confirm.ask", lambda prompt, default=None: True)
        
        # Initialize the vault
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "init"])
        
        # Add a credential
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "add", "test-key"])
        
        # Remove the credential
        result = cli_runner.invoke(cli, ["--vault-dir", temp_dir, "remove", "test-key"])
        assert result.exit_code == 0
        assert "Removed credential: test-key" in result.output
        
        # Verify it's gone by listing credentials
        result = cli_runner.invoke(cli, ["--vault-dir", temp_dir, "list"])
        assert result.exit_code == 0
        assert "No credentials found" in result.output

    def test_export(self, cli_runner, temp_dir, monkeypatch):
        """Test exporting credentials to a .env file"""
        # Mock getpass to return passwords
        monkeypatch.setattr("getpass.getpass", lambda prompt: "test-password" if "New" in prompt or "Vault password" in prompt else "test-value" if "Enter value" in prompt else "test-password")
        
        # Initialize the vault
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "init"])
        
        # Add a credential
        cli_runner.invoke(cli, ["--vault-dir", temp_dir, "add", "api_key"])
        
        # Export to .env file
        env_file = os.path.join(temp_dir, ".env")
        result = cli_runner.invoke(cli, ["--vault-dir", temp_dir, "export", env_file])
        assert result.exit_code == 0
        assert f"Credentials exported to: {env_file}" in result.output
        
        # Check the file contents
        with open(env_file, "r") as f:
            content = f.read()
            assert "API_KEY=test-value" in content 