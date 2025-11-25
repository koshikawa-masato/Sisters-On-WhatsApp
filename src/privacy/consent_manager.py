"""
Consent Manager - Track and manage user consent for data processing.

Supports GDPR, CCPA, Taiwan PDPA, China PIPL requirements.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum

import psycopg2
from psycopg2.extras import RealDictCursor

from .policy_messages import PrivacyPolicyMessages, Region

logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """User consent status."""
    PENDING = "pending"       # Not yet responded
    GRANTED = "granted"       # User agreed
    DECLINED = "declined"     # User declined
    WITHDRAWN = "withdrawn"   # User withdrew consent (deleted data)


class ConsentManager:
    """Manage user consent for data processing."""

    def __init__(self):
        self.connection_params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "user": os.getenv("POSTGRES_USER", "sisters"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "database": os.getenv("POSTGRES_DB", "sisters_on_whatsapp"),
        }

    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.connection_params, connect_timeout=10)

    def ensure_table_exists(self):
        """Create user_consents table if not exists."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_consents (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(50) UNIQUE NOT NULL,
                region VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                language VARCHAR(10) DEFAULT 'en',
                consent_version VARCHAR(20) DEFAULT '1.0',
                ip_country VARCHAR(50),

                -- Timestamps for audit trail
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                consent_given_at TIMESTAMP,
                consent_withdrawn_at TIMESTAMP,
                last_reminded_at TIMESTAMP,

                -- Audit fields
                consent_method VARCHAR(50) DEFAULT 'whatsapp_message',
                policy_url_shown TEXT,

                -- Data processing records
                data_deletion_requested_at TIMESTAMP,
                data_deleted_at TIMESTAMP,
                data_export_requested_at TIMESTAMP,

                -- Metadata
                metadata JSONB DEFAULT '{}'
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consents_phone ON user_consents(phone_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consents_status ON user_consents(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consents_region ON user_consents(region)")

        conn.commit()
        conn.close()
        logger.info("user_consents table ready")

    def get_user_consent(self, phone_number: str) -> Optional[Dict]:
        """Get user's consent record."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM user_consents WHERE phone_number = %s
        """, (phone_number,))

        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def create_pending_consent(self, phone_number: str, language: str = "en") -> Dict:
        """Create a pending consent record for new user."""
        region = PrivacyPolicyMessages.detect_region(phone_number)
        policy_url = PrivacyPolicyMessages.POLICY_URLS.get(region, PrivacyPolicyMessages.POLICY_URLS[Region.DEFAULT])

        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO user_consents (
                phone_number, region, status, language, policy_url_shown, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (phone_number) DO UPDATE SET
                last_reminded_at = CURRENT_TIMESTAMP
            RETURNING *
        """, (
            phone_number,
            region.value,
            ConsentStatus.PENDING.value,
            language,
            policy_url,
            datetime.now()
        ))

        result = cursor.fetchone()
        conn.commit()
        conn.close()

        logger.info(f"Created pending consent for {phone_number[:6]}... (region: {region.value})")
        return dict(result)

    def grant_consent(self, phone_number: str) -> bool:
        """Record user's consent."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_consents
            SET status = %s,
                consent_given_at = CURRENT_TIMESTAMP,
                consent_method = 'whatsapp_message'
            WHERE phone_number = %s
            RETURNING id
        """, (ConsentStatus.GRANTED.value, phone_number))

        result = cursor.fetchone()
        conn.commit()
        conn.close()

        if result:
            logger.info(f"Consent granted for {phone_number[:6]}...")
            return True
        return False

    def decline_consent(self, phone_number: str) -> bool:
        """Record user's decline."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_consents
            SET status = %s,
                consent_withdrawn_at = CURRENT_TIMESTAMP
            WHERE phone_number = %s
            RETURNING id
        """, (ConsentStatus.DECLINED.value, phone_number))

        result = cursor.fetchone()
        conn.commit()
        conn.close()

        if result:
            logger.info(f"Consent declined for {phone_number[:6]}...")
            return True
        return False

    def withdraw_consent(self, phone_number: str) -> bool:
        """Record consent withdrawal (for data deletion)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_consents
            SET status = %s,
                consent_withdrawn_at = CURRENT_TIMESTAMP,
                data_deletion_requested_at = CURRENT_TIMESTAMP
            WHERE phone_number = %s
            RETURNING id
        """, (ConsentStatus.WITHDRAWN.value, phone_number))

        result = cursor.fetchone()
        conn.commit()
        conn.close()

        if result:
            logger.info(f"Consent withdrawn for {phone_number[:6]}...")
            return True
        return False

    def has_valid_consent(self, phone_number: str) -> bool:
        """Check if user has valid consent."""
        consent = self.get_user_consent(phone_number)

        if not consent:
            return False

        return consent["status"] == ConsentStatus.GRANTED.value

    def needs_consent(self, phone_number: str) -> bool:
        """Check if user needs to provide consent."""
        consent = self.get_user_consent(phone_number)

        if not consent:
            return True

        return consent["status"] in [ConsentStatus.PENDING.value, ConsentStatus.DECLINED.value]

    def record_data_deletion(self, phone_number: str) -> bool:
        """Record that user's data has been deleted."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_consents
            SET data_deleted_at = CURRENT_TIMESTAMP,
                metadata = metadata || '{"deletion_completed": true}'::jsonb
            WHERE phone_number = %s
            RETURNING id
        """, (phone_number,))

        result = cursor.fetchone()
        conn.commit()
        conn.close()

        return result is not None

    def record_data_export_request(self, phone_number: str) -> bool:
        """Record data export request (GDPR right to portability)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_consents
            SET data_export_requested_at = CURRENT_TIMESTAMP
            WHERE phone_number = %s
            RETURNING id
        """, (phone_number,))

        result = cursor.fetchone()
        conn.commit()
        conn.close()

        return result is not None

    def get_users_pending_deletion(self, days_inactive: int = 90) -> List[str]:
        """Get users who should have their data deleted (retention policy)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT uc.phone_number
            FROM user_consents uc
            LEFT JOIN (
                SELECT phone_number, MAX(timestamp) as last_message
                FROM conversation_history
                GROUP BY phone_number
            ) ch ON uc.phone_number = ch.phone_number
            WHERE uc.status = 'granted'
              AND (ch.last_message IS NULL OR ch.last_message < NOW() - INTERVAL '%s days')
              AND uc.data_deleted_at IS NULL
        """, (days_inactive,))

        results = cursor.fetchall()
        conn.close()

        return [r[0] for r in results]

    def get_consent_statistics(self) -> Dict:
        """Get consent statistics for compliance reporting."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                region,
                status,
                COUNT(*) as count
            FROM user_consents
            GROUP BY region, status
            ORDER BY region, status
        """)

        results = cursor.fetchall()
        conn.close()

        stats = {}
        for row in results:
            region = row["region"]
            if region not in stats:
                stats[region] = {}
            stats[region][row["status"]] = row["count"]

        return stats
