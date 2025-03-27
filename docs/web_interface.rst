Web Interface
=============

LlamaVault provides a web interface for managing your credentials through a browser. This interface is particularly useful for team environments or for users who prefer a graphical interface over the command line.

Starting the Web Interface
-------------------------

To start the web interface, you need to have LlamaVault installed with web dependencies:

.. code-block:: bash

    # Install with web support if you haven't already
    pip install llamavault[web]
    
    # Start the web interface
    llamavault web

By default, the web interface listens on ``127.0.0.1:5000``. You can customize the host and port:

.. code-block:: bash

    llamavault web --host 0.0.0.0 --port 8080

.. note::
    Using ``0.0.0.0`` as the host makes the web interface accessible from other machines. 
    Make sure you have proper network security in place if you do this.

Using Docker
-----------

If you're using the Docker image, the web interface is included:

.. code-block:: bash

    docker run -p 5000:5000 -v ~/.llamavault:/data llamasearch/llamavault

Then access the web interface at http://localhost:5000.

Logging In
---------

When you access the web interface, you'll be prompted to unlock the vault with your password:

.. image:: images/login_screen.png
   :alt: Login Screen
   :width: 600px

The password is the same one you use for the CLI. If you haven't created a vault yet, you'll need to do so first using the CLI:

.. code-block:: bash

    llamavault init

Dashboard
--------

After logging in, you'll see the dashboard with an overview of your vault:

.. image:: images/dashboard.png
   :alt: Dashboard
   :width: 800px

The dashboard shows:

- Total number of credentials
- Most recently added credential
- Oldest credential
- A list of recent credentials

Managing Credentials
------------------

Adding Credentials
^^^^^^^^^^^^^^^^^

To add a new credential:

1. Click the "Add Credential" button in the top right
2. Fill in the credential name and value
3. Optionally, add metadata as a JSON object
4. Click "Save Credential"

.. image:: images/add_credential.png
   :alt: Add Credential Form
   :width: 700px

Viewing and Editing Credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can view all your credentials by clicking "Credentials" in the navigation bar:

.. image:: images/credentials_list.png
   :alt: Credentials List
   :width: 800px

To edit a credential:

1. Click the edit icon (pencil) next to the credential
2. Modify the name, value, or metadata as needed
3. Click "Save Credential"

Deleting Credentials
^^^^^^^^^^^^^^^^^^

To delete a credential:

1. Click the delete icon (trash) next to the credential
2. Confirm the deletion in the confirmation dialog

Exporting Credentials
-------------------

You can export all credentials to a ``.env`` file:

1. Click "Export" in the navigation bar
2. Choose whether to convert names to uppercase (recommended)
3. Click "Download .env File"

.. image:: images/export.png
   :alt: Export Credentials
   :width: 700px

Backing Up the Vault
------------------

To create a backup of your vault:

1. Click "Backup" in the navigation bar
2. Click "Create Backup"

The backup will be created in the default backup directory, which is a subdirectory called ``backups`` in your vault directory.

.. warning::
    Backups are encrypted with your vault password. If you forget your password, you won't be able to restore your credentials from a backup.

Security Considerations
---------------------

Session Expiration
^^^^^^^^^^^^^^^^^

For security reasons, web sessions expire after a short period of inactivity (30 minutes by default). You can choose "Remember Password" when logging in to extend this to 30 minutes.

CSRF Protection
^^^^^^^^^^^^

The web interface includes Cross-Site Request Forgery (CSRF) protection to prevent unauthorized requests.

API Endpoints
-----------

The web interface includes a simple API for interacting with the vault programmatically:

List Credentials
^^^^^^^^^^^^^^^

.. code-block:: bash

    GET /api/credentials

Returns a JSON object with all credentials (without their values for security).

Get Credential
^^^^^^^^^^^^^

.. code-block:: bash

    GET /api/credentials/{name}

Returns a JSON object with the specified credential, including its value.

These endpoints require authentication, just like the web interface.

Environment Variables
------------------

The web interface recognizes the following environment variables:

- ``LLAMAVAULT_DIR``: Custom vault directory
- ``LLAMAVAULT_SECRET_KEY``: Secret key for the Flask application (generated automatically if not provided)

Customizing the Web Interface
---------------------------

Advanced users can customize the web interface by creating custom templates. The templates are located in ``src/llamavault/web/templates``.

To customize the templates:

1. Copy the templates to a new location
2. Modify them as needed
3. Set the ``FLASK_APP_TEMPLATE_FOLDER`` environment variable to your custom template directory

For example:

.. code-block:: bash

    export FLASK_APP_TEMPLATE_FOLDER=/path/to/custom/templates
    llamavault web

Next Steps
---------

Now that you're familiar with the web interface, you can:

- Learn about the :doc:`security` measures in place
- Explore the :doc:`api/vault` for programmatic access
- Check out the :doc:`development` guide if you want to contribute to LlamaVault 