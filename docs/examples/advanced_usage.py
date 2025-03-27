#!/usr/bin/env python3
"""
Advanced usage examples for LlamaVault.

This example demonstrates more complex usage patterns:
- Working with multiple vaults
- Custom metadata processing
- Automatic credential rotation
- Using context managers
- Integration with libraries that need API keys
"""

import os
import time
import getpass
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from llamavault import Vault, Credential, CredentialNotFoundError


class VaultManager:
    """Manager for working with multiple vaults."""
    
    def __init__(self):
        self.vaults = {}
        self.base_dir = Path.home() / ".llamavaults"
        self.base_dir.mkdir(exist_ok=True)
        
    def get_vault(self, name: str, password: Optional[str] = None) -> Vault:
        """Get a vault by name, creating or opening as needed."""
        if name in self.vaults:
            return self.vaults[name]
            
        vault_dir = self.base_dir / name
        
        if password is None:
            password = getpass.getpass(f"Password for vault '{name}': ")
            
        vault = Vault(vault_dir=vault_dir, password=password)
        
        # Initialize if it doesn't exist
        if not (vault_dir / "config.json").exists():
            vault.init()
            print(f"Initialized new vault: {name}")
            
        self.vaults[name] = vault
        return vault
        
    def close_all(self):
        """Close all open vaults."""
        self.vaults.clear()
        
    def list_vaults(self) -> List[str]:
        """List all available vaults."""
        return [d.name for d in self.base_dir.iterdir() 
                if d.is_dir() and (d / "config.json").exists()]


class CredentialRotator:
    """Helper for automatic credential rotation."""
    
    def __init__(self, vault: Vault):
        self.vault = vault
        
    def rotate_if_needed(self, name: str, max_age_days: int = 90) -> bool:
        """
        Check if a credential needs rotation and call the appropriate handler.
        
        Returns True if credential was rotated.
        """
        try:
            cred = self.vault.get_credential_object(name)
        except CredentialNotFoundError:
            return False
            
        # Check if rotation is needed
        if not self._needs_rotation(cred, max_age_days):
            return False
            
        # Get rotation handler based on metadata
        handler = self._get_rotation_handler(cred)
        if not handler:
            print(f"No rotation handler for credential: {name}")
            return False
            
        # Perform rotation
        print(f"Rotating credential: {name}")
        new_value = handler(cred)
        if new_value:
            # Update credential with new value
            metadata = cred.metadata.copy() if cred.metadata else {}
            metadata["last_rotated"] = datetime.now().isoformat()
            metadata["previous_rotation"] = cred.updated_at.isoformat() if cred.updated_at else None
            
            self.vault.update_credential(name, new_value, metadata)
            return True
            
        return False
        
    def _needs_rotation(self, cred: Credential, max_age_days: int) -> bool:
        """Check if a credential needs rotation based on age or metadata."""
        # Check for explicit expiry in metadata
        if cred.metadata and "expiry" in cred.metadata:
            try:
                expiry = datetime.fromisoformat(cred.metadata["expiry"])
                if datetime.now() >= expiry:
                    return True
            except (ValueError, TypeError):
                pass
                
        # Check based on age
        if cred.updated_at:
            age = datetime.now() - cred.updated_at
            if age.days >= max_age_days:
                return True
                
        return False
        
    def _get_rotation_handler(self, cred: Credential):
        """Get the appropriate rotation handler for a credential type."""
        handlers = {
            "api_key": self._rotate_api_key,
            "database": self._rotate_database_password,
            "token": self._rotate_token,
        }
        
        # Determine credential type from metadata or name
        cred_type = None
        if cred.metadata and "type" in cred.metadata:
            cred_type = cred.metadata["type"]
        else:
            # Try to infer from name
            for key in handlers:
                if key in cred.name:
                    cred_type = key
                    break
                    
        return handlers.get(cred_type)
        
    def _rotate_api_key(self, cred: Credential) -> Optional[str]:
        """Example handler for API key rotation."""
        # In a real application, this would call the service's API to rotate the key
        print(f"Would rotate API key for {cred.name}")
        # Return a mock new key for demonstration
        return f"new-api-key-{int(time.time())}"
        
    def _rotate_database_password(self, cred: Credential) -> Optional[str]:
        """Example handler for database password rotation."""
        # In a real application, this would update the database password
        print(f"Would rotate database password for {cred.name}")
        return f"new-db-password-{int(time.time())}"
        
    def _rotate_token(self, cred: Credential) -> Optional[str]:
        """Example handler for token rotation."""
        # In a real application, this would refresh the token
        print(f"Would refresh token for {cred.name}")
        return f"new-token-{int(time.time())}"


class VaultContext:
    """Context manager for vault access."""
    
    def __init__(self, 
                 vault_dir: Optional[str] = None, 
                 password: Optional[str] = None,
                 vault: Optional[Vault] = None):
        self.vault_dir = vault_dir
        self.password = password
        self.external_vault = vault
        self.vault = None
        
    def __enter__(self) -> Vault:
        if self.external_vault:
            self.vault = self.external_vault
        else:
            self.vault = Vault(vault_dir=self.vault_dir, password=self.password)
        return self.vault
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Any cleanup if needed
        pass


class EnvVarManager:
    """Helper for managing environment variables from credentials."""
    
    def __init__(self, vault: Vault):
        self.vault = vault
        self.original_env = {}
        
    def set_env_vars(self, credentials: List[str] = None, prefix: str = "", 
                   uppercase: bool = True) -> Dict[str, str]:
        """
        Set environment variables for specified credentials.
        If credentials is None, all credentials are used.
        Returns a dict of the set variables.
        """
        set_vars = {}
        
        if credentials is None:
            # Use all credentials
            credentials = self.vault.list_credentials()
            
        for name in credentials:
            try:
                value = self.vault.get_credential(name)
                env_name = self._format_env_name(name, prefix, uppercase)
                
                # Store original value if it exists
                if env_name in os.environ:
                    self.original_env[env_name] = os.environ[env_name]
                    
                # Set new value
                os.environ[env_name] = value
                set_vars[env_name] = value
            except CredentialNotFoundError:
                print(f"Credential not found: {name}")
                
        return set_vars
        
    def clear_env_vars(self, env_vars: Dict[str, str] = None):
        """
        Clear environment variables, restoring original values.
        If env_vars is None, clear all variables that were set.
        """
        if env_vars is None:
            # Clear all variables that were set and restore originals
            for name in list(self.original_env.keys()):
                if name in self.original_env:
                    os.environ[name] = self.original_env[name]
                    del self.original_env[name]
                else:
                    del os.environ[name]
        else:
            # Clear only specified variables
            for name in env_vars:
                if name in self.original_env:
                    os.environ[name] = self.original_env[name]
                    del self.original_env[name]
                else:
                    del os.environ[name]
                    
    def _format_env_name(self, name: str, prefix: str = "", uppercase: bool = True) -> str:
        """Format a credential name as an environment variable name."""
        result = name.replace("-", "_").replace(" ", "_")
        if prefix:
            result = f"{prefix}_{result}"
        if uppercase:
            result = result.upper()
        return result


class CredentialImporter:
    """Helper for importing credentials from various sources."""
    
    def __init__(self, vault: Vault):
        self.vault = vault
        
    def import_from_env(self, var_names: List[str], prefix: str = "", 
                       lowercase: bool = True) -> int:
        """
        Import credentials from environment variables.
        Returns the number of credentials imported.
        """
        count = 0
        for var_name in var_names:
            if var_name in os.environ:
                name = var_name
                if prefix and name.startswith(prefix):
                    name = name[len(prefix):]
                if lowercase:
                    name = name.lower()
                
                try:
                    self.vault.add_credential(
                        name, 
                        os.environ[var_name],
                        metadata={
                            "source": "environment",
                            "original_name": var_name,
                            "imported_at": datetime.now().isoformat()
                        }
                    )
                    count += 1
                except Exception as e:
                    print(f"Error importing {var_name}: {e}")
                    
        return count
        
    def import_from_dotenv(self, file_path: str, prefix: str = "",
                          lowercase: bool = True) -> int:
        """
        Import credentials from a .env file.
        Returns the number of credentials imported.
        """
        count = 0
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    if '=' in line:
                        var_name, value = line.split('=', 1)
                        var_name = var_name.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value and value[0] in ('"', "'") and value[-1] == value[0]:
                            value = value[1:-1]
                            
                        name = var_name
                        if prefix and name.startswith(prefix):
                            name = name[len(prefix):]
                        if lowercase:
                            name = name.lower()
                            
                        try:
                            self.vault.add_credential(
                                name, 
                                value,
                                metadata={
                                    "source": "dotenv",
                                    "file": file_path,
                                    "original_name": var_name,
                                    "imported_at": datetime.now().isoformat()
                                }
                            )
                            count += 1
                        except Exception as e:
                            print(f"Error importing {var_name}: {e}")
        except Exception as e:
            print(f"Error reading .env file: {e}")
            
        return count
        
    def import_from_json(self, file_path: str, key_path: str = None) -> int:
        """
        Import credentials from a JSON file.
        If key_path is provided, it should be a dot-separated path to the credentials object.
        Returns the number of credentials imported.
        """
        count = 0
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Navigate to nested location if key_path is provided
            if key_path:
                parts = key_path.split('.')
                for part in parts:
                    if part in data:
                        data = data[part]
                    else:
                        print(f"Key path {key_path} not found in JSON")
                        return 0
                        
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (str, int, float, bool)):
                        try:
                            self.vault.add_credential(
                                key, 
                                str(value),
                                metadata={
                                    "source": "json",
                                    "file": file_path,
                                    "key_path": key_path,
                                    "imported_at": datetime.now().isoformat()
                                }
                            )
                            count += 1
                        except Exception as e:
                            print(f"Error importing {key}: {e}")
            else:
                print(f"Expected dict in JSON, got {type(data)}")
                
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            
        return count


def demo():
    """Demonstrate the advanced usage examples."""
    # Create a vault manager
    manager = VaultManager()
    
    # Get different vaults for different environments
    dev_vault = manager.get_vault("development", "dev-password")
    prod_vault = manager.get_vault("production", "prod-password")
    
    # Add some example credentials
    dev_vault.add_credential(
        "openai_api_key", 
        "sk-dev12345",
        metadata={
            "type": "api_key",
            "service": "OpenAI",
            "environment": "development",
            "expiry": (datetime.now() + timedelta(days=30)).isoformat()
        }
    )
    
    prod_vault.add_credential(
        "openai_api_key", 
        "sk-prod67890",
        metadata={
            "type": "api_key",
            "service": "OpenAI",
            "environment": "production",
            "expiry": (datetime.now() + timedelta(days=90)).isoformat()
        }
    )
    
    # Use context manager
    with VaultContext(vault=dev_vault) as vault:
        # Create environment variable manager
        env_manager = EnvVarManager(vault)
        
        # Set environment variables
        env_vars = env_manager.set_env_vars(["openai_api_key"], prefix="")
        
        # Use the credentials (simulated)
        print(f"Using OpenAI API with key: {os.environ.get('OPENAI_API_KEY')}")
        
        # Cleanup
        env_manager.clear_env_vars(env_vars)
    
    # Check for credential rotation
    rotator = CredentialRotator(dev_vault)
    
    # Force rotation for demo purposes by setting an expiry in the past
    cred = dev_vault.get_credential_object("openai_api_key")
    metadata = cred.metadata.copy()
    metadata["expiry"] = (datetime.now() - timedelta(days=1)).isoformat()
    dev_vault.update_credential("openai_api_key", cred.value, metadata)
    
    # Perform rotation check
    rotated = rotator.rotate_if_needed("openai_api_key")
    if rotated:
        print(f"Rotated credential. New value: {dev_vault.get_credential('openai_api_key')}")
    
    # Import credentials example (create a temporary .env file for demo)
    with open(".env.example", "w") as f:
        f.write("DATABASE_URL=postgresql://user:pass@localhost/db\n")
        f.write("AWS_ACCESS_KEY=AKIAEXAMPLE123456\n")
    
    importer = CredentialImporter(dev_vault)
    count = importer.import_from_dotenv(".env.example")
    print(f"Imported {count} credentials from .env file")
    
    # Clean up
    os.remove(".env.example")
    
    # List all vaults and their credentials
    print("\nAvailable vaults:")
    for vault_name in manager.list_vaults():
        vault = manager.get_vault(vault_name, "dev-password" if vault_name == "development" else "prod-password")
        credentials = vault.list_credentials()
        print(f"Vault: {vault_name}, Credentials: {', '.join(credentials)}")
    
    # Close all vaults
    manager.close_all()


if __name__ == "__main__":
    demo() 