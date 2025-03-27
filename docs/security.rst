Security
========

LlamaVault is designed with security as a top priority. This page describes the security measures implemented to protect your sensitive credentials.

Encryption
---------

All credentials stored in LlamaVault are encrypted using industry-standard algorithms:

- **AES-256-GCM** (Advanced Encryption Standard with 256-bit keys in Galois/Counter Mode) for symmetric encryption of credential values and metadata
- **PBKDF2** (Password-Based Key Derivation Function 2) with a high iteration count for deriving encryption keys from passwords
- **HMAC-SHA256** for authentication and integrity verification

Credential Encryption Flow
^^^^^^^^^^^^^^^^^^^^^^^^^

1. User provides a master password
2. The password is fed through PBKDF2 with a unique salt to derive an encryption key
3. Each credential is encrypted individually using AES-256-GCM with a unique initialization vector (IV)
4. The encrypted credential, along with its metadata, is stored in the vault file

Vault Structure
-------------

The vault consists of two main files:

1. **config.json**: Contains non-sensitive configuration data, including:
   - Salt for key derivation
   - Vault version information
   - Other configuration parameters

2. **vault.json**: Contains the encrypted credentials, including:
   - Encrypted credential values
   - Encrypted metadata
   - Creation and update timestamps
   - IVs and authentication tags for each credential

Neither file contains the master password or the derived encryption key, which are kept only in memory during operation.

Password Security
---------------

Password Handling
^^^^^^^^^^^^^^^

LlamaVault never stores your master password. Instead:

- The password is used to derive an encryption key using PBKDF2
- The derived key is used only in memory during vault operations
- The password is cleared from memory as soon as it's no longer needed

Password Requirements
^^^^^^^^^^^^^^^^^^^

While LlamaVault doesn't enforce specific password requirements, we strongly recommend:

- Using a strong, unique password with at least 12 characters
- Including a mix of uppercase and lowercase letters, numbers, and special characters
- Avoiding passwords used for other services
- Considering using a password manager to generate and store your master password

Web Interface Security
-------------------

The web interface includes several security measures:

- **Session Management**: Sessions expire after a short period of inactivity
- **CSRF Protection**: All forms include CSRF tokens to prevent cross-site request forgery attacks
- **HTTPS**: We recommend serving the web interface over HTTPS in production environments
- **Password Masking**: Credential values are masked in the UI unless explicitly viewed
- **Secure Cookies**: Cookies are set with the HttpOnly flag to prevent JavaScript access

Network Security
--------------

By default, the web interface listens only on ``127.0.0.1`` (localhost), preventing access from other machines. If you need to access the web interface from other machines, we recommend:

- Using a reverse proxy with HTTPS (like Nginx or Apache)
- Setting up authentication at the proxy level
- Using a firewall to restrict access to trusted IP addresses

Security Best Practices
--------------------

Backups
^^^^^^^

Backups created by LlamaVault are encrypted with the same master password as the vault. This ensures that even if a backup file is compromised, the credentials remain protected.

Environment Variables
^^^^^^^^^^^^^^^^^^^

While LlamaVault allows setting the master password via the ``LLAMAVAULT_PASSWORD`` environment variable, we recommend against using this feature in production environments, as environment variables may be visible to other processes or in system logs.

Audit Logging
^^^^^^^^^^^

LlamaVault maintains basic audit logs of credential access and modifications. These logs include:

- Timestamps for credential creation, updates, and access
- User information (when using the web interface)

To enable more detailed logging, use the ``--debug`` flag with the CLI or set the ``LLAMAVAULT_DEBUG`` environment variable.

Security Limitations
-----------------

While LlamaVault provides strong encryption for stored credentials, it's important to be aware of these limitations:

- **Memory-Safe Languages**: LlamaVault is written in Python, which doesn't provide the same memory safety guarantees as languages like Rust or Go. Sensitive information may remain in memory longer than strictly necessary.
- **In-Memory Attacks**: When a credential is in use, it must be decrypted in memory. During this time, it could potentially be exposed to memory-scanning malware or in crash dumps.
- **Key Stretching**: While PBKDF2 provides key stretching, dedicated password cracking hardware can still attempt many passwords per second if an attacker obtains the vault file.

Reporting Security Issues
-----------------------

If you discover a security vulnerability in LlamaVault, please do not disclose it publicly until we've had a chance to address it. Instead, please send a description of the issue to security@llamasearch.ai.

We appreciate your help in keeping LlamaVault secure for all users. 