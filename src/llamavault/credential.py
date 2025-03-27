"""
Credential model for the vault
"""

from datetime import datetime
from typing import Dict, Any, Optional, ClassVar, Type
import json

class Credential:
    """
    Represents a stored credential with metadata
    
    Attributes:
        name: The name/identifier of the credential
        value: The actual credential value (API key, token, etc.)
        created_at: When the credential was first created
        updated_at: When the credential was last updated
        last_accessed: When the credential was last accessed (None if never)
        metadata: Additional information about the credential
    """
    
    def __init__(
        self,
        name: str,
        value: str,
        created_at: datetime,
        updated_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        last_accessed: Optional[datetime] = None
    ) -> None:
        """
        Initialize a credential
        
        Args:
            name: Name/identifier of the credential
            value: The credential value
            created_at: Creation timestamp
            updated_at: Last update timestamp
            metadata: Additional metadata (optional)
            last_accessed: Last access timestamp (optional)
        """
        self.name = name
        self.value = value
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_accessed = last_accessed
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert credential to dictionary for serialization
        
        Returns:
            Dictionary representation of the credential
        """
        return {
            "name": self.name,
            "value": self.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Credential':
        """
        Create a credential from a dictionary
        
        Args:
            data: Dictionary containing credential data
            
        Returns:
            Credential instance
        """
        # Parse ISO format dates if they exist
        created_at = parse_datetime(data.get("created_at"))
        updated_at = parse_datetime(data.get("updated_at"))
        last_accessed = parse_datetime(data.get("last_accessed"))
        
        return cls(
            name=data["name"],
            value=data["value"],
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
            last_accessed=last_accessed,
            metadata=data.get("metadata", {})
        )
    
    def __repr__(self) -> str:
        """String representation of the credential (value is masked)"""
        return (
            f"Credential(name='{self.name}', "
            f"value='***', "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}, "
            f"last_accessed={self.last_accessed})"
        )
    
    def is_expired(self, expiry_days: int) -> bool:
        """
        Check if the credential has expired
        
        Args:
            expiry_days: Number of days after which credentials expire
            
        Returns:
            True if the credential has expired, False otherwise
        """
        if expiry_days <= 0:
            return False
            
        now = datetime.now()
        if self.updated_at:
            days_since_update = (now - self.updated_at).days
            return days_since_update > expiry_days
            
        return False
    
    def update_value(self, value: str) -> None:
        """
        Update the credential value
        
        Args:
            value: New credential value
        """
        self.value = value
        self.updated_at = datetime.now()
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Update the credential metadata
        
        Args:
            metadata: New metadata (merges with existing)
        """
        self.metadata.update(metadata)
        self.updated_at = datetime.now()
    
    def to_json(self) -> str:
        """
        Convert credential to JSON string
        
        Returns:
            JSON representation of the credential
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Credential':
        """
        Create a credential from JSON string
        
        Args:
            json_str: JSON string containing credential data
            
        Returns:
            Credential instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO format datetime string
    
    Args:
        dt_str: ISO format datetime string or None
        
    Returns:
        datetime object or None if input is None
    """
    if not dt_str:
        return None
        
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        # Fall back to datetime.now() if parsing fails
        return datetime.now() 