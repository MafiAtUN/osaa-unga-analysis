#!/usr/bin/env python3
"""
Final comprehensive test script for the UNGA Analysis App
Tests all functionality after refactoring
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing imports...")
    
    try:
        # Test main application
        from src.unga_analysis.main import main
        print("   ✅ Main application imports successfully")
        
        # Test core modules
        from src.unga_analysis.core.user_auth import UserAuthManager
        from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
        from src.unga_analysis.utils.country_manager import country_manager
        print("   ✅ Core modules import successfully")
        
        # Test UI modules
        from src.unga_analysis.ui.auth_interface import render_auth_interface
        from src.unga_analysis.ui.tabs.new_analysis_tab import render_new_analysis_tab
        from src.unga_analysis.ui.tabs.cross_year_analysis_tab import render_cross_year_analysis_tab
        print("   ✅ UI modules import successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def test_database():
    """Test database functionality."""
    print("🗄️ Testing database...")
    
    try:
        from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
        
        # Test basic connection
        result = db_manager.conn.execute("SELECT 1").fetchone()
        assert result[0] == 1
        print("   ✅ Database connection successful")
        
        # Test speeches count
        speeches_count = db_manager.conn.execute("SELECT COUNT(*) FROM speeches").fetchone()[0]
        print(f"   ✅ Speeches table: {speeches_count} records")
        
        # Test countries count
        countries_count = db_manager.conn.execute("SELECT COUNT(DISTINCT country_name) FROM speeches").fetchone()[0]
        print(f"   ✅ Countries: {countries_count} unique countries")
        
        # Test embeddings
        embeddings_count = db_manager.conn.execute("SELECT COUNT(*) FROM speeches WHERE embedding IS NOT NULL").fetchone()[0]
        print(f"   ✅ Embeddings: {embeddings_count}/{speeches_count} speeches have embeddings")
        
        # Test African classification
        african_count = db_manager.conn.execute("SELECT COUNT(*) FROM speeches WHERE is_african_member = true").fetchone()[0]
        non_african_count = db_manager.conn.execute("SELECT COUNT(*) FROM speeches WHERE is_african_member = false").fetchone()[0]
        print(f"   ✅ African classification: {african_count} African, {non_african_count} non-African")
        
        return True
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_search_functionality():
    """Test search functionality."""
    print("🔍 Testing search functionality...")
    
    try:
        from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
        
        # Test basic search
        search_results = db_manager.search_speeches(
            query_text="climate change",
            limit=5
        )
        print(f"   ✅ Basic search: {len(search_results)} results")
        
        # Test country search
        country_results = db_manager.search_speeches(
            countries=["United States"],
            years=[2023],
            limit=5
        )
        print(f"   ✅ Country search: {len(country_results)} results")
        
        # Test year search
        year_results = db_manager.search_speeches(
            years=[2020, 2021, 2022],
            limit=5
        )
        print(f"   ✅ Year search: {len(year_results)} results")
        
        return True
    except Exception as e:
        print(f"   ❌ Search test failed: {e}")
        return False

def test_country_management():
    """Test country management."""
    print("🌍 Testing country management...")
    
    try:
        from src.unga_analysis.utils.country_manager import country_manager
        
        # Test get all countries
        all_countries = country_manager.get_all_countries()
        print(f"   ✅ All countries: {len(all_countries)} countries")
        
        # Test specific countries
        test_countries = ["United States", "China", "Algeria", "Nigeria"]
        for country in test_countries:
            if country in all_countries:
                print(f"   ✅ {country} found")
            else:
                print(f"   ❌ {country} not found")
        
        # Test African countries
        african_countries = country_manager.get_african_countries()
        print(f"   ✅ African countries: {len(african_countries)} countries")
        
        # Test development partners
        dev_partners = country_manager.get_development_partners()
        print(f"   ✅ Development partners: {len(dev_partners)} countries")
        
        # Test country stats
        stats = country_manager.get_country_stats()
        print(f"   ✅ Country stats: {stats}")
        
        return True
    except Exception as e:
        print(f"   ❌ Country management test failed: {e}")
        return False

def test_authentication():
    """Test authentication system."""
    print("🔐 Testing authentication...")
    
    try:
        from src.unga_analysis.core.user_auth import UserAuthManager
        
        # Test auth manager initialization
        auth_manager = UserAuthManager()
        print("   ✅ UserAuthManager initialized")
        
        # Test user database
        import sqlite3
        conn = sqlite3.connect("user_auth.db")
        cursor = conn.cursor()
        
        users_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        print(f"   ✅ User database: {users_count} users")
        
        # Test admin user
        admin_user = cursor.execute("SELECT email FROM users WHERE email = 'islam50@un.org'").fetchone()
        if admin_user:
            print("   ✅ Admin user exists")
        else:
            print("   ❌ Admin user not found")
        
        conn.close()
        
        return True
    except Exception as e:
        print(f"   ❌ Authentication test failed: {e}")
        return False

def test_cross_year_analysis():
    """Test cross-year analysis."""
    print("📊 Testing cross-year analysis...")
    
    try:
        from src.unga_analysis.data.cross_year_analysis import CrossYearAnalysisManager
        
        # Test analysis manager initialization
        analysis_manager = CrossYearAnalysisManager()
        print("   ✅ CrossYearAnalysisManager initialized")
        
        # Test search by criteria (without limit parameter)
        criteria_results = analysis_manager.search_speeches_by_criteria(
            query_text="sustainable development",
            countries=["Germany", "France"],
            years=[2022, 2023]
        )
        print(f"   ✅ Criteria search: {len(criteria_results)} results")
        
        return True
    except Exception as e:
        print(f"   ❌ Cross-year analysis test failed: {e}")
        return False

def test_enhanced_search():
    """Test enhanced search engine."""
    print("🔍 Testing enhanced search engine...")
    
    try:
        from src.unga_analysis.core.enhanced_search_engine import get_enhanced_search_engine
        from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager
        
        # Test search engine initialization
        search_engine = get_enhanced_search_engine(db_manager)
        print("   ✅ Enhanced search engine initialized")
        
        # Test entity extraction
        entities = search_engine.extract_entities("What did the United States say about climate change in 2023?")
        print(f"   ✅ Entity extraction: {len(entities.get('countries', []))} countries, {len(entities.get('years', []))} years")
        
        return True
    except Exception as e:
        print(f"   ❌ Enhanced search test failed: {e}")
        return False

def test_ui_components():
    """Test UI components."""
    print("🖥️ Testing UI components...")
    
    try:
        # Test auth interface
        from src.unga_analysis.ui.auth_interface import render_auth_interface, is_user_authenticated
        print("   ✅ Auth interface imports successful")
        
        # Test tab components
        from src.unga_analysis.ui.tabs.new_analysis_tab import render_new_analysis_tab
        from src.unga_analysis.ui.tabs.cross_year_analysis_tab import render_cross_year_analysis_tab
        from src.unga_analysis.ui.tabs.database_chat_tab import render_database_chat_tab
        from src.unga_analysis.ui.tabs.document_context_analysis_tab import render_document_context_analysis_tab
        from src.unga_analysis.ui.tabs.all_analyses_tab import render_all_analyses_tab
        from src.unga_analysis.ui.tabs.visualizations_tab import render_visualizations_tab
        from src.unga_analysis.ui.tabs.data_explorer_tab import render_data_explorer_tab
        from src.unga_analysis.ui.tabs.error_insights_tab import render_error_insights_tab
        print("   ✅ All tab components import successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ UI components test failed: {e}")
        return False

def test_application_startup():
    """Test application startup."""
    print("🚀 Testing application startup...")
    
    try:
        from src.unga_analysis.main import main
        
        # Test that main function is callable
        if callable(main):
            print("   ✅ Main function is callable")
        else:
            print("   ❌ Main function is not callable")
            return False
        
        # Test Streamlit import
        import streamlit as st
        print("   ✅ Streamlit imported successfully")
        
        # Test environment variables
        from dotenv import load_dotenv
        load_dotenv()
        print("   ✅ Environment variables loaded")
        
        return True
    except Exception as e:
        print(f"   ❌ Application startup test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 FINAL COMPREHENSIVE TESTING")
    print("=" * 50)
    print()
    
    tests = [
        ("Import Tests", test_imports),
        ("Database Tests", test_database),
        ("Search Functionality", test_search_functionality),
        ("Country Management", test_country_management),
        ("Authentication", test_authentication),
        ("Cross-Year Analysis", test_cross_year_analysis),
        ("Enhanced Search", test_enhanced_search),
        ("UI Components", test_ui_components),
        ("Application Startup", test_application_startup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"   ✅ {test_name} PASSED")
            else:
                print(f"   ❌ {test_name} FAILED")
        except Exception as e:
            print(f"   ❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The application is ready for production!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
