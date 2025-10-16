#!/usr/bin/env python3
"""
Test script to demonstrate the data limitation handler functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_limitation_handler import data_limitation_handler

def test_bangladesh_gender_analysis():
    """Test the data limitation handler with Bangladesh gender analysis scenario."""
    
    print("🔍 Testing Data Limitation Handler")
    print("=" * 50)
    
    # Simulate the Bangladesh gender analysis request
    requested_countries = ["Bangladesh"]
    requested_years = list(range(1990, 2026))
    query = "How has the frequency of gender-related terms for Bangladesh changed from 1990–2025?"
    
    print(f"📝 Query: {query}")
    print(f"🌍 Countries: {requested_countries}")
    print(f"📅 Years: {requested_years[0]}-{requested_years[-1]}")
    print()
    
    # Analyze the limitation
    limitation_analysis = data_limitation_handler.analyze_data_limitation(
        requested_countries, requested_years, query
    )
    
    # Display results
    print("📊 LIMITATION ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"🗣️ Available Years: {limitation_analysis['available_data']['years']}")
    print(f"🌍 Available Regions: {limitation_analysis['available_data']['regions']}")
    print(f"📝 Total Speeches: {limitation_analysis['available_data']['total_speeches']:,}")
    print(f"🏛️ Total Countries: {limitation_analysis['available_data']['total_countries']}")
    print()
    
    print("❌ LIMITATIONS IDENTIFIED:")
    for limitation in limitation_analysis['limitations']:
        print(f"   • {limitation}")
    print()
    
    print("💡 KEY RECOMMENDATIONS:")
    for i, rec in enumerate(limitation_analysis['recommendations'][:5], 1):
        print(f"   {i}. {rec}")
    print()
    
    print("🔄 ALTERNATIVE ANALYSES:")
    for i, alt in enumerate(limitation_analysis['alternative_analysis'][:3], 1):
        print(f"   {i}. {alt}")
    print()
    
    # Generate and save the full report
    report = data_limitation_handler.generate_limitation_report(limitation_analysis)
    
    with open("data_limitation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("📄 Full report saved to: data_limitation_report.md")
    print()
    
    # Show template tables
    print("📋 TEMPLATE TABLES AVAILABLE:")
    for table_name in limitation_analysis['template_tables'].keys():
        print(f"   • {table_name.replace('_', ' ').title()}")
    print()
    
    print("✅ Data limitation analysis completed successfully!")
    print("\n🎯 NEXT STEPS:")
    print("   1. Download the complete UNGA corpus from Harvard Dataverse")
    print("   2. Run data ingestion to populate the database")
    print("   3. Re-run your Bangladesh gender analysis")
    print("   4. Use the template tables to structure your results")

if __name__ == "__main__":
    test_bangladesh_gender_analysis()
