#!/usr/bin/env python3
"""
Database Setup Script for UNGA Analysis App

This script helps set up the UNGA vector database with sample data.
The full database (802MB) is not included in the repository due to GitHub size limits.
"""

import os
import sys
import shutil
from pathlib import Path

def setup_database():
    """Set up the database for the UNGA Analysis App."""
    print("🔧 UNGA Analysis App - Database Setup")
    print("=" * 50)
    
    # Check if sample database exists
    backup_db = "unga_vector_backup.db"
    main_db = "unga_vector.db"
    
    if os.path.exists(backup_db):
        print(f"✅ Found backup database: {backup_db}")
        print(f"   Size: {os.path.getsize(backup_db) / 1024:.2f} KB")
        
        # Ask user if they want to use backup or create full database
        print("\n📋 Database Options:")
        print("1. Use backup database (5 speeches) - Quick start")
        print("2. Create full database (802MB) - Full functionality")
        print("3. Keep existing database if it exists")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if os.path.exists(main_db):
                backup_name = f"{main_db}.backup"
                shutil.move(main_db, backup_name)
                print(f"✅ Backed up existing database to {backup_name}")
            
            shutil.copy(backup_db, main_db)
            print(f"✅ Using backup database for quick start")
            print("   Note: Limited to 5 sample speeches")
            
        elif choice == "2":
            print("\n🚀 Creating full database...")
            print("   This will process all UNGA speeches (1946-2024)")
            print("   Estimated time: 10-30 minutes depending on your system")
            print("   Estimated size: ~802MB")
            
            confirm = input("\nContinue with full database creation? (y/N): ").strip().lower()
            if confirm == 'y':
                print("✅ Full database creation initiated")
                print("   Run the app to start the full database creation process")
            else:
                print("❌ Full database creation cancelled")
                return
                
        elif choice == "3":
            if os.path.exists(main_db):
                print(f"✅ Keeping existing database: {main_db}")
                print(f"   Size: {os.path.getsize(main_db) / 1024 / 1024:.2f} MB")
            else:
                print("❌ No existing database found")
                return
        else:
            print("❌ Invalid choice")
            return
    
    else:
        print(f"❌ Sample database not found: {sample_db}")
        print("   Please ensure you have the complete repository")
        return
    
    print("\n🎉 Database setup complete!")
    print("   You can now run: streamlit run app.py")

if __name__ == "__main__":
    setup_database()
