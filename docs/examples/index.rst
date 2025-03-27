Example Code
===========

This section contains example code demonstrating how to use LlamaVault in various scenarios.

Basic Usage
---------

.. literalinclude:: basic_usage.py
   :language: python
   :caption: Basic usage of LlamaVault
   :name: basic-usage-example

Advanced Usage
-----------

.. literalinclude:: advanced_usage.py
   :language: python
   :caption: Advanced usage patterns with LlamaVault
   :name: advanced-usage-example

AI Framework Integrations
----------------------

.. literalinclude:: ai_integrations.py
   :language: python
   :caption: Integrating LlamaVault with AI frameworks
   :name: ai-integrations-example

CI/CD Integrations
---------------

.. literalinclude:: ci_cd_integrations.py
   :language: python
   :caption: Integrating LlamaVault with CI/CD systems
   :name: ci-cd-integrations-example

Docker Integrations
---------------

.. literalinclude:: docker_usage.py
   :language: python
   :caption: Using LlamaVault with Docker
   :name: docker-usage-example

Kubernetes Integrations
------------------

.. literalinclude:: kubernetes_integration.py
   :language: python
   :caption: Using LlamaVault with Kubernetes
   :name: kubernetes-integration-example

Code Examples by Topic
-------------------

Working with Multiple Vaults
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from llamavault import Vault
    
    # Development vault
    dev_vault = Vault(vault_dir="~/.llamavault-dev", password="dev-password")
    
    # Production vault
    prod_vault = Vault(vault_dir="~/.llamavault-prod", password="prod-password")
    
    # Use the appropriate vault based on environment
    env = os.environ.get("ENVIRONMENT", "development")
    vault = dev_vault if env == "development" else prod_vault
    
    api_key = vault.get_credential("api_key")

Automatic Credential Rotation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from llamavault import Vault
    from datetime import datetime, timedelta
    
    vault = Vault(password="secure-password")
    
    # Check if credential is older than 90 days
    credential = vault.get_credential_object("api_key")
    if credential.updated_at and (datetime.now() - credential.updated_at).days > 90:
        # Rotate the credential
        new_value = get_new_api_key_from_service()  # Your service-specific rotation logic
        
        # Update the vault with the new value
        vault.update_credential(
            "api_key", 
            new_value, 
            metadata={
                "rotated_at": datetime.now().isoformat(),
                "previous_rotation": credential.updated_at.isoformat() if credential.updated_at else None
            }
        )
        
        print(f"Rotated credential api_key")

Context Manager Pattern
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from llamavault import Vault
    import getpass
    
    class VaultContext:
        def __init__(self, vault_dir=None, password=None):
            self.vault_dir = vault_dir
            self.password = password
            self.vault = None
            
        def __enter__(self):
            if self.password is None:
                self.password = getpass.getpass("Vault password: ")
            self.vault = Vault(vault_dir=self.vault_dir, password=self.password)
            return self.vault
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Any cleanup if needed
            pass
    
    # Usage
    with VaultContext(password="secure-password") as vault:
        api_key = vault.get_credential("api_key")
        # Use the API key
        print(f"Using API key: {api_key}")

Using Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from llamavault import Vault
    import os
    
    vault = Vault(password="secure-password")
    
    # Export specific credentials to environment
    os.environ["OPENAI_API_KEY"] = vault.get_credential("openai_api_key")
    os.environ["PINECONE_API_KEY"] = vault.get_credential("pinecone_api_key")
    
    # Export all credentials with uppercase names
    env_vars = vault.export_env(uppercase=True)
    
    # Or write to .env file
    vault.export_env_file(".env")

CI/CD Integration with GitHub Actions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    # .github/workflows/deploy.yml
    name: Deploy
    
    on:
      push:
        branches: [ main ]
    
    jobs:
      deploy:
        runs-on: ubuntu-latest
        
        steps:
          - uses: actions/checkout@v3
          
          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.10'
              
          - name: Install LlamaVault
            run: pip install llamavault
            
          - name: Set up credentials
            run: |
              echo "${{ secrets.VAULT_PASSWORD }}" | llamavault export --password-stdin > .env
            
          - name: Run deployment with credentials
            run: |
              set -a; source .env; set +a
              ./deploy.sh

Docker Integration Example
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: dockerfile

    # Dockerfile
    FROM python:3.10-slim
    
    # Install LlamaVault
    RUN pip install llamavault
    
    # Create a non-root user
    RUN useradd -m appuser
    USER appuser
    WORKDIR /home/appuser
    
    # Copy application code
    COPY --chown=appuser:appuser app.py .
    
    # Run with credentials from vault
    CMD ["python", "app.py"]

Running with Docker:

.. code-block:: bash

    # First, export credentials to .env file
    llamavault export .env
    
    # Run container with env file approach
    docker run --env-file .env myapp
    
    # Or run with vault mounted approach
    docker run -e VAULT_PASSWORD=mypassword \
      -v ~/.llamavault:/home/appuser/.llamavault \
      myapp

Kubernetes Integration Example
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    # kubernetes/secret.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: app-credentials
      namespace: default
      labels:
        managed-by: llamavault
    type: Opaque
    data:
      database_password: <base64-encoded-password>
      api_key: <base64-encoded-api-key>

Applying to Kubernetes:

.. code-block:: bash

    # Export credentials to Kubernetes YAML
    llamavault kubernetes export --namespace my-app --output-dir k8s
    
    # Apply the generated manifests
    kubectl apply -f k8s/

Custom Metadata Processing
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from llamavault import Vault
    import json
    from datetime import datetime
    
    vault = Vault(password="secure-password")
    
    # Add credential with rich metadata
    vault.add_credential(
        "database_url",
        "postgresql://user:pass@localhost/db",
        metadata={
            "environment": "development",
            "owner": "data-team",
            "expiry": (datetime.now() + timedelta(days=90)).isoformat(),
            "rotation_policy": "90_days",
            "services": ["analytics", "reporting"]
        }
    )
    
    # Query credentials with specific metadata
    dev_credentials = []
    for name in vault.list_credentials():
        cred = vault.get_credential_object(name)
        if cred.metadata and cred.metadata.get("environment") == "development":
            dev_credentials.append(cred)
            
    print(f"Found {len(dev_credentials)} development credentials")
    
    # Export credentials for a specific service
    service_creds = {}
    for name in vault.list_credentials():
        cred = vault.get_credential_object(name)
        if cred.metadata and "services" in cred.metadata and "analytics" in cred.metadata["services"]:
            service_creds[name] = cred.value
            
    with open("analytics_creds.json", "w") as f:
        json.dump(service_creds, f)

Downloading Examples
-----------------

You can download these examples from the LlamaVault repository:

.. code-block:: bash

    git clone https://github.com/llamasearch/llamavault.git
    cd llamavault/examples 