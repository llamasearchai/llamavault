Architecture Overview
===================

This document provides an overview of LlamaVault's architecture, explaining the major components and how they interact. Understanding this architecture is essential for developers who want to contribute to the project or build extensions.

Key Components
------------

LlamaVault consists of several key components:

1. **Core Library**: The central credential management functionality
2. **CLI Interface**: Command-line interface for interacting with vaults
3. **Web Interface**: Browser-based interface for credential management
4. **Plugin System**: Extension mechanism for additional features
5. **Storage Backends**: Abstraction for where vault data is stored

System Architecture Diagram
------------------------

.. code-block:: text

    +---------------------------+
    |        Applications       |
    |  (Using LlamaVault API)   |
    +---------------------------+
               |
               v
    +---------------------------+     +---------------+
    |      Public API Layer     |<--->|  CLI & Web    |
    |     (Vault, Credential)   |     |  Interfaces   |
    +---------------------------+     +---------------+
               |                           |
               v                           v
    +---------------------------+     +---------------+
    |    Credential Manager     |<--->|    Plugin     |
    |                           |     |    System     |
    +---------------------------+     +---------------+
               |
               v
    +---------------------------+
    |     Encryption Layer      |
    |                           |
    +---------------------------+
               |
               v
    +---------------------------+
    |     Storage Backend       |
    | (File, DB, S3, etc.)      |
    +---------------------------+

Core Library
-----------

The core library is responsible for the secure management of credentials. It handles:

- Credential encryption and decryption
- Vault storage and retrieval
- Access control and authentication

Key classes in the core library:

- **Vault**: Main entry point for credential operations
- **Credential**: Represents a stored credential with metadata
- **Encryption**: Handles encryption/decryption of vault data

Implementation Details
^^^^^^^^^^^^^^^^^^^

The `Vault` class uses a layered approach to security:

1. Password-based key derivation using PBKDF2
2. AES-256-GCM encryption for credential values
3. HMAC-SHA256 for authentication and integrity verification

Vault data is stored in two files:

- `config.json`: Contains non-sensitive configuration data
- `vault.json`: Contains encrypted credentials and metadata

Data Flow
^^^^^^^^

1. User provides password to open vault
2. Master key is derived from password using PBKDF2
3. Vault reads and decrypts credentials
4. Credential operations work with decrypted data in memory
5. On save, credentials are encrypted and written to storage

CLI Interface
-----------

The CLI interface provides command-line access to vault operations, using Click for argument parsing and command structure.

Key components:

- **Command Groups**: Logical organization of commands
- **Pass Decorators**: Share vault instances between commands
- **Formatters**: Format output for the terminal

The CLI follows a pattern of:

.. code-block:: bash

    llamavault [global options] command [command options] [arguments]

Web Interface
-----------

The web interface is built with Flask and provides a browser-based UI for managing credentials.

Key components:

- **Flask App**: Handles HTTP requests and responses
- **Routes**: Define API endpoints and views
- **Templates**: Jinja2 templates for HTML rendering
- **Session Management**: Secure user sessions

Authentication flow:

1. User navigates to web interface
2. Login form requests vault password
3. Server verifies password by attempting to open vault
4. On success, a session is created with limited lifetime
5. Subsequent requests use session for authentication

Plugin System
-----------

The plugin system allows third-party extensions to LlamaVault using Python's entry points mechanism.

Plugin types:

- **Core Plugins**: Extend core functionality
- **CLI Plugins**: Add new commands
- **Web Plugins**: Add web interface features
- **Storage Plugins**: Provide alternative storage backends

Plugin discovery:

1. Entry points are queried at startup
2. Plugin classes are instantiated
3. Plugins register hooks for various events
4. Hooks are called during normal operation

Storage Backends
-------------

Storage backends abstract how vault data is persisted. The default is file-based storage, but alternatives can be implemented.

Backend interface:

- **read(path)**: Read data from storage
- **write(path, data)**: Write data to storage
- **exists(path)**: Check if path exists
- **delete(path)**: Remove data from storage

Security Considerations
--------------------

LlamaVault's security model is based on several core principles:

1. **Zero Knowledge**: The server never has access to unencrypted credentials
2. **Defense in Depth**: Multiple layers of security
3. **Secure by Default**: Strong defaults with minimal configuration
4. **Principle of Least Privilege**: Access only what's needed

Attack Surfaces
^^^^^^^^^^^

The main attack surfaces are:

- **Password Strength**: Weak passwords can be brute-forced
- **Memory Safety**: Credentials are decrypted in memory
- **API Security**: Web interface authentication and authorization
- **Storage Security**: Access to underlying storage

Mitigations
^^^^^^^^^

1. **Password Complexity**: Encouragement of strong passwords
2. **Memory Management**: Limiting credential lifetime in memory
3. **Session Security**: Short-lived sessions and CSRF protection
4. **Storage Encryption**: Encrypted storage by default

Code Organization
--------------

The LlamaVault codebase is organized as follows:

.. code-block:: text

    llamavault/
    ├── src/
    │   └── llamavault/
    │       ├── __init__.py       # Package exports
    │       ├── vault.py          # Main Vault class
    │       ├── credential.py     # Credential class
    │       ├── exceptions.py     # Custom exceptions
    │       ├── encryption.py     # Encryption utilities
    │       ├── cli/              # CLI interface
    │       │   ├── __init__.py
    │       │   ├── main.py       # CLI entry point
    │       │   └── commands/     # CLI command groups
    │       ├── web/              # Web interface
    │       │   ├── __init__.py
    │       │   ├── app.py        # Flask application
    │       │   ├── routes.py     # HTTP routes
    │       │   └── templates/    # HTML templates
    │       ├── plugins/          # Plugin system
    │       │   ├── __init__.py
    │       │   └── base.py       # Plugin base classes
    │       └── storage/          # Storage backends
    │           ├── __init__.py
    │           ├── base.py       # Backend interface
    │           └── file.py       # File-based storage
    ├── tests/                    # Test suite
    ├── docs/                     # Documentation
    └── examples/                 # Example code

Development Workflow
-----------------

When developing for LlamaVault, follow these guidelines:

1. **Feature Branches**: Create a branch for each feature or bugfix
2. **Testing**: Write tests for new functionality
3. **Type Hints**: Use Python type hints for better code quality
4. **Documentation**: Update documentation for API changes
5. **Version Compatibility**: Maintain compatibility within major versions

Testing Architecture
-----------------

LlamaVault uses pytest for testing. The test suite includes:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test components working together
- **Security Tests**: Verify security properties
- **CLI Tests**: Test command-line interface
- **Web Tests**: Test web interface

Test fixtures provide common setup and teardown across tests, including:

- **Temporary Vaults**: Created and destroyed for each test
- **Mock Backends**: Simulate storage backends
- **Test Credentials**: Sample data for testing

Future Architecture Enhancements
-----------------------------

Planned architectural improvements include:

1. **Asynchronous API**: Support for async/await operations
2. **Remote Vaults**: Support for centralized credential stores
3. **Multi-User Access**: Role-based access control for shared vaults
4. **Event System**: More comprehensive event hooks for plugins
5. **Caching Layer**: Performance improvements for frequent access

Contributing to Architecture
-------------------------

When proposing architectural changes:

1. **Document the Change**: Clearly explain the improvement
2. **Consider Backward Compatibility**: Avoid breaking existing code
3. **Security Analysis**: Analyze security implications
4. **Performance Impact**: Consider performance effects
5. **Extension Points**: Maintain plugin compatibility 