#!/usr/bin/env python3
"""
Basic usage example for LlamaVault
"""

import os
import sys
import getpass
from pathlib import Path

from llamavault import Vault, CredentialNotFoundError, AuthenticationError


def main():
    """
    Demonstrate basic LlamaVault functionality
    """
    # Set vault location (defaults to ~/.llamavault if not specified)
    vault_dir = Path.home() / ".demo-vault"
    
    # Get password securely
    password = getpass.getpass("Enter vault password: ")
    
    try:
        # Initialize the vault (creates if it doesn't exist)
        print(f"Initializing vault at: {vault_dir}")
        vault = Vault(vault_dir=vault_dir, password=password)
        
        # If vault doesn't exist yet, initialize it
        if not os.path.exists(vault_dir / "vault.json"):
            vault.init()
            print("Created new vault.")
        
        # Add a credential
        api_key = "sk-1234567890abcdef1234567890abcdef1234567890"
        vault.add_credential(
            "openai_api_key", 
            api_key,
            metadata={
                "service": "OpenAI",
                "environment": "development",
                "description": "API key for GPT-4 access"
            }
        )
        print("Added OpenAI API key.")
        
        # Add another credential
        db_password = "P@ssw0rd!123"
        vault.add_credential(
            "database_password",
            db_password,
            metadata={
                "service": "PostgreSQL",
                "host": "localhost:5432",
                "username": "admin"
            }
        )
        print("Added database password.")
        
        # List all credentials
        print("\nStored credentials:")
        credentials = vault.get_all_credentials()
        for name, cred in credentials.items():
            created = cred.created_at.strftime("%Y-%m-%d %H:%M") if cred.created_at else "N/A"
            print(f" - {name} (created: {created})")
            if cred.metadata:
                for key, value in cred.metadata.items():
                    print(f"   • {key}: {value}")
        
        # Retrieve a credential
        retrieved_key = vault.get_credential("openai_api_key")
        print(f"\nRetrieved API key: {retrieved_key[:5]}...{retrieved_key[-5:]}")
        
        # Update a credential with new metadata
        vault.update_credential(
            "openai_api_key",
            api_key,
            metadata={
                "service": "OpenAI",
                "environment": "production",  # Changed from development
                "description": "API key for GPT-4 access",
                "added": "Additional metadata field"
            }
        )
        print("Updated API key metadata.")
        
        # Export credentials as environment variables
        env_file = vault_dir / ".env"
        vault.export_env_file(env_file)
        print(f"\nExported credentials to: {env_file}")
        
        # Create a backup
        backup_path = vault.backup()
        print(f"Created backup at: {backup_path}")
        
        # Remove a credential
        vault.remove_credential("database_password")
        print("Removed database password.")
        
        # Verify it's gone
        try:
            vault.get_credential("database_password")
            print("Error: Credential still exists!")
        except CredentialNotFoundError:
            print("Verified credential was removed.")
        
        print("\nExample completed successfully!")
    
    except AuthenticationError:
        print("Authentication error: Incorrect password")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 