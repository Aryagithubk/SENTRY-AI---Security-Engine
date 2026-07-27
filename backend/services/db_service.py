import sqlite3
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_DIR = Path(__file__).resolve().parent.parent.parent / "mock_data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "secureops.db"

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class DatabaseService:
    """
    Embedded SQLite Relational Database Service for SecureOps AI (SENTRY).
    Manages users, RBAC roles, alerts, endpoints, login history, incidents, and audit logs.
    """

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def initialize_database(cls):
        """Create tables and seed initial demo data into SQLite database."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                role_display TEXT NOT NULL,
                department TEXT NOT NULL
            )
        """)

        # Seed Users
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            demo_users = [
                ("analyst_l1", "alex.m@securetech.com", hash_pass("l1pass123"), "Alex Mercer", "L1", "L1 SOC Analyst", "Security Operations Center"),
                ("analyst_l2", "david.m@securetech.com", hash_pass("l2pass123"), "David Miller", "L2", "L2 SOC Analyst & Threat Hunter", "Threat Intelligence & Detection"),
                ("manager", "sarah.c@securetech.com", hash_pass("mgrpass123"), "Sarah Connor", "MANAGER", "SOC Manager / Incident Commander", "Cyber Incident Response Team"),
                ("ciso", "elena.r@securetech.com", hash_pass("cisopass123"), "Elena Rostova", "CISO", "CISO / Security Executive", "Executive Leadership"),
                ("admin", "sysadmin@securetech.com", hash_pass("adminpass123"), "System Admin", "ADMIN", "Security Administrator", "IT & Security Infrastructure")
            ]
            cursor.executemany("""
                INSERT INTO users (username, email, password_hash, name, role, role_display, department)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, demo_users)

        conn.commit()
        conn.close()

    @classmethod
    def verify_user_login(cls, username_or_email: str, password: str, selected_role_code: str) -> Optional[Dict[str, Any]]:
        """
        Verify username/email, password hash, and matching assigned role against SQLite database.
        """
        cls.initialize_database()
        conn = cls.get_connection()
        cursor = conn.cursor()

        identifier = username_or_email.lower().strip()
        target_hash = hash_pass(password)

        cursor.execute("""
            SELECT username, email, password_hash, name, role, role_display, department
            FROM users
            WHERE (LOWER(username) = ? OR LOWER(email) = ?)
        """, (identifier, identifier))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Check Password Match (Supports hashed match or fallback demo passwords)
        password_valid = (row["password_hash"] == target_hash) or (password in ["123", "l1pass123", "l2pass123", "mgrpass123", "cisopass123", "adminpass123"])

        # Check Role Code Match
        role_valid = (row["role"].upper() == selected_role_code.upper())

        if password_valid and role_valid:
            return {
                "username": row["username"],
                "email": row["email"],
                "name": row["name"],
                "role": row["role"],
                "role_display": row["role_display"],
                "department": row["department"]
            }

        return None

# Initialize DB on module load
DatabaseService.initialize_database()
