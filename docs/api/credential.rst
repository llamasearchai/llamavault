Credential API
=============

The ``Credential`` class represents a stored credential with metadata in LlamaVault.

.. py:class:: llamavault.Credential(name, value, created_at=None, updated_at=None, last_accessed=None, metadata=None)

   A secure credential with associated metadata.
   
   :param name: Name of the credential
   :type name: str
   :param value: Value of the credential (secret)
   :type value: str
   :param created_at: Timestamp of when the credential was created (default: current time)
   :type created_at: datetime or str, optional
   :param updated_at: Timestamp of when the credential was last updated (default: same as created_at)
   :type updated_at: datetime or str, optional
   :param last_accessed: Timestamp of when the credential was last accessed (default: None)
   :type last_accessed: datetime or str, optional
   :param metadata: Additional metadata for the credential
   :type metadata: dict, optional

Attributes
---------

.. py:attribute:: Credential.name

   The name of the credential (string).

.. py:attribute:: Credential.value

   The value of the credential (string).

.. py:attribute:: Credential.created_at

   Datetime when the credential was created.

.. py:attribute:: Credential.updated_at

   Datetime when the credential was last updated.

.. py:attribute:: Credential.last_accessed

   Datetime when the credential was last accessed (or None).

.. py:attribute:: Credential.metadata

   Dictionary of additional metadata associated with the credential.

Methods
------

.. py:method:: Credential.to_dict()

   Convert the credential to a dictionary for serialization.
   
   :returns: Dictionary representation of the credential
   :rtype: dict

.. py:classmethod:: Credential.from_dict(data)

   Create a credential from a dictionary.
   
   :param data: Dictionary containing credential data
   :type data: dict
   :returns: New credential object
   :rtype: Credential
   :raises ValidationError: If required fields are missing or invalid

.. py:method:: Credential.update_value(value)

   Update the credential value and update timestamp.
   
   :param value: New value for the credential
   :type value: str

.. py:method:: Credential.update_metadata(metadata)

   Update or replace the credential metadata.
   
   :param metadata: New metadata to set (replaces existing)
   :type metadata: dict

.. py:method:: Credential.update_last_accessed()

   Update the last accessed timestamp to the current time.

.. py:method:: Credential.is_expired(days=None)

   Check if the credential has expired based on creation date or 'expiry' in metadata.
   
   :param days: Number of days after which the credential is considered expired
   :type days: int, optional
   :returns: Whether the credential is expired
   :rtype: bool

.. py:method:: Credential.to_json()

   Convert the credential to a JSON string.
   
   :returns: JSON representation of the credential
   :rtype: str

.. py:classmethod:: Credential.from_json(json_string)

   Create a credential from a JSON string.
   
   :param json_string: JSON string containing credential data
   :type json_string: str
   :returns: New credential object
   :rtype: Credential

String Representation
-------------------

When printed, the ``Credential`` class will show a masked version of the value for security:

.. code-block:: python

    >>> credential = Credential("api_key", "sk-12345abcde")
    >>> print(credential)
    Credential(name='api_key', value='sk-*********')

Accessing Metadata
---------------

The metadata is a dictionary that can contain any key-value pairs:

.. code-block:: python

    >>> credential = Credential(
    ...     "api_key", 
    ...     "sk-12345abcde",
    ...     metadata={
    ...         "service": "OpenAI", 
    ...         "env": "production",
    ...         "expiry": "2023-12-31"
    ...     }
    ... )
    >>> credential.metadata["service"]
    'OpenAI'
    >>> credential.metadata["expiry"]
    '2023-12-31'

Example Usage
-----------

.. code-block:: python

    from llamavault import Credential
    from datetime import datetime, timedelta
    
    # Create a credential
    credential = Credential(
        name="database_password",
        value="secure-db-password-123",
        metadata={
            "service": "PostgreSQL",
            "environment": "development",
            "expiry": (datetime.now() + timedelta(days=90)).isoformat()
        }
    )
    
    # Convert to dictionary
    data = credential.to_dict()
    
    # Check if expired
    if credential.is_expired(days=30):
        print("This credential will expire in less than 30 days!")
    
    # Update value
    credential.update_value("new-secure-password-456")
    
    # Update metadata
    credential.metadata["username"] = "admin"
    
    # Track access time
    credential.update_last_accessed() 