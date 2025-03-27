#!/usr/bin/env python3
"""
Basic usage examples for LlamaVault.

This script demonstrates the core functionality of LlamaVault:
- Creating and initializing a vault
- Adding and retrieving credentials
- Working with metadata
- Exporting credentials to environment variables
"""

import os
import getpass
from datetime import datetime
from pathlib import Path

from llamavault import Vault, CredentialNotFoundError


def create_vault():
    """Create and initialize a new vault."""
    # Get a password for the vault
    password = getpass.getpass("Enter a new vault password: ")
    
    # Create a vault instance
    vault = Vault(password=password)
    
    # Initialize the vault (creates necessary files)
    vault.init(force=True)  # force=True will overwrite an existing vault
    
    print(f"Vault initialized at: {Path.home() / '.llamavault'}")
    return vault


def add_credentials(vault):
    """Add some example credentials to the vault."""
    # Add a simple credential
    vault.add_credential("database_password", "db-password-123")
    print("Added database_password credential")
    
    # Add a credential with metadata
    vault.add_credential(
        "openai_api_key",
        "sk-example12345",
        metadata={
            "service": "OpenAI",
            "environment": "development",
            "created_at": datetime.now().isoformat(),
            "owner": "data-science-team"
        }
    )
    print("Added openai_api_key credential with metadata")
    
    # Add another credential
    vault.add_credential(
        "aws_access_key",
        "AKIAEXAMPLE12345",
        metadata={
            "service": "AWS",
            "environment": "development",
            "secret_key_name": "aws_secret_key"
        }
    )
    print("Added aws_access_key credential")
    
    # Add related credential
    vault.add_credential("aws_secret_key", "aws-secret-example12345")
    print("Added aws_secret_key credential")


def get_credentials(vault):
    """Retrieve credentials from the vault."""
    # Get a simple credential value
    db_password = vault.get_credential("database_password")
    print(f"Retrieved database_password: {db_password}")
    
    # Get a credential with its metadata
    openai_key = vault.get_credential_object("openai_api_key")
    print(f"Retrieved openai_api_key: {openai_key.value}")
    print(f"Metadata: {openai_key.metadata}")
    
    # Try to get a non-existent credential
    try:
        vault.get_credential("nonexistent_credential")
    except CredentialNotFoundError:
        print("Correctly handled non-existent credential")


def update_credentials(vault):
    """Update existing credentials."""
    # Update a credential's value
    vault.update_credential("database_password", "new-db-password-456")
    print("Updated database_password value")
    
    # Update a credential's metadata
    openai_key = vault.get_credential_object("openai_api_key")
    metadata = openai_key.metadata.copy() if openai_key.metadata else {}
    metadata["environment"] = "production"
    metadata["updated_at"] = datetime.now().isoformat()
    
    vault.update_credential("openai_api_key", openai_key.value, metadata)
    print("Updated openai_api_key metadata")
    
    # Verify the update
    updated_key = vault.get_credential_object("openai_api_key")
    print(f"Updated metadata: {updated_key.metadata}")


def list_credentials(vault):
    """List all credentials in the vault."""
    # Get all credential names
    credential_names = vault.list_credentials()
    print(f"All credentials: {', '.join(credential_names)}")
    
    # Get all credential objects
    all_credentials = vault.get_all_credentials()
    
    # Display details of each credential
    print("\nCredential details:")
    for name, credential in all_credentials.items():
        print(f"- {name}: Created {credential.created_at.strftime('%Y-%m-%d')}")
        if credential.metadata:
            print(f"  Metadata: {credential.metadata}")


def export_credentials(vault):
    """Export credentials to environment variables."""
    # Export all credentials to environment variables
    env_vars = vault.export_env()
    
    # Check environment variables
    print("\nExported environment variables:")
    for name, value in env_vars.items():
        masked_value = value[:3] + "..." if len(value) > 3 else "***"
        print(f"- {name}={masked_value}")
    
    # Export to a .env file
    vault.export_env_file(".env.example")
    print("Exported credentials to .env.example file")
    
    # Read back the .env file to verify
    with open(".env.example", "r") as f:
        env_content = f.read()
    print("\n.env file contents:")
    for line in env_content.splitlines():
        if "=" in line:
            name, value = line.split("=", 1)
            masked_value = value[:3] + "..." if len(value) > 3 else "***"
            print(f"{name}={masked_value}")
    
    # Clean up the example file
    os.remove(".env.example")


def remove_credentials(vault):
    """Remove credentials from the vault."""
    # Remove a credential
    vault.remove_credential("aws_secret_key")
    print("Removed aws_secret_key credential")
    
    # Verify it's gone
    try:
        vault.get_credential("aws_secret_key")
        print("Error: Credential was not removed!")
    except CredentialNotFoundError:
        print("Verified credential was removed")
    
    # List remaining credentials
    credential_names = vault.list_credentials()
    print(f"Remaining credentials: {', '.join(credential_names)}")


def backup_vault(vault):
    """Create a backup of the vault."""
    # Create a backup
    backup_path = vault.backup()
    print(f"Created vault backup at: {backup_path}")


def main():
    """Main function demonstrating basic LlamaVault usage."""
    print("=== LlamaVault Basic Usage Demo ===\n")
    
    # Create a new vault
    vault = create_vault()
    
    # Add credentials
    add_credentials(vault)
    
    # Get credentials
    get_credentials(vault)
    
    # List credentials
    list_credentials(vault)
    
    # Update credentials
    update_credentials(vault)
    
    # Export credentials
    export_credentials(vault)
    
    # Create backup
    backup_vault(vault)
    
    # Remove credentials
    remove_credentials(vault)
    
    print("\n=== Demo Complete ===")
    print("This demo created a real vault at ~/.llamavault with example credentials.")
    print("For security, please delete this vault after testing if you don't need it.")


if __name__ == "__main__":
    main() 