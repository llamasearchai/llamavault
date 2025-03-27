"""
LlamaVault Core Implementation
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import hashlib
import secrets
from cryptography.fernet import Fernet
import base64
import hmac
import datetime
from enum import Enum

# Security constants
KEY_ROTATION_INTERVAL = datetime.timedelta(days=30)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = datetime.timedelta(minutes=15)

class CredentialType(Enum):
    API_KEY = "api_key"
    TOKEN = "token"
    PASSWORD = "password"
    CERTIFICATE = "certificate"

class LlamaVault:
    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize the LlamaVault instance.
        
        Args:
            vault_path: Path to the vault storage directory
        """
        self.vault_path = Path(vault_path or "~/.llamavault").expanduser()
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize security components
        self._init_encryption()
        self._init_access_control()
        
        # Initialize AI components
        self._init_ai_engine()
        
        # Initialize audit logging
        self.audit_log = self.vault_path / "audit.log"
        
    def _init_encryption(self):
        """Initialize encryption components."""
        self.key_file = self.vault_path / "encryption.key"
        
        if not self.key_file.exists():
            # Generate new encryption key
            self.encryption_key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.encryption_key)
        else:
            # Load existing key
            with open(self.key_file, "rb") as f:
                self.encryption_key = f.read()
                
        self.cipher = Fernet(self.encryption_key)
        
    def _init_access_control(self):
        """Initialize access control system."""
        self.access_file = self.vault_path / "access.json"
        self.failed_attempts = {}
        
        if not self.access_file.exists():
            # Initialize empty access control
            with open(self.access_file, "w") as f:
                json.dump({}, f)
                
    def _init_ai_engine(self):
        """Initialize AI-powered components."""
        try:
            from llama_ai_config_engine import SmartConfigurationManager
            self.ai_engine = SmartConfigurationManager(str(self.vault_path))
        except ImportError:
            logging.warning("AI engine not available. Some features will be limited.")
            self.ai_engine = None
        
    def add_credential(self, name: str, value: str, credential_type: CredentialType, 
                      tags: Optional[List[str]] = None, metadata: Optional[Dict] = None):
        """
        Add a new credential to the vault.
        
        Args:
            name: Name/identifier for the credential
            value: The credential value
            credential_type: Type of credential
            tags: Optional tags for categorization
            metadata: Optional metadata dictionary
        """
        # Validate input
        if not name or not value:
            raise ValueError("Name and value must be provided")
            
        # Check if credential already exists
        if self._credential_exists(name):
            raise ValueError(f"Credential '{name}' already exists")
            
        # Encrypt the credential value
        encrypted_value = self._encrypt_value(value)
        
        # Create credential record
        credential = {
            "name": name,
            "value": encrypted_value,
            "type": credential_type.value,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat(),
            "version": 1
        }
        
        # Store credential
        self._store_credential(name, credential)
        
        # Log the addition
        self._log_audit("ADD", name)
        
    def get_credential(self, name: str) -> Dict:
        """
        Retrieve a credential from the vault.
        
        Args:
            name: Name of the credential to retrieve
            
        Returns:
            Dictionary containing the credential information
        """
        # Check access
        self._check_access(name)
        
        # Load credential
        credential = self._load_credential(name)
        if not credential:
            raise ValueError(f"Credential '{name}' not found")
            
        # Decrypt the value
        credential["value"] = self._decrypt_value(credential["value"])
        
        # Log the access
        self._log_audit("ACCESS", name)
        
        return credential
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a credential value."""
        return self.cipher.encrypt(value.encode()).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a credential value."""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
    
    def _store_credential(self, name: str, credential: Dict):
        """Store a credential in the vault."""
        credential_file = self.vault_path / f"{name}.json"
        with open(credential_file, "w") as f:
            json.dump(credential, f, indent=2)
            
    def _load_credential(self, name: str) -> Optional[Dict]:
        """Load a credential from the vault."""
        credential_file = self.vault_path / f"{name}.json"
        if not credential_file.exists():
            return None
            
        with open(credential_file, "r") as f:
            return json.load(f)
            
    def _credential_exists(self, name: str) -> bool:
        """Check if a credential exists."""
        return (self.vault_path / f"{name}.json").exists()
        
    def _check_access(self, name: str):
        """Check if access to a credential is allowed."""
        # Implement access control checks here
        pass
        
    def _log_audit(self, action: str, credential_name: str):
        """Log an audit event."""
        timestamp = datetime.datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "action": action,
            "credential": credential_name
        }
        
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def list_credentials(self, tag: Optional[str] = None, cred_type: Optional[str] = None) -> List[Dict]:
        """
        List credentials in the vault.
        
        Args:
            tag: Optional tag to filter by
            cred_type: Optional credential type to filter by
            
        Returns:
            List of credential dictionaries (without values)
        """
        credentials = []
        
        # Iterate over all JSON files in the vault directory
        for file_path in self.vault_path.glob("*.json"):
            # Skip non-credential files
            if file_path.name in ["access.json"]:
                continue
                
            # Load credential
            with open(file_path, "r") as f:
                try:
                    credential = json.load(f)
                    
                    # Apply filters
                    if tag and tag not in credential.get("tags", []):
                        continue
                    if cred_type and credential.get("type") != cred_type:
                        continue
                        
                    # Don't include the encrypted value in the listing
                    credential_copy = credential.copy()
                    credential_copy.pop("value", None)
                    
                    credentials.append(credential_copy)
                except json.JSONDecodeError:
                    logging.warning(f"Error decoding credential file: {file_path}")
        
        return credentials
    
    def remove_credential(self, name: str):
        """
        Remove a credential from the vault.
        
        Args:
            name: Name of the credential to remove
        """
        # Check if credential exists
        if not self._credential_exists(name):
            raise ValueError(f"Credential '{name}' not found")
            
        # Remove the credential file
        credential_file = self.vault_path / f"{name}.json"
        credential_file.unlink()
        
        # Log the removal
        self._log_audit("REMOVE", name)
    
    def rotate_credential(self, name: str, new_value: str):
        """
        Rotate a credential with a new value.
        
        Args:
            name: Name of the credential to rotate
            new_value: New value for the credential
        """
        # Load existing credential
        credential = self._load_credential(name)
        if not credential:
            raise ValueError(f"Credential '{name}' not found")
            
        # Update the credential
        credential["value"] = self._encrypt_value(new_value)
        credential["updated_at"] = datetime.datetime.utcnow().isoformat()
        credential["version"] += 1
        
        # Store updated credential
        self._store_credential(name, credential)
        
        # Log the rotation
        self._log_audit("ROTATE", name)
    
    def analyze_configuration(self, repo_path: str) -> Dict:
        """
        Analyze a repository's configuration using AI.
        
        Args:
            repo_path: Path to the repository to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.ai_engine:
            raise ImportError("AI engine not available. Install with: pip install llamavault[ai]")
            
        return self.ai_engine.analyze_repository(repo_path)
        
    def generate_configuration(self, repo_path: str, format: str = "env") -> str:
        """
        Generate optimal configuration for a repository.
        
        Args:
            repo_path: Path to the repository
            format: Output format (env, yaml, json, toml)
            
        Returns:
            Generated configuration content
        """
        if not self.ai_engine:
            raise ImportError("AI engine not available. Install with: pip install llamavault[ai]")
            
        return self.ai_engine.generate_configuration_file(format)
        
    def resolve_dependencies(self, repos_dir: str) -> Dict:
        """
        Resolve dependency conflicts across repositories.
        
        Args:
            repos_dir: Directory containing multiple repositories
            
        Returns:
            Dictionary containing resolution results
        """
        if not self.ai_engine:
            raise ImportError("AI engine not available. Install with: pip install llamavault[ai]")
            
        try:
            # Try to import dependency checker
            from dependency_checker import analyze_repositories, find_conflicts
            
            # Use the dependency checker
            repo_paths = [Path(repos_dir) / d for d in os.listdir(repos_dir) 
                        if os.path.isdir(os.path.join(repos_dir, d)) and 
                        os.path.exists(os.path.join(repos_dir, d, ".git"))]
                        
            repo_dependencies = analyze_repositories(repo_paths)
            conflicts = find_conflicts(repo_dependencies)
            
            return {
                "repositories": [p.name for p in repo_paths],
                "conflicts": conflicts
            }
        except ImportError:
            # Fall back to AI engine if available
            return self.ai_engine.resolve_dependencies(repos_dir) 