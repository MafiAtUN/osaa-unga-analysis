"""
User Authentication System
Handles user registration, login, admin approval, and usage tracking
"""

import os
import hashlib
import secrets
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path


@dataclass
class User:
    """User data structure."""
    id: str
    email: str
    full_name: str
    title: str
    office: str
    purpose: str
    status: str  # 'pending', 'approved', 'denied'
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    last_login: Optional[datetime] = None
    login_count: int = 0


class UserAuthManager:
    """Manages user authentication, registration, and admin functions."""
    
    def __init__(self, db_path: str = "user_auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user authentication database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
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
        
        # Usage logs table
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
        
        # Admin settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Initialize admin password if not exists
        cursor.execute("SELECT value FROM admin_settings WHERE key = 'admin_password'")
        if not cursor.fetchone():
            # Get admin password from environment variable
            default_admin_password = os.getenv('ADMIN_PASSWORD', 'OSAAKing!')  # Default for development only
            admin_hash = self._hash_password(default_admin_password)
            cursor.execute("INSERT INTO admin_settings (key, value) VALUES (?, ?)", 
                         ("admin_password", admin_hash))
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            hash_part, salt = hashed.split(":")
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_part
        except:
            return False
    
    def register_user(self, email: str, password: str, full_name: str, 
                     title: str, office: str, purpose: str) -> Dict[str, Any]:
        """Register a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {"success": False, "message": "Email already registered"}
            
            # Create new user
            user_id = secrets.token_urlsafe(16)
            password_hash = self._hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (id, email, full_name, title, office, purpose, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, email, full_name, title, office, purpose, password_hash))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Registration successful. Awaiting admin approval."}
            
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user login."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, full_name, title, office, purpose, status, 
                       created_at, approved_at, approved_by, last_login, login_count, password_hash
                FROM users WHERE email = ?
            """, (email,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, email, full_name, title, office, purpose, status, created_at, approved_at, approved_by, last_login, login_count, password_hash = row
            
            if not self._verify_password(password, password_hash):
                return None
            
            if status != 'approved':
                return None
            
            # Update login info
            cursor.execute("""
                UPDATE users SET last_login = ?, login_count = login_count + 1
                WHERE id = ?
            """, (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            
            return User(
                id=user_id,
                email=email,
                full_name=full_name,
                title=title,
                office=office,
                purpose=purpose,
                status=status,
                created_at=datetime.fromisoformat(created_at),
                approved_at=datetime.fromisoformat(approved_at) if approved_at else None,
                approved_by=approved_by,
                last_login=datetime.now(),
                login_count=login_count + 1
            )
            
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None
    
    def get_pending_users(self) -> List[User]:
        """Get all pending user registrations."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, full_name, title, office, purpose, status, 
                       created_at, approved_at, approved_by, last_login, login_count
                FROM users WHERE status = 'pending'
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                user_id, email, full_name, title, office, purpose, status, created_at, approved_at, approved_by, last_login, login_count = row
                users.append(User(
                    id=user_id,
                    email=email,
                    full_name=full_name,
                    title=title,
                    office=office,
                    purpose=purpose,
                    status=status,
                    created_at=datetime.fromisoformat(created_at),
                    approved_at=datetime.fromisoformat(approved_at) if approved_at else None,
                    approved_by=approved_by,
                    last_login=datetime.fromisoformat(last_login) if last_login else None,
                    login_count=login_count
                ))
            
            conn.close()
            return users
            
        except Exception as e:
            st.error(f"Error fetching pending users: {e}")
            return []
    
    def approve_user(self, user_id: str, admin_user: str) -> bool:
        """Approve a user registration."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET status = 'approved', approved_at = ?, approved_by = ?
                WHERE id = ?
            """, (datetime.now(), admin_user, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error approving user: {e}")
            return False
    
    def deny_user(self, user_id: str, admin_user: str) -> bool:
        """Deny a user registration."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET status = 'denied', approved_at = ?, approved_by = ?
                WHERE id = ?
            """, (datetime.now(), admin_user, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error denying user: {e}")
            return False
    
    def log_user_activity(self, user_id: str, action: str, session_duration: int = 0, details: str = ""):
        """Log user activity."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO usage_logs (user_id, action, session_duration, details)
                VALUES (?, ?, ?, ?)
            """, (user_id, action, session_duration, details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error logging activity: {e}")
    
    def get_user_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total sessions
            cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE user_id = ? AND action = 'login'", (user_id,))
            total_sessions = cursor.fetchone()[0]
            
            # Get total time
            cursor.execute("SELECT SUM(session_duration) FROM usage_logs WHERE user_id = ?", (user_id,))
            total_time = cursor.fetchone()[0] or 0
            
            # Get last login
            cursor.execute("SELECT MAX(timestamp) FROM usage_logs WHERE user_id = ? AND action = 'login'", (user_id,))
            last_login = cursor.fetchone()[0]
            
            # Get recent activities
            cursor.execute("""
                SELECT action, timestamp, details FROM usage_logs 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            """, (user_id,))
            recent_activities = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_sessions': total_sessions,
                'total_time_minutes': total_time,
                'last_login': last_login,
                'recent_activities': recent_activities
            }
            
        except Exception as e:
            st.error(f"Error getting usage stats: {e}")
            return {}
    
    def get_all_users(self) -> List[User]:
        """Get all users for admin view."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, full_name, title, office, purpose, status, 
                       created_at, approved_at, approved_by, last_login, login_count
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                user_id, email, full_name, title, office, purpose, status, created_at, approved_at, approved_by, last_login, login_count = row
                users.append(User(
                    id=user_id,
                    email=email,
                    full_name=full_name,
                    title=title,
                    office=office,
                    purpose=purpose,
                    status=status,
                    created_at=datetime.fromisoformat(created_at),
                    approved_at=datetime.fromisoformat(approved_at) if approved_at else None,
                    approved_by=approved_by,
                    last_login=datetime.fromisoformat(last_login) if last_login else None,
                    login_count=login_count
                ))
            
            conn.close()
            return users
            
        except Exception as e:
            st.error(f"Error fetching users: {e}")
            return []
    
    def verify_admin_password(self, password: str) -> bool:
        """Verify admin password."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM admin_settings WHERE key = 'admin_password'")
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return self._verify_password(password, result[0])
            return False
            
        except Exception as e:
            st.error(f"Error verifying admin password: {e}")
            return False


# Global instance
user_auth_manager = UserAuthManager()