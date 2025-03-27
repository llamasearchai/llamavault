Plugin Development Guide
=====================

LlamaVault provides a plugin system that allows for extending its functionality in various ways. This guide covers how to create plugins for LlamaVault, the available hook points, and best practices for plugin development.

Plugin Architecture
----------------

LlamaVault uses a simple yet powerful plugin architecture based on entry points. Plugins can extend various parts of the system, including:

- Adding new commands to the CLI
- Providing additional storage backends
- Adding custom authentication methods
- Extending the web interface
- Intercepting and processing credentials
- Adding new export formats

Plugin Registration
----------------

Plugins are registered using Python's entry points mechanism. To create a plugin:

1. Create a Python package that implements your plugin's functionality
2. Define entry points in your package's `setup.py` or `pyproject.toml`
3. Install your package alongside LlamaVault

Here's an example `setup.py` for a simple plugin:

.. code-block:: python

    from setuptools import setup, find_packages
    
    setup(
        name="llamavault-plugin-example",
        version="0.1.0",
        packages=find_packages(),
        entry_points={
            "llamavault.plugins": [
                "example = llamavault_plugin_example:ExamplePlugin",
            ],
            "llamavault.cli_commands": [
                "example = llamavault_plugin_example.cli:example_command",
            ],
        },
        install_requires=[
            "llamavault>=0.2.0",
        ],
    )

Plugin Base Class
--------------

All plugins should inherit from the `LlamaVaultPlugin` base class:

.. code-block:: python

    from llamavault.plugins import LlamaVaultPlugin
    
    class ExamplePlugin(LlamaVaultPlugin):
        """Example plugin for LlamaVault."""
        
        name = "example"
        version = "0.1.0"
        
        def initialize(self):
            """Initialize the plugin."""
            self.logger.info("Example plugin initialized")
        
        def on_vault_open(self, vault):
            """Called when a vault is opened."""
            self.logger.debug(f"Vault opened: {vault.config.get('vault_id')}")
        
        def on_credential_access(self, credential):
            """Called when a credential is accessed."""
            self.logger.debug(f"Credential accessed: {credential.name}")

Available Hook Points
------------------

Core Hooks
^^^^^^^^^

- `initialize()`: Called when the plugin is first loaded
- `shutdown()`: Called when the application is shutting down

Vault Hooks
^^^^^^^^^^

- `on_vault_init(vault)`: Called when a new vault is initialized
- `on_vault_open(vault)`: Called when a vault is opened
- `on_vault_save(vault)`: Called before a vault is saved
- `on_vault_backup(vault, backup_path)`: Called when a vault is backed up

Credential Hooks
^^^^^^^^^^^^^

- `on_credential_add(credential)`: Called when a credential is added
- `on_credential_update(credential, old_credential)`: Called when a credential is updated
- `on_credential_access(credential)`: Called when a credential is accessed
- `on_credential_remove(credential)`: Called when a credential is removed

Web Interface Hooks
^^^^^^^^^^^^^^^^

- `register_web_routes(app)`: Called to register additional Flask routes
- `extend_web_context(context)`: Called to extend template context
- `on_web_auth(user_id)`: Called when a user authenticates to the web interface

Creating CLI Commands
------------------

You can add new commands to the CLI by registering entry points under `llamavault.cli_commands`:

.. code-block:: python

    # in llamavault_plugin_example/cli.py
    import click
    from llamavault.cli.utils import pass_vault
    
    @click.command()
    @click.option("--name", help="Name to greet")
    @pass_vault
    def example_command(vault, name):
        """Example command added by plugin."""
        click.echo(f"Hello, {name}! Your vault has {len(vault.list_credentials())} credentials.")
        
    # Then in setup.py:
    # entry_points={
    #     "llamavault.cli_commands": [
    #         "example = llamavault_plugin_example.cli:example_command",
    #     ],
    # }

Extending the Web Interface
------------------------

Plugins can extend the web interface by registering Flask routes and providing templates:

.. code-block:: python

    from flask import render_template, Blueprint
    
    class WebInterfacePlugin(LlamaVaultPlugin):
        def register_web_routes(self, app):
            blueprint = Blueprint('example_plugin', __name__, 
                                template_folder='templates',
                                static_folder='static')
            
            @blueprint.route('/plugin/example')
            def example_page():
                return render_template('example_plugin/page.html')
            
            app.register_blueprint(blueprint)
        
        def extend_web_context(self, context):
            # Add data to all templates
            context['example_plugin_version'] = self.version

Custom Storage Backends
--------------------

To implement a custom storage backend:

.. code-block:: python

    from llamavault.storage import StorageBackend
    
    class S3StorageBackend(StorageBackend):
        """AWS S3 storage backend for LlamaVault."""
        
        name = "s3"
        
        def __init__(self, bucket_name, prefix=None, **kwargs):
            self.bucket_name = bucket_name
            self.prefix = prefix or ""
            self.s3_client = boto3.client('s3', **kwargs)
        
        def read(self, path):
            """Read data from the storage backend."""
            key = self._get_key(path)
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        
        def write(self, path, data):
            """Write data to the storage backend."""
            key = self._get_key(path)
            self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=data)
        
        def _get_key(self, path):
            """Convert a path to an S3 key."""
            return f"{self.prefix.rstrip('/')}/{path.lstrip('/')}"
    
    # Register in setup.py:
    # entry_points={
    #     "llamavault.storage_backends": [
    #         "s3 = llamavault_plugin_s3:S3StorageBackend",
    #     ],
    # }

Best Practices
-----------

1. **Version Compatibility**: Clearly specify which versions of LlamaVault your plugin is compatible with
2. **Error Handling**: Handle errors gracefully and don't break the main application flow
3. **Logging**: Use the plugin's logger (`self.logger`) for diagnostic information
4. **Configuration**: Store plugin configuration in a standard location
5. **Documentation**: Provide clear documentation on how to use your plugin
6. **Testing**: Write tests for your plugin functionality

Example Plugin
-----------

Here's a complete example of a simple plugin that logs credential access:

.. code-block:: python

    # llamavault_plugin_audit/plugin.py
    from llamavault.plugins import LlamaVaultPlugin
    import time
    import json
    import os
    from pathlib import Path
    
    class AuditPlugin(LlamaVaultPlugin):
        """Plugin that logs all credential access."""
        
        name = "audit"
        version = "0.1.0"
        
        def initialize(self):
            """Initialize the audit plugin."""
            self.audit_dir = self._get_audit_dir()
            self.audit_dir.mkdir(exist_ok=True, parents=True)
            self.logger.info(f"Audit plugin initialized. Logs in {self.audit_dir}")
        
        def on_credential_access(self, credential):
            """Log when a credential is accessed."""
            log_entry = {
                "timestamp": time.time(),
                "action": "access",
                "credential_name": credential.name,
                "credential_created_at": credential.created_at.isoformat() if credential.created_at else None,
                "metadata": credential.metadata
            }
            
            log_file = self.audit_dir / f"audit_{time.strftime('%Y-%m-%d')}.jsonl"
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        
        def _get_audit_dir(self):
            """Get the directory for audit logs."""
            vault_dir = os.environ.get("LLAMAVAULT_DIR")
            if vault_dir:
                base_dir = Path(vault_dir)
            else:
                base_dir = Path.home() / ".llamavault"
            return base_dir / "audit_logs"
    
    # llamavault_plugin_audit/cli.py
    import click
    import json
    from pathlib import Path
    from datetime import datetime, timedelta
    
    @click.command()
    @click.option("--days", default=7, help="Number of days to include in the report")
    def audit_report(days):
        """Generate an audit report of credential access."""
        plugin = AuditPlugin()
        plugin.initialize()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        click.echo(f"Audit report from {start_date.date()} to {end_date.date()}")
        click.echo("-" * 50)
        
        access_count = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            log_file = plugin._get_audit_dir() / f"audit_{date_str}.jsonl"
            
            if log_file.exists():
                with open(log_file) as f:
                    for line in f:
                        entry = json.loads(line)
                        cred_name = entry["credential_name"]
                        if cred_name not in access_count:
                            access_count[cred_name] = 0
                        access_count[cred_name] += 1
            
            current_date += timedelta(days=1)
        
        for cred_name, count in sorted(access_count.items(), key=lambda x: x[1], reverse=True):
            click.echo(f"{cred_name}: {count} accesses")
    
    # setup.py
    from setuptools import setup, find_packages
    
    setup(
        name="llamavault-plugin-audit",
        version="0.1.0",
        packages=find_packages(),
        entry_points={
            "llamavault.plugins": [
                "audit = llamavault_plugin_audit.plugin:AuditPlugin",
            ],
            "llamavault.cli_commands": [
                "audit-report = llamavault_plugin_audit.cli:audit_report",
            ],
        },
        install_requires=[
            "llamavault>=0.2.0",
            "click>=7.0",
        ],
    )

Publishing Plugins
---------------

LlamaVault plugins can be published on PyPI like any other Python package. Follow these conventions:

1. Name your package with a `llamavault-plugin-` prefix (e.g., `llamavault-plugin-aws`)
2. Include keywords like "llamavault" and "plugin" in your package metadata
3. Set a development status classifier appropriate for your plugin's maturity

Finding and Installing Plugins
---------------------------

Users can find LlamaVault plugins by searching PyPI:

.. code-block:: bash

    pip search llamavault-plugin

And install them with:

.. code-block:: bash

    pip install llamavault-plugin-name

Official Plugins
-------------

The following official plugins are maintained by the LlamaVault team:

- **llamavault-plugin-aws**: AWS integration, including S3 storage backend
- **llamavault-plugin-vault**: HashiCorp Vault integration
- **llamavault-plugin-keyring**: System keyring integration
- **llamavault-plugin-ldap**: LDAP authentication for web interface 