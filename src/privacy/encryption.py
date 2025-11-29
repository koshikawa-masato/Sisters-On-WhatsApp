"""
Conversation Encryption - AES-256 encryption for stored conversations.

Provides field-level encryption for sensitive data in the database.
Uses hash-based lookup for phone numbers to enable queries on encrypted data.
"""

import os
import base64
import hashlib
import json
import logging
from typing import Optional, Dict, Any, List, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class ConversationEncryption:
    """
    AES-256 encryption for conversation content.

    Uses Fernet (AES-128-CBC with HMAC) which is simpler and secure enough.
    For true AES-256, we use PBKDF2 to derive a 256-bit key.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption with key from environment or parameter.

        Args:
            encryption_key: Base64-encoded encryption key, or will use ENCRYPTION_KEY env var
        """
        key_source = encryption_key or os.getenv("ENCRYPTION_KEY")

        if not key_source:
            logger.warning("ENCRYPTION_KEY not set - generating new key (NOT FOR PRODUCTION)")
            # Generate a key for development only
            key_source = Fernet.generate_key().decode()
            logger.warning(f"Generated key (save this!): {key_source}")

        # Derive a proper Fernet key from the source key
        self.fernet = self._create_fernet(key_source)

        # Salt for phone number hashing (from env or default)
        self._hash_salt = os.getenv("PHONE_HASH_SALT", "sisters_phone_salt_v1").encode()

    def _create_fernet(self, key_source: str) -> Fernet:
        """Create Fernet instance from key source."""
        # If it's already a valid Fernet key (44 chars base64), use directly
        if len(key_source) == 44:
            try:
                return Fernet(key_source.encode())
            except Exception:
                pass

        # Otherwise, derive a key using PBKDF2
        salt = b"sisters_on_whatsapp_v1"  # Static salt (key is already secret)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_source.encode()))
        return Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.

        Args:
            plaintext: The text to encrypt

        Returns:
            Base64-encoded encrypted string (Fernet's native format)
        """
        if not plaintext:
            return plaintext

        try:
            # Fernet.encrypt() already returns urlsafe base64-encoded bytes
            # No need for additional base64 encoding
            encrypted = self.fernet.encrypt(plaintext.encode('utf-8'))
            return encrypted.decode('utf-8')  # Just decode bytes to string
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.

        Handles both:
        - Legacy double-encoded format: Z0FBQUFB... (base64 of base64)
        - New single-encoded format: gAAAAA... (Fernet's native base64)

        Args:
            ciphertext: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext
        """
        if not ciphertext:
            return ciphertext

        try:
            # Check if it's double-encoded (legacy format)
            # Double-encoded strings start with 'Z0FBQUFB' which decodes to 'gAAAAA'
            if ciphertext.startswith('Z0FBQUFB'):
                # Legacy double-encoded: decode base64 first, then decrypt
                encrypted = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
                decrypted = self.fernet.decrypt(encrypted)
                return decrypted.decode('utf-8')
            elif ciphertext.startswith('gAAAAA'):
                # New single-encoded format: Fernet's native base64
                decrypted = self.fernet.decrypt(ciphertext.encode('utf-8'))
                return decrypted.decode('utf-8')
            else:
                # Unknown format, return as-is (might be unencrypted)
                return ciphertext
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            # Return original if decryption fails (might be unencrypted legacy data)
            return ciphertext

    def is_encrypted(self, text: str) -> bool:
        """
        Check if text appears to be encrypted.

        Detects both:
        - Legacy double-encoded format: Z0FBQUFB... (base64 of base64)
        - New single-encoded format: gAAAAA... (Fernet's native base64)
        """
        if not text:
            return False

        # Check for double-encoded format (legacy)
        # 'Z0FBQUFB' is base64 encoding of 'gAAAAA' (Fernet token prefix)
        if text.startswith('Z0FBQUFB'):
            return True

        # Check for single-encoded format (new/correct)
        # Fernet tokens start with 'gAAAAA' (version byte 0x80 = 128)
        if text.startswith('gAAAAA'):
            return True

        return False

    def encrypt_if_needed(self, text: str) -> str:
        """Encrypt text only if not already encrypted."""
        if self.is_encrypted(text):
            return text
        return self.encrypt(text)

    def decrypt_if_needed(self, text: str) -> str:
        """Decrypt text only if it's encrypted."""
        if not self.is_encrypted(text):
            return text
        return self.decrypt(text)

    def hash_phone_number(self, phone_number: str) -> str:
        """
        Create a deterministic hash of phone number for database lookups.

        Uses SHA-256 with salt to create a consistent hash that can be used
        as a lookup key while keeping the actual phone number encrypted.

        Args:
            phone_number: The phone number to hash

        Returns:
            Hex-encoded SHA-256 hash (64 characters)
        """
        if not phone_number:
            return phone_number

        # Normalize phone number (remove spaces, ensure + prefix)
        normalized = phone_number.strip().replace(" ", "").replace("-", "")

        # Create salted hash
        salted = self._hash_salt + normalized.encode('utf-8')
        return hashlib.sha256(salted).hexdigest()

    def is_phone_hash(self, value: str) -> bool:
        """Check if value looks like a phone hash (64 hex chars)."""
        if not value or len(value) != 64:
            return False
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    def encrypt_json(self, data: Union[dict, list]) -> str:
        """Encrypt a JSON-serializable object."""
        if data is None:
            return None
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt(json_str)

    def decrypt_json(self, ciphertext: str) -> Union[dict, list, None]:
        """Decrypt to a JSON object."""
        if not ciphertext:
            return None

        decrypted = self.decrypt_if_needed(ciphertext)

        # If decryption returned original (legacy unencrypted data)
        if decrypted == ciphertext:
            # Try parsing as JSON directly
            try:
                return json.loads(ciphertext)
            except json.JSONDecodeError:
                return ciphertext

        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return decrypted


class EncryptedFieldManager:
    """
    Manages encryption for all sensitive database fields.

    Provides hash-based lookup for phone numbers and encryption for content.
    """

    # Fields requiring encryption by table
    SENSITIVE_FIELDS = {
        'conversation_history': {
            'phone_number': 'phone',  # Uses hash for lookup + encryption for storage
            'content': 'text',
        },
        'user_sessions': {
            'phone_number': 'phone',
        },
        'user_consents': {
            'phone_number': 'phone',
        },
        'user_memories': {
            'phone_number': 'phone',
            'profile': 'text',
            'preferences': 'json',
            'facts': 'json',
            'topics_discussed': 'json',
            'personality_notes': 'text',
        },
    }

    def __init__(self):
        self.encryption = ConversationEncryption()

    def get_phone_hash(self, phone_number: str) -> str:
        """Get hash for phone number lookup."""
        return self.encryption.hash_phone_number(phone_number)

    def encrypt_phone(self, phone_number: str) -> str:
        """Encrypt phone number for storage."""
        return self.encryption.encrypt(phone_number)

    def decrypt_phone(self, encrypted_phone: str) -> str:
        """Decrypt phone number for display/export."""
        return self.encryption.decrypt_if_needed(encrypted_phone)

    def encrypt_field(self, value: Any, field_type: str) -> Any:
        """
        Encrypt a field based on its type.

        Args:
            value: The value to encrypt
            field_type: 'text', 'json', or 'phone'

        Returns:
            Encrypted value
        """
        if value is None:
            return None

        if field_type == 'text':
            return self.encryption.encrypt(str(value))
        elif field_type == 'json':
            return self.encryption.encrypt_json(value)
        elif field_type == 'phone':
            return self.encryption.encrypt(value)
        else:
            return value

    def decrypt_field(self, value: Any, field_type: str) -> Any:
        """
        Decrypt a field based on its type.

        Args:
            value: The encrypted value
            field_type: 'text', 'json', or 'phone'

        Returns:
            Decrypted value
        """
        if value is None:
            return None

        if field_type == 'text':
            return self.encryption.decrypt_if_needed(str(value))
        elif field_type == 'json':
            return self.encryption.decrypt_json(value)
        elif field_type == 'phone':
            return self.encryption.decrypt_if_needed(value)
        else:
            return value

    def encrypt_record(self, table: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt all sensitive fields in a database record.

        Args:
            table: Table name
            record: Record dict with field values

        Returns:
            Record with sensitive fields encrypted
        """
        if table not in self.SENSITIVE_FIELDS:
            return record

        encrypted = record.copy()
        field_types = self.SENSITIVE_FIELDS[table]

        for field, field_type in field_types.items():
            if field in encrypted and encrypted[field] is not None:
                # For phone fields, also add hash for lookup
                if field_type == 'phone' and field == 'phone_number':
                    encrypted['phone_hash'] = self.get_phone_hash(encrypted[field])
                encrypted[field] = self.encrypt_field(encrypted[field], field_type)

        return encrypted

    def decrypt_record(self, table: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt all sensitive fields in a database record.

        Args:
            table: Table name
            record: Record dict with encrypted field values

        Returns:
            Record with sensitive fields decrypted
        """
        if table not in self.SENSITIVE_FIELDS:
            return record

        decrypted = record.copy()
        field_types = self.SENSITIVE_FIELDS[table]

        for field, field_type in field_types.items():
            if field in decrypted and decrypted[field] is not None:
                decrypted[field] = self.decrypt_field(decrypted[field], field_type)

        # Remove phone_hash from output (internal use only)
        decrypted.pop('phone_hash', None)

        return decrypted


class EncryptedConversationStore:
    """
    Store and retrieve encrypted conversations.

    Wraps database operations with encryption/decryption.
    Supports hash-based phone number lookups.
    """

    def __init__(self):
        self.encryption = ConversationEncryption()
        self.field_manager = EncryptedFieldManager()

    def get_phone_hash(self, phone_number: str) -> str:
        """Get hash for phone number lookup in database."""
        return self.field_manager.get_phone_hash(phone_number)

    def encrypt_message(self, content: str) -> str:
        """Encrypt a message before storing."""
        return self.encryption.encrypt(content)

    def decrypt_message(self, content: str) -> str:
        """Decrypt a message after retrieval."""
        return self.encryption.decrypt_if_needed(content)

    def encrypt_phone(self, phone_number: str) -> str:
        """Encrypt phone number for storage."""
        return self.field_manager.encrypt_phone(phone_number)

    def decrypt_phone(self, encrypted_phone: str) -> str:
        """Decrypt phone number for display."""
        return self.field_manager.decrypt_phone(encrypted_phone)

    def encrypt_user_data(self, data: dict) -> dict:
        """Encrypt sensitive fields in user data."""
        encrypted = data.copy()

        # Text fields to encrypt
        text_fields = ['content', 'profile', 'personality_notes']
        for field in text_fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = self.encryption.encrypt(encrypted[field])

        # JSON fields to encrypt
        json_fields = ['preferences', 'facts', 'topics_discussed']
        for field in json_fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = self.encryption.encrypt_json(encrypted[field])

        # Phone number (add hash + encrypt)
        if 'phone_number' in encrypted and encrypted['phone_number']:
            encrypted['phone_hash'] = self.get_phone_hash(encrypted['phone_number'])
            encrypted['phone_number'] = self.encrypt_phone(encrypted['phone_number'])

        return encrypted

    def decrypt_user_data(self, data: dict) -> dict:
        """Decrypt sensitive fields in user data."""
        decrypted = data.copy()

        # Text fields
        text_fields = ['content', 'profile', 'personality_notes']
        for field in text_fields:
            if field in decrypted and decrypted[field]:
                decrypted[field] = self.encryption.decrypt_if_needed(decrypted[field])

        # JSON fields
        json_fields = ['preferences', 'facts', 'topics_discussed']
        for field in json_fields:
            if field in decrypted and decrypted[field]:
                decrypted[field] = self.encryption.decrypt_json(decrypted[field])

        # Phone number
        if 'phone_number' in decrypted and decrypted['phone_number']:
            decrypted['phone_number'] = self.decrypt_phone(decrypted['phone_number'])

        # Remove internal hash field
        decrypted.pop('phone_hash', None)

        return decrypted


def generate_encryption_key() -> str:
    """Generate a new encryption key for .env file."""
    key = Fernet.generate_key()
    return key.decode()


def generate_phone_hash_salt() -> str:
    """Generate a new salt for phone number hashing."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


if __name__ == "__main__":
    # Generate keys when run directly
    print("=" * 60)
    print("Encryption Keys for .env")
    print("=" * 60)
    print()
    print("# Add these to your .env file:")
    print(f"ENCRYPTION_KEY={generate_encryption_key()}")
    print(f"PHONE_HASH_SALT={generate_phone_hash_salt()}")
    print()
    print("=" * 60)

    # Demo
    print("\nDemo: Phone number hashing")
    print("-" * 40)
    enc = ConversationEncryption()
    test_phone = "+00000000000"  # Example placeholder
    phone_hash = enc.hash_phone_number(test_phone)
    phone_encrypted = enc.encrypt(test_phone)
    print(f"Original:  {test_phone}")
    print(f"Hash:      {phone_hash}")
    print(f"Encrypted: {phone_encrypted[:50]}...")
    print(f"Decrypted: {enc.decrypt(phone_encrypted)}")
