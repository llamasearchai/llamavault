API Reference
============

This section provides detailed API documentation for all components of LlamaVault. Use this reference to understand the available classes, methods, and functions for programmatic access to the credential management system.

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   vault
   credential
   exceptions

Core Components
--------------

* :doc:`vault` - The primary class for working with credential vaults
* :doc:`credential` - The class representing individual credentials with metadata
* :doc:`exceptions` - Error types for handling various failure conditions

Quick Links
----------

* :py:class:`llamavault.Vault` - Main vault interface
* :py:class:`llamavault.Credential` - Credential container
* :py:exception:`llamavault.VaultError` - Base exception type

API Usage Examples
---------------

Basic Usage
^^^^^^^^^^

.. code-block:: python

    from llamavault import Vault
    
    # Create a vault
    vault = Vault(password="secure-password")
    vault.init()
    
    # Add a credential
    vault.add_credential("api_key", "my-secret-key", 
                        metadata={"service": "example"})
    
    # Retrieve a credential
    api_key = vault.get_credential("api_key")
    
    # List all credentials
    all_creds = vault.list_credentials()

Working with Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Export credentials to environment variables
    env_vars = vault.export_env()
    
    # Export to .env file
    vault.export_env_file(".env")
    
    # Use with python-dotenv
    import os
    from dotenv import load_dotenv
    
    vault.export_env_file(".env")
    load_dotenv()
    
    api_key = os.getenv("API_KEY")

Advanced Error Handling
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from llamavault import (
        Vault, 
        VaultError, 
        AuthenticationError,
        CredentialNotFoundError
    )
    
    try:
        vault = Vault(password="my-password")
        value = vault.get_credential("important_credential")
    except AuthenticationError:
        # Handle bad password
        print("Authentication failed")
    except CredentialNotFoundError:
        # Handle missing credential
        print("Credential not found")
    except VaultError as e:
        # Handle any other vault error
        print(f"Vault error: {e}")

Integration Patterns
-----------------

The API is designed to be flexible for different integration patterns:

* **Direct use**: Import and use the `Vault` class directly
* **Factory pattern**: Create a vault factory to manage multiple vault instances
* **Dependency injection**: Pass vault instances to services that need credentials
* **Context managers**: Use Python context managers for automatic vault handling

.. code-block:: python

    # Context manager example
    class VaultContext:
        def __init__(self, password=None, vault_dir=None):
            self.password = password
            self.vault_dir = vault_dir
            self.vault = None
            
        def __enter__(self):
            self.vault = Vault(password=self.password, vault_dir=self.vault_dir)
            return self.vault
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Cleanup if needed
            pass
            
    # Usage
    with VaultContext(password="secure-pass") as vault:
        api_key = vault.get_credential("api_key") 