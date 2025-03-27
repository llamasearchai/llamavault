Best Practices for Secure Credential Management
=========================================

This guide outlines best practices for using LlamaVault securely to manage credentials for AI/ML applications and other sensitive systems.

Password Security
---------------

Your master password is the foundation of your vault's security:

- **Use a Strong Password**: Create a unique, complex password with a minimum of 12 characters
- **Password Managers**: Consider using a dedicated password manager to generate and store your master password
- **Rotation**: Change your master password periodically (3-6 months recommended)
- **Avoid Reuse**: Never use the same password for your vault that you use for other services
- **Environmental Factors**: Be mindful of your surroundings when entering your password

Recommended Password Guidelines:

.. code-block:: text

    ✓ Minimum 12 characters
    ✓ Combination of uppercase, lowercase, numbers, and symbols
    ✓ Not based on dictionary words or personal information
    ✓ Not used for other accounts
    ✓ Changed periodically
    ✗ Avoid common patterns (12345, qwerty, etc.)
    ✗ Avoid obvious personal information (birthdays, names, etc.)

Vault Management
--------------

Keeping your vault secure requires good management practices:

- **Regular Backups**: Use the ``llamavault backup`` command regularly
- **Audit Access**: Review who has access to your vault files
- **Keep Software Updated**: Run the latest version of LlamaVault
- **Secure Storage**: Ensure the underlying filesystem is secure
- **Limit Access**: Grant access to your vault only to those who need it

Secure Backup Strategy:

1. Create regular backups with ``llamavault backup``
2. Store backups in multiple secure locations
3. Test restoration procedures periodically
4. Consider encrypting backup media with additional measures
5. Implement a retention policy for old backups

Credential Practices
-----------------

Best practices for working with individual credentials:

- **Descriptive Names**: Use clear, consistent naming for credentials
- **Use Metadata**: Add context with metadata (service, purpose, expiration)
- **Regular Rotation**: Set and follow credential rotation schedules
- **Least Privilege**: Use credentials with minimal required permissions
- **Credential Lifecycle**: Promptly remove credentials for services no longer in use

Example Naming Convention:

.. code-block:: text

    <service>_<environment>_<credential_type>

    Examples:
    - aws_prod_access_key
    - openai_dev_api_key
    - database_staging_password

Using Metadata Effectively:

.. code-block:: python

    vault.add_credential(
        "openai_api_key",
        "sk-...",
        metadata={
            "created_by": "alex",
            "environment": "production",
            "rotation_date": "2023-12-31",
            "service": "OpenAI GPT-4",
            "rate_limits": "5000 tokens/min",
            "usage": "Customer support chatbot"
        }
    )

Environment Variables
------------------

When exporting credentials as environment variables:

- **Ephemeral Use**: Export variables only for the duration needed
- **Avoid Shell History**: Use techniques to prevent commands with secrets from being recorded in shell history
- **Clear Environment**: Clear environment variables after use when possible
- **Subprocess Isolation**: Be mindful that child processes inherit environment variables

Safer Environment Variable Usage:

.. code-block:: bash

    # Export to .env file instead of directly to environment
    llamavault export .env
    
    # Load variables only in the context needed
    set -a; source .env; set +a
    
    # Run your application
    python my_app.py
    
    # Clear variables after use (in ephemeral contexts)
    unset OPENAI_API_KEY

In Python Scripts:

.. code-block:: python

    # Load credentials only in the scope where needed
    from llamavault import Vault
    import os
    
    def function_needing_credentials():
        with Vault(password=get_password()) as vault:
            os.environ["API_KEY"] = vault.get_credential("api_key")
            # Use the credential
            result = make_api_call()
            # Clear from environment
            del os.environ["API_KEY"]
        return result

Web Interface Security
-------------------

When using the web interface:

- **Local Access**: Prefer accessing the web interface only from localhost
- **HTTPS**: Use HTTPS when exposing the interface beyond localhost
- **Session Timeout**: Set appropriate session timeouts (default is 30 minutes)
- **Secure Browsers**: Use updated browsers with security features enabled
- **Authentication**: Use strong authentication mechanisms

Exposing Web Interface Securely:

.. code-block:: bash

    # Run with HTTPS
    llamavault web --ssl-cert /path/to/cert.pem --ssl-key /path/to/key.pem
    
    # Or use behind a secure reverse proxy like nginx/Apache with proper HTTPS

API and Integration Security
-------------------------

When integrating LlamaVault with other systems:

- **API Security**: Secure API connections with proper authentication and TLS
- **CI/CD Integration**: Use secure methods to provide credentials to CI/CD systems
- **Service Accounts**: Create dedicated service accounts with limited permissions
- **Logging**: Balance security and troubleshooting in log detail levels
- **Monitoring**: Monitor for unusual access patterns

Example CI/CD Integration:

.. code-block:: yaml

    # GitHub Actions example using vault export
    steps:
      - name: Install LlamaVault
        run: pip install llamavault
        
      - name: Get credentials from vault
        run: |
          echo "${{ secrets.VAULT_PASSWORD }}" | llamavault export --password-stdin > .env
        
      - name: Run tests with credentials
        run: |
          set -a; source .env; set +a
          pytest

Team Usage Patterns
----------------

For teams using LlamaVault:

- **Shared Access Protocols**: Establish clear procedures for shared vault access
- **Onboarding/Offboarding**: Include vault access in employee procedures
- **Credential Ownership**: Assign ownership for specific credentials
- **Emergencies**: Create break-glass procedures for emergency access
- **Training**: Ensure all team members understand secure credential practices

Security Auditing
--------------

Regular security reviews help maintain vault security:

- **Access Logs**: Review vault access logs periodically
- **Vulnerability Scans**: Scan systems hosting LlamaVault
- **Credential Inventory**: Maintain an inventory of active credentials
- **Security Testing**: Perform security testing of your vault setup
- **Third-Party Audits**: Consider external security reviews for critical deployments

For highly sensitive environments, consider using the audit plugin:

.. code-block:: bash

    # Install the audit plugin
    pip install llamavault-plugin-audit
    
    # Generate access reports
    llamavault audit-report --days 30

Troubleshooting Securely
---------------------

When troubleshooting issues:

- **Avoid Exposure**: Never share raw credentials during troubleshooting
- **Sanitized Logs**: Ensure logs don't contain sensitive information
- **Test Credentials**: Use test credentials for troubleshooting when possible
- **Secure Support Channels**: Use secure channels for support

Secure Coding with LlamaVault
--------------------------

When developing applications that use LlamaVault:

- **Error Handling**: Handle LlamaVault errors gracefully without exposing sensitive information
- **Dependency Security**: Keep dependencies up to date
- **Secrets in Code**: Never hardcode credentials or vault passwords in source code
- **Memory Management**: Be mindful of how long credentials stay in memory
- **Secure Communication**: Use secure channels for all credential transmission

Example of secure error handling:

.. code-block:: python

    from llamavault import Vault, AuthenticationError, CredentialNotFoundError
    
    try:
        vault = Vault(password=get_password())
        credential = vault.get_credential("api_key")
    except AuthenticationError:
        # Log the error type but not the attempted password
        logger.error("Authentication failed when accessing vault")
        return handle_auth_error()
    except CredentialNotFoundError:
        # Log which credential was missing but no other details
        logger.error("Required credential 'api_key' not found in vault")
        return handle_missing_credential()
    except Exception as e:
        # Don't expose internal vault details in logs
        logger.error(f"Error accessing vault: {type(e).__name__}")
        return handle_general_error()

Resources and References
---------------------

For more information on secure credential management:

- **NIST Guidelines**: Refer to NIST SP 800-63B for password and authentication guidelines
- **OWASP**: Review the OWASP Top 10 security risks
- **Cloud Security Alliance**: Guidelines for secrets management
- **AWS/Azure/GCP**: Best practices for credential management in cloud environments
- **CIS Benchmarks**: Security configuration benchmarks for various systems

Quick Reference
------------

**Daily Operations**:
- Use a strong master password
- Export credentials only when needed
- Clear environment variables after use
- Keep vault backups current

**Weekly Tasks**:
- Review access logs
- Verify vault backups
- Remove unused credentials

**Monthly Review**:
- Rotate high-value credentials
- Update LlamaVault to latest version
- Audit credential inventory

**Quarterly Actions**:
- Consider rotating master password
- Review security practices
- Test recovery procedures 