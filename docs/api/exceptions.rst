Exceptions API
=============

LlamaVault provides a range of exception classes for handling various error conditions.

Base Exception
------------

.. py:exception:: llamavault.VaultError

   Base exception for all vault-related errors.

Authentication Errors
------------------

.. py:exception:: llamavault.AuthenticationError

   Raised when there is an authentication failure, such as an incorrect password.

Credential Errors
--------------

.. py:exception:: llamavault.CredentialNotFoundError

   Raised when attempting to access a credential that doesn't exist.

.. py:exception:: llamavault.ValidationError

   Raised when a credential fails validation (e.g., empty name or value).

Encryption Errors
--------------

.. py:exception:: llamavault.EncryptionError

   Raised when encryption or decryption operations fail.

Configuration Errors
-----------------

.. py:exception:: llamavault.ConfigurationError

   Raised when there is an issue with the vault configuration.

Backup and Export Errors
---------------------

.. py:exception:: llamavault.BackupError

   Raised when creating a vault backup fails.

.. py:exception:: llamavault.ImportExportError

   Raised when importing or exporting credentials fails.

Permission Errors
--------------

.. py:exception:: llamavault.PermissionError

   Raised when there is insufficient permission to perform an operation.

Exception Hierarchy
-----------------

All exceptions inherit from the base ``VaultError`` class:

.. code-block:: text

    VaultError
    ├── AuthenticationError
    ├── CredentialNotFoundError
    ├── ValidationError
    ├── EncryptionError
    ├── ConfigurationError
    ├── BackupError
    ├── ImportExportError
    └── PermissionError

Handling Exceptions
-----------------

Example of handling LlamaVault exceptions:

.. code-block:: python

    from llamavault import Vault
    from llamavault import (
        VaultError,
        AuthenticationError,
        CredentialNotFoundError,
        ValidationError
    )
    
    try:
        # Try to open a vault
        vault = Vault(password="incorrect-password")
    except AuthenticationError:
        print("Wrong password!")
    except ConfigurationError:
        print("Vault is not properly configured.")
    except VaultError as e:
        print(f"General vault error: {e}")
    
    try:
        # Try to get a credential
        vault.get_credential("nonexistent_credential")
    except CredentialNotFoundError:
        print("Credential doesn't exist!")
    
    try:
        # Try to add an invalid credential
        vault.add_credential("", "secret")
    except ValidationError:
        print("Invalid credential name or value!")

Web Interface Exceptions
---------------------

When using the web interface, errors are typically displayed to the user in a friendly format. The same exceptions are used internally but are translated into appropriate HTTP status codes and error messages.

CLI Exceptions
-----------

When using the command-line interface, exceptions are caught and displayed with helpful error messages. Error codes are also returned to the calling process:

.. code-block:: bash

    $ llamavault get nonexistent_credential
    Error: Credential 'nonexistent_credential' not found.
    # Returns exit code 1

Testing for Specific Exceptions
----------------------------

Use standard Python techniques for testing specific exceptions:

.. code-block:: python

    import pytest
    from llamavault import Vault, CredentialNotFoundError
    
    def test_credential_not_found():
        vault = Vault(password="test-password")
        vault.init(force=True)
        
        with pytest.raises(CredentialNotFoundError):
            vault.get_credential("nonexistent") 