#!/usr/bin/env python3
"""
Setup Admin User for UNGA Analysis App
Creates the admin user islam50@un.org with password OSAAKing!
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt

def setup_admin_user():
    """Setup the admin user in the database."""
    DB_PATH = "user_auth.db"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                title TEXT NOT NULL,
                office TEXT NOT NULL,
                purpose TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                approved_by TEXT,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                password_hash TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_duration INTEGER,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ("islam50@un.org",))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print("✅ Admin user already exists")
            # Update admin user to approved status
            cursor.execute("""
                UPDATE users 
                SET status = 'approved', approved_at = ?, approved_by = 'system'
                WHERE email = ?
            """, (datetime.now().isoformat(), "islam50@un.org"))
            print("✅ Admin user status updated to approved")
        else:
            # Create admin user
            admin_id = "admin_" + secrets.token_urlsafe(16)
            password_hash = hash_password("OSAAKing!")
            
            cursor.execute("""
                INSERT INTO users (id, email, full_name, title, office, purpose, status, password_hash, approved_at, approved_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                admin_id,
                "islam50@un.org",
                "Mafizul Islam",
                "Senior Data Analyst",
                "Office of the Special Adviser on Africa",
                "System administrator for UNGA Analysis Platform",
                "approved",
                password_hash,
                datetime.now().isoformat(),
                "system"
            ))
            print("✅ Admin user created successfully")
        
        # Set admin password in settings
        admin_password_hash = hash_password("OSAAKing!")
        cursor.execute("""
            INSERT OR REPLACE INTO admin_settings (key, value) 
            VALUES (?, ?)
        """, ("admin_password", admin_password_hash))
        
        conn.commit()
        conn.close()
        
        print("✅ Admin setup completed successfully!")
        print("📧 Email: islam50@un.org")
        print("🔑 Password: OSAAKing!")
        print("🛡️ Status: Approved")
        
    except Exception as e:
        print(f"❌ Error setting up admin user: {e}")

if __name__ == "__main__":
    setup_admin_user()
