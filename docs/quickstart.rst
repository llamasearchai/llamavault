Quickstart
==========

This guide will help you get started with LlamaVault quickly. It covers initializing a vault, adding credentials, and using them in your applications.

Creating Your First Vault
------------------------

Before you can store credentials, you need to initialize a vault:

.. code-block:: bash

    # Initialize a new vault (by default at ~/.llamavault)
    llamavault init

You'll be prompted to create a password for the vault. Choose a strong password and make sure to remember it, as it cannot be recovered.

.. note:: 
    You can specify a custom location with the ``--vault-dir`` option:
    
    ``llamavault --vault-dir /path/to/vault init``

Adding Credentials
-----------------

To add a credential to the vault:

.. code-block:: bash

    # Add an OpenAI API key
    llamavault add openai_api_key

You'll be prompted to enter the value for the credential. You can also add metadata to help organize and categorize your credentials.

Retrieving Credentials
--------------------

To retrieve a credential:

.. code-block:: bash

    llamavault get openai_api_key

Listing All Credentials
---------------------

To see all stored credentials:

.. code-block:: bash

    llamavault list

This will display a table with all your credentials, including creation dates and metadata.

Exporting as Environment Variables
--------------------------------

A common use case is to export credentials as environment variables for use in applications:

.. code-block:: bash

    # Export to a .env file
    llamavault export .env

    # Then in your shell:
    source .env

    # Or with Python's python-dotenv:
    from dotenv import load_dotenv
    load_dotenv()

Python API Example
----------------

Here's how to use LlamaVault directly in your Python code:

.. code-block:: python

    from llamavault import Vault
    import getpass

    # Create or open a vault
    password = getpass.getpass("Vault password: ")
    vault = Vault(password=password)

    # Add a credential
    vault.add_credential(
        "openai_api_key", 
        "sk-example123456789", 
        metadata={
            "service": "OpenAI", 
            "environment": "development"
        }
    )

    # Use the credential
    import openai
    openai.api_key = vault.get_credential("openai_api_key")

    # Update with new metadata
    vault.update_credential(
        "openai_api_key",
        "sk-example123456789",
        metadata={"service": "OpenAI", "environment": "production"}
    )

    # List all credentials
    credentials = vault.get_all_credentials()
    for name, cred in credentials.items():
        print(f"{name}: {cred.value}")

    # Remove a credential
    vault.remove_credential("openai_api_key")

Web Interface
-----------

If you installed LlamaVault with web support, you can start the web interface:

.. code-block:: bash

    # Start the web interface on localhost:5000
    llamavault web

Then open a browser and navigate to http://localhost:5000.

Next Steps
---------

Now that you've learned the basics, you can:

- Read the detailed :doc:`cli_usage` documentation
- Explore the :doc:`web_interface` features
- Check out the :doc:`api/vault` for advanced usage
- Learn about the :doc:`security` measures in place 