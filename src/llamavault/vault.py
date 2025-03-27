"""
Core Vault implementation for credential management
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import tempfile
import shutil

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .credential import Credential
from .exceptions import VaultError, CredentialNotFoundError, AuthenticationError, EncryptionError

logger = logging.getLogger(__name__)

class Vault:
    """
    Secure storage for credentials with encryption
    
    Provides methods for storing, retrieving, and managing credentials
    like API keys, access tokens, and other sensitive information.
    
    Examples:
        >>> vault = Vault()
        >>> vault.add_credential("openai", "sk-abcdef123456")
        >>> openai_key = vault.get_credential("openai")
        >>> vault.list_credentials()
        ['openai']
    """
    
    DEFAULT_VAULT_DIR = Path.home() / ".llamavault"
    VAULT_FILE_NAME = "vault.enc"
    CONFIG_FILE_NAME = "config.json"
    
    def __init__(
        self, 
        vault_dir: Optional[Union[str, Path]] = None,
        password: Optional[str] = None,
        auto_save: bool = True
    ) -> None:
        """
        Initialize a Vault instance
        
        Args:
            vault_dir: Directory to store the vault file (default: ~/.llamavault)
            password: Password for encrypting/decrypting the vault
                      If not provided, will use environment variable or prompt
            auto_save: Whether to automatically save changes to disk
        
        Raises:
            AuthenticationError: If the provided password is incorrect
            VaultError: If there's an issue initializing the vault
        """
        self.vault_dir = Path(vault_dir) if vault_dir else self.DEFAULT_VAULT_DIR
        self.vault_path = self.vault_dir / self.VAULT_FILE_NAME
        self.config_path = self.vault_dir / self.CONFIG_FILE_NAME
        self.auto_save = auto_save
        
        # Ensure vault directory exists
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        
        # Get or prompt for password
        self._password = password or os.environ.get("LLAMAVAULT_PASSWORD")
        if not self._password and self.vault_path.exists():
            raise AuthenticationError("Password required for existing vault")
            
        # Initialize or load credentials
        self._credentials: Dict[str, Credential] = {}
        self._config: Dict[str, Any] = self._load_config()
        
        # Load existing vault if it exists
        if self.vault_path.exists():
            try:
                self._load_vault()
            except Exception as e:
                raise AuthenticationError(f"Failed to decrypt vault: {e}")
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation, generated if not provided
            
        Returns:
            Tuple of (key, salt)
        """
        if not salt:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from disk or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")
                
        # Default configuration
        return {
            "created_at": datetime.now().isoformat(),
            "version": 1,
            "salt": base64.b64encode(os.urandom(16)).decode(),
            "settings": {
                "log_access": True,
                "auto_backup": True,
                "backup_count": 5
            }
        }
    
    def _save_config(self) -> None:
        """Save configuration to disk"""
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2)
    
    def _load_vault(self) -> None:
        """Load and decrypt vault from disk"""
        if not self.vault_path.exists():
            return
            
        try:
            # Read the encrypted data
            with open(self.vault_path, "rb") as f:
                encrypted_data = f.read()
            
            # Get salt from config
            salt = base64.b64decode(self._config["salt"])
            
            # Derive key
            key, _ = self._derive_key(self._password, salt)
            
            # Decrypt
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Parse credentials
            credentials_data = json.loads(decrypted_data)
            self._credentials = {
                k: Credential.from_dict(v) for k, v in credentials_data.items()
            }
            
        except Exception as e:
            logger.error(f"Failed to load vault: {e}")
            raise EncryptionError(f"Could not decrypt vault: {e}")
    
    def _save_vault(self) -> None:
        """Encrypt and save vault to disk"""
        try:
            # Convert credentials to serializable format
            credentials_data = {
                k: v.to_dict() for k, v in self._credentials.items()
            }
            
            # Serialize
            data = json.dumps(credentials_data).encode()
            
            # Get salt from config
            salt = base64.b64decode(self._config["salt"])
            
            # Derive key
            key, _ = self._derive_key(self._password, salt)
            
            # Encrypt
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data)
            
            # Save encrypted data securely (atomic write)
            with tempfile.NamedTemporaryFile(
                dir=self.vault_dir, delete=False
            ) as tmp:
                tmp.write(encrypted_data)
                tmp_path = tmp.name
                
            shutil.move(tmp_path, self.vault_path)
            
        except Exception as e:
            logger.error(f"Failed to save vault: {e}")
            raise EncryptionError(f"Could not encrypt vault: {e}")
    
    def add_credential(
        self, 
        name: str, 
        value: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a credential to the vault
        
        Args:
            name: Name of the credential (e.g., "openai", "github")
            value: Value of the credential (e.g., API key or token)
            metadata: Optional metadata about the credential
            
        Returns:
            None
        """
        metadata = metadata or {}
        credential = Credential(
            name=name,
            value=value,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata
        )
        
        self._credentials[name] = credential
        
        if self.auto_save:
            self._save_vault()
    
    def get_credential(self, name: str) -> str:
        """
        Retrieve a credential by name
        
        Args:
            name: Name of the credential to retrieve
            
        Returns:
            The credential value as a string
            
        Raises:
            CredentialNotFoundError: If the credential doesn't exist
        """
        if name not in self._credentials:
            raise CredentialNotFoundError(f"Credential '{name}' not found")
            
        credential = self._credentials[name]
        
        # Update last accessed time
        if self._config["settings"]["log_access"]:
            credential.last_accessed = datetime.now()
            if self.auto_save:
                self._save_vault()
                
        return credential.value
    
    def remove_credential(self, name: str) -> None:
        """
        Remove a credential from the vault
        
        Args:
            name: Name of the credential to remove
            
        Raises:
            CredentialNotFoundError: If the credential doesn't exist
        """
        if name not in self._credentials:
            raise CredentialNotFoundError(f"Credential '{name}' not found")
            
        del self._credentials[name]
        
        if self.auto_save:
            self._save_vault()
    
    def list_credentials(self) -> List[str]:
        """
        List all credential names in the vault
        
        Returns:
            List of credential names
        """
        return list(self._credentials.keys())
    
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get metadata for a credential
        
        Args:
            name: Name of the credential
            
        Returns:
            Dictionary of metadata
            
        Raises:
            CredentialNotFoundError: If the credential doesn't exist
        """
        if name not in self._credentials:
            raise CredentialNotFoundError(f"Credential '{name}' not found")
            
        return self._credentials[name].metadata.copy()
    
    def set_metadata(self, name: str, metadata: Dict[str, Any]) -> None:
        """
        Set metadata for a credential
        
        Args:
            name: Name of the credential
            metadata: Metadata to set
            
        Raises:
            CredentialNotFoundError: If the credential doesn't exist
        """
        if name not in self._credentials:
            raise CredentialNotFoundError(f"Credential '{name}' not found")
            
        self._credentials[name].metadata = metadata.copy()
        self._credentials[name].updated_at = datetime.now()
        
        if self.auto_save:
            self._save_vault()
    
    def get_all_credentials(self) -> Dict[str, Credential]:
        """
        Get all credentials with their metadata
        
        Returns:
            Dictionary of credential objects
        """
        return self._credentials.copy()
    
    def save(self) -> None:
        """
        Explicitly save the vault to disk
        
        Use this when auto_save is disabled
        """
        self._save_vault()
        self._save_config()
    
    def export_env(self, uppercase: bool = True) -> Dict[str, str]:
        """
        Export credentials as environment variable format
        
        Args:
            uppercase: Whether to convert keys to uppercase
            
        Returns:
            Dictionary of credential name to value, formatted for env vars
        """
        env_vars = {}
        
        for name, credential in self._credentials.items():
            key = name.upper() if uppercase else name
            # Convert hyphens to underscores for env var compatibility
            key = key.replace("-", "_")
            env_vars[key] = credential.value
            
        return env_vars
    
    def export_env_file(self, path: Union[str, Path], uppercase: bool = True) -> None:
        """
        Export credentials to a .env file
        
        Args:
            path: Path to the .env file
            uppercase: Whether to convert keys to uppercase
        """
        env_vars = self.export_env(uppercase=uppercase)
        
        with open(path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
    
    def backup(self, backup_dir: Optional[Union[str, Path]] = None) -> Path:
        """
        Create a backup of the vault
        
        Args:
            backup_dir: Directory to store backup, defaults to vault_dir/backups
            
        Returns:
            Path to the backup file
        """
        backup_dir = Path(backup_dir) if backup_dir else self.vault_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"vault_{timestamp}.enc"
        
        shutil.copy2(self.vault_path, backup_path)
        
        # Remove old backups if needed
        self._cleanup_backups(backup_dir)
        
        return backup_path
    
    def _cleanup_backups(self, backup_dir: Path) -> None:
        """Remove old backups based on configuration"""
        if not self._config["settings"]["auto_backup"]:
            return
            
        max_backups = self._config["settings"]["backup_count"]
        if max_backups <= 0:
            return
            
        backups = sorted(backup_dir.glob("vault_*.enc"))
        while len(backups) > max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
    
    def change_password(self, new_password: str) -> None:
        """
        Change the encryption password for the vault
        
        Args:
            new_password: New password to use
        """
        # Store old password and set new one
        old_password = self._password
        self._password = new_password
        
        # Generate new salt
        new_salt = os.urandom(16)
        self._config["salt"] = base64.b64encode(new_salt).decode()
        
        # Save with new password
        try:
            self._save_vault()
            self._save_config()
        except Exception as e:
            # Revert to old password on failure
            self._password = old_password
            raise EncryptionError(f"Failed to change password: {e}")
    
    def init(self, force: bool = False) -> None:
        """
        Initialize a new vault
        
        Args:
            force: Whether to overwrite an existing vault
        
        Raises:
            VaultError: If the vault already exists and force is False
        """
        if self.vault_path.exists() and not force:
            raise VaultError("Vault already exists. Use force=True to overwrite")
            
        # Create fresh config
        self._config = {
            "created_at": datetime.now().isoformat(),
            "version": 1,
            "salt": base64.b64encode(os.urandom(16)).decode(),
            "settings": {
                "log_access": True,
                "auto_backup": True,
                "backup_count": 5
            }
        }
        
        # Clear credentials
        self._credentials = {}
        
        # Save empty vault
        self._save_config()
        self._save_vault()
        
        logger.info(f"Initialized new vault at {self.vault_path}") 