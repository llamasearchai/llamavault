"""
LlamaVault - Secure Credential Management for AI/ML Applications

This module provides tools for securely storing and accessing API keys,
access tokens, and other sensitive credentials needed for AI/ML workflows.
"""

__version__ = "0.2.0"

from .vault import Vault
from .credential import Credential
from .exceptions import (
    VaultError,
    CredentialNotFoundError,
    AuthenticationError,
    EncryptionError,
)

__all__ = [
    "Vault",
    "Credential",
    "VaultError",
    "CredentialNotFoundError",
    "AuthenticationError",
    "EncryptionError",
] 