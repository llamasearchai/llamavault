LlamaVault Documentation
=====================

LlamaVault is a secure credential management tool designed for AI/ML applications. It provides encrypted storage for sensitive credentials with intuitive command-line and web interfaces.

.. image:: https://img.shields.io/pypi/v/llamavault.svg
   :target: https://pypi.org/project/llamavault/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/llamavault.svg
   :target: https://pypi.org/project/llamavault/
   :alt: Python Versions

.. image:: https://img.shields.io/github/license/llamasearch/llamavault.svg
   :target: https://github.com/llamasearch/llamavault/blob/main/LICENSE
   :alt: License

Features
-------

* **Secure Storage**: AES-256-GCM encryption for all credentials
* **CLI Interface**: Easy command-line management of credentials
* **Web Interface**: Browser-based credential management
* **Environment Integration**: Export credentials as environment variables
* **Plugin System**: Extensible architecture for custom functionality
* **Metadata Support**: Store additional information with credentials
* **API Access**: Programmatic access for integration with applications

Getting Started
-------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   cli_usage
   web_interface
   security
   best_practices

API Reference
-----------

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api/index
   api/vault
   api/credential
   api/exceptions

Developer Guide
-------------

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/architecture
   development/plugins
   development/contributing

Examples
-------

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index

Use Cases
--------

LlamaVault is ideal for securing:

* API keys for OpenAI, Anthropic, and other AI services
* Database credentials
* Cloud provider access keys
* OAuth tokens
* Webhook secrets
* SSH keys (via plugin)
* Internal service credentials

Installation
-----------

Quick installation:

.. code-block:: bash

   pip install llamavault

For web interface:

.. code-block:: bash

   pip install llamavault[web]

Basic Usage
---------

Initialize a vault:

.. code-block:: bash

   llamavault init

Add a credential:

.. code-block:: bash

   llamavault add openai_api_key "sk-..."

Retrieve a credential:

.. code-block:: bash

   llamavault get openai_api_key

Export all credentials as environment variables:

.. code-block:: bash

   llamavault export .env

Start the web interface:

.. code-block:: bash

   llamavault web

Project Status
------------

LlamaVault is under active development. Current version: |version|

Indices and tables
---------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 