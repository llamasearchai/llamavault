"""
Exceptions for the llamavault module
"""

class VaultError(Exception):
    """Base exception for all vault-related errors"""
    pass

class CredentialNotFoundError(VaultError):
    """Raised when a requested credential is not found in the vault"""
    pass

class AuthenticationError(VaultError):
    """Raised when authentication to the vault fails"""
    pass

class EncryptionError(VaultError):
    """Raised when encryption or decryption operations fail"""
    pass

class ValidationError(VaultError):
    """Raised when credential validation fails"""
    pass

class ConfigurationError(VaultError):
    """Raised when there's an issue with the vault configuration"""
    pass

class BackupError(VaultError):
    """Raised when backup or restore operations fail"""
    pass

class ImportExportError(VaultError):
    """Raised when import or export operations fail"""
    pass

class PermissionError(VaultError):
    """Raised when there's an issue with file permissions"""
    pass 