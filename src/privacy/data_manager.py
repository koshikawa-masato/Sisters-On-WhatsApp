"""
Data Manager - Handle data deletion and retention policies.

Implements GDPR Article 17 (Right to Erasure), CCPA deletion rights,
Taiwan PDPA, and China PIPL requirements.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor

from .consent_manager import ConsentManager, ConsentStatus

logger = logging.getLogger(__name__)


class DataManager:
    """Manage user data lifecycle - deletion, export, retention."""

    # Default retention period (days)
    DEFAULT_RETENTION_DAYS = 90

    def __init__(self):
        self.connection_params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "user": os.getenv("POSTGRES_USER", "sisters"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "database": os.getenv("POSTGRES_DB", "sisters_on_whatsapp"),
        }
        self.consent_manager = ConsentManager()
        self.retention_days = int(os.getenv("DATA_RETENTION_DAYS", self.DEFAULT_RETENTION_DAYS))

    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.connection_params, connect_timeout=10)

    def delete_user_data(self, phone_number: str, reason: str = "user_request") -> Dict:
        """
        Delete all user data (GDPR Article 17 - Right to Erasure).

        Args:
            phone_number: User's phone number
            reason: Reason for deletion (user_request, retention_policy, etc.)

        Returns:
            Summary of deleted data
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        deleted = {
            "phone_number": phone_number[:6] + "...",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "deleted_records": {}
        }

        try:
            # 1. Delete conversation history
            cursor.execute("""
                DELETE FROM conversation_history
                WHERE phone_number = %s
                RETURNING id
            """, (phone_number,))
            deleted["deleted_records"]["conversation_history"] = cursor.rowcount

            # 2. Delete user memories
            cursor.execute("""
                DELETE FROM user_memories
                WHERE phone_number = %s
                RETURNING id
            """, (phone_number,))
            deleted["deleted_records"]["user_memories"] = cursor.rowcount

            # 3. Delete user sessions
            cursor.execute("""
                DELETE FROM user_sessions
                WHERE phone_number = %s
                RETURNING id
            """, (phone_number,))
            deleted["deleted_records"]["user_sessions"] = cursor.rowcount

            # 4. Update consent record (don't delete - keep for audit)
            cursor.execute("""
                UPDATE user_consents
                SET status = %s,
                    consent_withdrawn_at = CURRENT_TIMESTAMP,
                    data_deleted_at = CURRENT_TIMESTAMP,
                    metadata = metadata || %s::jsonb
                WHERE phone_number = %s
            """, (
                ConsentStatus.WITHDRAWN.value,
                json.dumps({"deletion_reason": reason, "deleted_at": datetime.now().isoformat()}),
                phone_number
            ))
            deleted["deleted_records"]["consent_updated"] = cursor.rowcount > 0

            conn.commit()
            logger.info(f"Deleted data for {phone_number[:6]}...: {deleted['deleted_records']}")

        except Exception as e:
            conn.rollback()
            logger.error(f"Data deletion failed for {phone_number[:6]}...: {e}")
            raise

        finally:
            conn.close()

        return deleted

    def export_user_data(self, phone_number: str) -> Dict:
        """
        Export all user data (GDPR Article 20 - Right to Data Portability).

        Args:
            phone_number: User's phone number

        Returns:
            All user data in portable format
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        export_data = {
            "export_date": datetime.now().isoformat(),
            "phone_number": phone_number,
            "data": {}
        }

        try:
            # 1. Consent record
            cursor.execute("""
                SELECT region, status, language, consent_given_at, created_at
                FROM user_consents
                WHERE phone_number = %s
            """, (phone_number,))
            consent = cursor.fetchone()
            export_data["data"]["consent"] = dict(consent) if consent else None

            # 2. Conversation history
            cursor.execute("""
                SELECT character, role, content, timestamp
                FROM conversation_history
                WHERE phone_number = %s
                ORDER BY timestamp ASC
            """, (phone_number,))
            conversations = cursor.fetchall()
            export_data["data"]["conversations"] = [dict(c) for c in conversations]

            # 3. User memories
            cursor.execute("""
                SELECT profile, preferences, facts, topics_discussed,
                       personality_notes, language, last_updated
                FROM user_memories
                WHERE phone_number = %s
            """, (phone_number,))
            memory = cursor.fetchone()
            export_data["data"]["memory"] = dict(memory) if memory else None

            # 4. Session data
            cursor.execute("""
                SELECT current_character, language, last_activity
                FROM user_sessions
                WHERE phone_number = %s
            """, (phone_number,))
            session = cursor.fetchone()
            export_data["data"]["session"] = dict(session) if session else None

            # Record export request
            self.consent_manager.record_data_export_request(phone_number)

            logger.info(f"Exported data for {phone_number[:6]}...")

        finally:
            conn.close()

        return export_data

    def apply_retention_policy(self, dry_run: bool = False) -> Dict:
        """
        Apply data retention policy - delete data older than retention period.

        Args:
            dry_run: If True, only report what would be deleted

        Returns:
            Summary of affected users
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        result = {
            "retention_days": self.retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "dry_run": dry_run,
            "users_affected": []
        }

        try:
            # Find users with no activity since cutoff
            cursor.execute("""
                SELECT uc.phone_number, uc.region,
                       MAX(ch.timestamp) as last_activity
                FROM user_consents uc
                LEFT JOIN conversation_history ch ON uc.phone_number = ch.phone_number
                WHERE uc.status = 'granted'
                  AND uc.data_deleted_at IS NULL
                GROUP BY uc.phone_number, uc.region
                HAVING MAX(ch.timestamp) IS NULL
                   OR MAX(ch.timestamp) < %s
            """, (cutoff_date,))

            users = cursor.fetchall()

            for user in users:
                user_info = {
                    "phone_number": user["phone_number"][:6] + "...",
                    "region": user["region"],
                    "last_activity": user["last_activity"].isoformat() if user["last_activity"] else None
                }

                if not dry_run:
                    self.delete_user_data(user["phone_number"], reason="retention_policy")
                    user_info["deleted"] = True

                result["users_affected"].append(user_info)

            logger.info(f"Retention policy: {len(users)} users affected (dry_run={dry_run})")

        finally:
            conn.close()

        return result

    def get_data_statistics(self) -> Dict:
        """Get data storage statistics for compliance reporting."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        stats = {}

        try:
            # Total users by region
            cursor.execute("""
                SELECT region, COUNT(*) as count
                FROM user_consents
                WHERE status = 'granted'
                GROUP BY region
            """)
            stats["users_by_region"] = {row["region"]: row["count"] for row in cursor.fetchall()}

            # Total conversations
            cursor.execute("SELECT COUNT(*) as count FROM conversation_history")
            stats["total_conversations"] = cursor.fetchone()["count"]

            # Data deletion requests
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM user_consents
                WHERE data_deletion_requested_at IS NOT NULL
            """)
            stats["deletion_requests"] = cursor.fetchone()["count"]

            # Data export requests
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM user_consents
                WHERE data_export_requested_at IS NOT NULL
            """)
            stats["export_requests"] = cursor.fetchone()["count"]

            # Users pending deletion (retention policy)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM user_consents uc
                LEFT JOIN (
                    SELECT phone_number, MAX(timestamp) as last_msg
                    FROM conversation_history
                    GROUP BY phone_number
                ) ch ON uc.phone_number = ch.phone_number
                WHERE uc.status = 'granted'
                  AND (ch.last_msg IS NULL OR ch.last_msg < NOW() - INTERVAL '%s days')
            """, (self.retention_days,))
            stats["pending_retention_deletion"] = cursor.fetchone()["count"]

        finally:
            conn.close()

        return stats


class RetentionPolicyCron:
    """Cron job for applying retention policy."""

    def __init__(self):
        self.data_manager = DataManager()

    def run(self, dry_run: bool = False):
        """Run retention policy cleanup."""
        logger.info("=" * 50)
        logger.info("Data Retention Policy - Sisters-On-WhatsApp")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("=" * 50)

        result = self.data_manager.apply_retention_policy(dry_run=dry_run)

        logger.info(f"Retention period: {result['retention_days']} days")
        logger.info(f"Cutoff date: {result['cutoff_date']}")
        logger.info(f"Users affected: {len(result['users_affected'])}")

        if result["users_affected"]:
            for user in result["users_affected"]:
                logger.info(f"  - {user['phone_number']} (region: {user['region']})")

        logger.info("=" * 50)

        return result
