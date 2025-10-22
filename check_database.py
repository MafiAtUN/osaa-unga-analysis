#!/usr/bin/env python3
"""
Database Check Script for UNGA Analysis App

This script shows information about the current database setup.
"""

import os
import sys
import duckdb
from pathlib import Path

def check_database():
    """Check the current database setup."""
    print("🔍 UNGA Analysis App - Database Check")
    print("=" * 50)
    
    main_db = "unga_vector.db"
    sample_db = "unga_vector_sample.db"
    
    # Check main database
    if os.path.exists(main_db):
        size_mb = os.path.getsize(main_db) / 1024 / 1024
        print(f"✅ Main database found: {main_db}")
        print(f"   Size: {size_mb:.2f} MB")
        
        # Connect and check content
        try:
            conn = duckdb.connect(main_db)
            
            # Count speeches
            result = conn.execute("SELECT COUNT(*) FROM speeches").fetchone()
            speech_count = result[0] if result else 0
            
            # Count embeddings
            result = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()
            embedding_count = result[0] if result else 0
            
            # Get year range
            result = conn.execute("SELECT MIN(year), MAX(year) FROM speeches").fetchone()
            year_range = f"{result[0]}-{result[1]}" if result and result[0] and result[1] else "Unknown"
            
            print(f"   Speeches: {speech_count:,}")
            print(f"   Embeddings: {embedding_count:,}")
            print(f"   Year range: {year_range}")
            
            # Show sample countries
            result = conn.execute("SELECT DISTINCT country FROM speeches LIMIT 10").fetchall()
            countries = [row[0] for row in result]
            print(f"   Sample countries: {', '.join(countries)}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ⚠️  Could not read database content: {e}")
    
    else:
        print(f"❌ Main database not found: {main_db}")
    
    # Check sample database
    if os.path.exists(sample_db):
        size_kb = os.path.getsize(sample_db) / 1024
        print(f"\n✅ Sample database found: {sample_db}")
        print(f"   Size: {size_kb:.2f} KB")
        
        # Connect and check content
        try:
            conn = duckdb.connect(sample_db)
            
            # Count speeches
            result = conn.execute("SELECT COUNT(*) FROM speeches").fetchone()
            speech_count = result[0] if result else 0
            
            # Show sample speeches
            result = conn.execute("SELECT country, year, filename FROM speeches").fetchall()
            print(f"   Sample speeches: {speech_count}")
            for country, year, filename in result:
                print(f"     - {country} ({year}): {filename}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ⚠️  Could not read sample database content: {e}")
    
    else:
        print(f"\n❌ Sample database not found: {sample_db}")
    
    print("\n📋 Next Steps:")
    if not os.path.exists(main_db):
        print("   1. Run: python setup_database.py")
        print("   2. Choose between sample or full database")
    else:
        print("   1. Your database is ready!")
        print("   2. Run: streamlit run app.py")

if __name__ == "__main__":
    check_database()
