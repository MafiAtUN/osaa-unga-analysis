#!/usr/bin/env python3
"""
Test script for enhanced search capabilities
Demonstrates the new search engine with proper document referencing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.unga_analysis.core.enhanced_search_engine import get_enhanced_search_engine
from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager

def test_enhanced_search():
    """Test the enhanced search engine functionality."""
    print("🔍 Testing Enhanced Search Engine")
    print("=" * 50)
    
    # Initialize search engine
    enhanced_search = get_enhanced_search_engine(db_manager)
    
    # Test queries
    test_queries = [
        "How has China's focus on climate change evolved over the past decade?",
        "What are the main themes in African countries' speeches about development?",
        "Compare United States and Russia priorities in recent years",
        "Which countries mention gender equality most frequently?",
        "What are the trends in peace and security discussions?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Execute enhanced search
            results = enhanced_search.execute_enhanced_search(query)
            
            print(f"✅ Search Strategy: {results.get('strategy', 'unknown')}")
            print(f"📊 Total Results Found: {results.get('total_found', 0)}")
            
            # Show query analysis
            analysis = results.get('analysis', {})
            print(f"🎯 Query Intent: {analysis.get('intent', 'unknown')}")
            print(f"🏷️  Extracted Entities: {analysis.get('entities', {})}")
            print(f"⚡ Complexity: {analysis.get('complexity', 'unknown')}")
            
            # Show sample results with citations
            results_list = results.get('results', [])
            if results_list:
                print(f"\n📄 Sample Results with Citations:")
                for j, result in enumerate(results_list[:3]):  # Show top 3 results
                    citation = result.get('citation', 'Unknown citation')
                    relevance = result.get('relevance_score', 0)
                    print(f"  {j+1}. {citation} (Relevance: {relevance:.2f})")
                    
                    # Show relevant quotes
                    quotes = result.get('relevant_quotes', [])
                    if quotes:
                        print(f"     💬 Top Quote: \"{quotes[0]['quote'][:100]}...\"")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Enhanced Search Engine Test Completed")

if __name__ == "__main__":
    test_enhanced_search()
