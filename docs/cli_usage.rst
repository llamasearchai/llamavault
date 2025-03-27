Command Line Interface
====================

LlamaVault provides a powerful command-line interface (CLI) that allows you to manage your credentials easily from the terminal.

Global Options
-------------

The following options are available for all commands:

.. code-block:: text

    --debug                 Enable debug logging
    --vault-dir PATH        Custom vault directory (default: ~/.llamavault)
    --version               Show version and exit
    -h, --help              Show help message and exit

Basic Commands
-------------

Initialize a Vault
^^^^^^^^^^^^^^^^^

Before you can use LlamaVault, you need to initialize a vault:

.. code-block:: bash

    llamavault init [--force]

Options:

- ``--force``: Overwrite an existing vault (use with caution)

You'll be prompted to create a password for the vault. This password is used to encrypt your credentials.

Add a Credential
^^^^^^^^^^^^^^

To add a new credential to the vault:

.. code-block:: bash

    llamavault add NAME

You'll be prompted for the credential value and optional metadata. Metadata is stored as key-value pairs and can include information like:

- Service name
- Environment (production, development)
- Description
- Expiry date

Get a Credential
^^^^^^^^^^^^^

To retrieve a credential:

.. code-block:: bash

    llamavault get NAME

This will display the value of the credential.

List Credentials
^^^^^^^^^^^^^^

To see all credentials stored in the vault:

.. code-block:: bash

    llamavault list

This displays a table with the following information:

- Name
- Creation date
- Last update date
- Last access date
- Metadata (if any)

Remove a Credential
^^^^^^^^^^^^^^^^^

To remove a credential from the vault:

.. code-block:: bash

    llamavault remove NAME

You'll be asked to confirm the deletion.

Advanced Commands
--------------

Export Credentials
^^^^^^^^^^^^^^^^

Export credentials to a ``.env`` file for use in applications:

.. code-block:: bash

    llamavault export FILE [--uppercase/--no-uppercase]

Options:

- ``--uppercase/--no-uppercase``: Convert credential names to uppercase (default: true)

Example:

.. code-block:: bash

    llamavault export .env

This creates a ``.env`` file with all credentials in the format:

.. code-block:: text

    NAME=value
    OTHER_NAME=other_value

Backup the Vault
^^^^^^^^^^^^^^

Create a backup of your vault:

.. code-block:: bash

    llamavault backup [--backup-dir PATH]

Options:

- ``--backup-dir PATH``: Directory to store the backup

The backup is encrypted with your vault password and includes all credentials and metadata.

Change Password
^^^^^^^^^^^^^

Change the password for your vault:

.. code-block:: bash

    llamavault change_password

You'll be prompted for your current password and your new password.

Web Interface
^^^^^^^^^^^

Start the web interface:

.. code-block:: bash

    llamavault web [--host HOST] [--port PORT]

Options:

- ``--host HOST``: Host to listen on (default: 127.0.0.1)
- ``--port PORT``: Port to listen on (default: 5000)

Examples
-------

Here are some common usage examples:

Managing API Keys
^^^^^^^^^^^^^^^

.. code-block:: bash

    # Add an OpenAI API key
    llamavault add openai_api_key
    
    # Use it in a script
    export OPENAI_API_KEY=$(llamavault get openai_api_key)
    python my_script.py

Working with Different Environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Create environment-specific vaults
    llamavault --vault-dir ~/.llamavault-dev init
    llamavault --vault-dir ~/.llamavault-prod init
    
    # Add credentials to development environment
    llamavault --vault-dir ~/.llamavault-dev add database_url
    
    # Add credentials to production environment
    llamavault --vault-dir ~/.llamavault-prod add database_url

Sharing Credentials Securely
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can create a vault specifically for sharing with teammates:

.. code-block:: bash

    # Create a team vault
    llamavault --vault-dir ~/team-vault init
    
    # Add team credentials
    llamavault --vault-dir ~/team-vault add shared_api_key
    
    # Create a backup for sharing
    llamavault --vault-dir ~/team-vault backup --backup-dir ./
    
    # Share the backup file and password securely with teammates

Scripting with LlamaVault
^^^^^^^^^^^^^^^^^^^^^^^

You can use LlamaVault in shell scripts:

.. code-block:: bash

    #!/bin/bash
    
    # Get API key
    API_KEY=$(llamavault get api_key)
    
    # Use the API key
    curl -H "Authorization: Bearer $API_KEY" https://api.example.com/data

Environment Variables
------------------

LlamaVault recognizes the following environment variables:

- ``LLAMAVAULT_PASSWORD``: Vault password (use with caution)
- ``LLAMAVAULT_DIR``: Custom vault directory
- ``LLAMAVAULT_DEBUG``: Enable debug mode (set to any value)

For example:

.. code-block:: bash

    # Set the vault password (not recommended for production)
    export LLAMAVAULT_PASSWORD="your-password"
    
    # Set a custom vault directory
    export LLAMAVAULT_DIR="/path/to/vault"
    
    # Enable debug mode
    export LLAMAVAULT_DEBUG=1 