"""
Data Limitation Handler for Cross-Year Analysis
Handles cases where requested data is not available in the current dataset
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DataLimitationHandler:
    """Handles data limitations and provides guidance for missing data scenarios."""
    
    def __init__(self):
        self.available_years = set()
        self.available_countries = set()
        self.available_regions = set()
        self.gender_keywords = [
            'gender', 'women', 'girls', 'equality', 'empowerment', 'feminist',
            'gender equality', 'women\'s empowerment', 'girls\' education',
            'violence against women', 'gender-based violence', 'gender discrimination',
            'women\'s rights', 'female', 'maternal', 'reproductive health',
            'gender mainstreaming', 'women in politics', 'gender parity'
        ]
    
    def analyze_data_limitation(self, requested_countries: List[str], 
                              requested_years: List[int], 
                              query: str) -> Dict[str, Any]:
        """
        Analyze what data is missing and provide comprehensive guidance.
        
        Args:
            requested_countries: List of requested country names/codes
            requested_years: List of requested years
            query: The analysis query
            
        Returns:
            Dictionary with limitation analysis and recommendations
        """
        # Get current dataset statistics
        from simple_vector_storage import simple_vector_storage
        stats = simple_vector_storage.get_statistics()
        
        self.available_years = set(stats.get('year_statistics', {}).keys())
        self.available_countries = set()  # Would need to be populated from actual data
        self.available_regions = set(stats.get('region_statistics', {}).keys())
        
        limitation_analysis = {
            'query': query,
            'requested_countries': requested_countries,
            'requested_years': requested_years,
            'available_data': {
                'years': sorted(list(self.available_years)),
                'regions': sorted(list(self.available_regions)),
                'total_speeches': stats.get('total_speeches', 0),
                'total_countries': stats.get('total_countries', 0)
            },
            'limitations': self._identify_limitations(requested_countries, requested_years),
            'recommendations': self._generate_recommendations(requested_countries, requested_years, query),
            'alternative_analysis': self._suggest_alternatives(requested_countries, requested_years, query),
            'template_tables': self._generate_template_tables(requested_countries, requested_years, query)
        }
        
        return limitation_analysis
    
    def _identify_limitations(self, countries: List[str], years: List[int]) -> List[str]:
        """Identify specific data limitations."""
        limitations = []
        
        # Check year availability
        missing_years = set(years) - self.available_years
        if missing_years:
            limitations.append(f"Missing years: {sorted(list(missing_years))}")
        
        # Check if all requested years are missing
        if not any(year in self.available_years for year in years):
            limitations.append("None of the requested years are available in the current dataset")
        
        # Check country availability (simplified - would need actual country data)
        if countries and 'Bangladesh' in countries:
            limitations.append("Bangladesh not available in current dataset (likely only 1946-1947 data)")
        
        # Check date range
        if years and max(years) > 1947:
            limitations.append("Requested analysis period extends beyond available data (1946-1947)")
        
        return limitations
    
    def _generate_recommendations(self, countries: List[str], years: List[int], query: str) -> List[str]:
        """Generate recommendations for obtaining the required data."""
        recommendations = [
            "**Data Acquisition Recommendations:**",
            "",
            "1. **Download Complete UNGA Corpus:**",
            "   - Visit: Harvard Dataverse - UNGA Corpus",
            "   - URL: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0TJX8Y",
            "   - Download and extract to: `artifacts/logo/unga-1946-2024-corpus/`",
            "",
            "2. **Expected File Structure:**",
            "   - Session folders: Session 01 - 1946/ through Session 79 - 2024/",
            "   - Country files: ISO3_COUNTRYCODE_SESSION_YEAR.txt",
            "   - Example: BGD_79_2024.txt for Bangladesh 2024",
            "",
            "3. **Data Ingestion Process:**",
            "   - Use the data ingestion system in the app",
            "   - Files will be automatically processed and vectorized",
            "   - Historical data will be searchable via semantic search",
            "",
            "4. **Bangladesh-Specific Notes:**",
            "   - Bangladesh joined UN in 1974",
            "   - Look for files: BGD_SESSION_YEAR.txt",
            "   - Expected years: 1974-2024 (50 years of data)"
        ]
        
        return recommendations
    
    def _suggest_alternatives(self, countries: List[str], years: List[int], query: str) -> List[str]:
        """Suggest alternative analyses with available data."""
        alternatives = [
            "**Alternative Analyses with Current Data:**",
            "",
            "1. **Available Time Period Analysis (1946-1947):**",
            "   - Analyze gender-related terms in the founding years of the UN",
            "   - Compare post-WWII gender discourse patterns",
            "   - Examine early UN Charter implementation regarding gender equality",
            "",
            "2. **Regional Analysis:**",
            "   - Use available regions instead of specific countries",
            "   - Compare gender discourse across different regions in 1946-1947",
            "",
            "3. **Historical Context Analysis:**",
            "   - Examine how gender issues were framed in the UN's early years",
            "   - Compare with modern gender discourse (qualitative analysis)",
            "",
            "4. **Methodology Demonstration:**",
            "   - Show the analysis methodology using available data",
            "   - Provide templates for when full dataset is available"
        ]
        
        return alternatives
    
    def _generate_template_tables(self, countries: List[str], years: List[int], query: str) -> Dict[str, str]:
        """Generate template tables for the analysis."""
        
        # Create year range for Bangladesh (1974-2024)
        bangladesh_years = list(range(1974, 2025))
        sample_years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]
        
        template_tables = {
            "gender_frequency_by_year": f"""
## Gender-Related Terms Frequency by Year - Bangladesh (Template)

| Year | Total Speeches | Gender Mentions | Percentage | Key Terms Found | Notes |
|------|----------------|-----------------|------------|-----------------|-------|
{chr(10).join([f"| {year} | [TBD] | [TBD] | [TBD]% | [TBD] | [TBD] |" for year in sample_years])}
| **Total** | **[TBD]** | **[TBD]** | **[TBD]%** | **All years** | **Trend analysis** |

**Legend:**
- Gender Mentions: Count of speeches containing gender-related terms
- Percentage: (Gender Mentions / Total Speeches) × 100
- Key Terms: Most frequently mentioned gender-related terms
""",

            "global_trends_comparison": """
## Global Gender Discourse Trends (Qualitative Analysis)

| Period | Global Context | Expected Trends | Key Events |
|--------|----------------|-----------------|------------|
| 1990-1995 | Post-Cold War Era | Rising gender awareness | Beijing Declaration (1995) |
| 1995-2000 | Beijing Platform Implementation | Increased women's rights focus | UNSCR 1325 (2000) |
| 2000-2005 | Millennium Development Goals | MDG 3: Gender Equality | Post-9/11 security focus |
| 2005-2010 | Global Financial Crisis | Economic gender impact | CEDAW Optional Protocol |
| 2010-2015 | Social Media Era | Digital gender divide | HeForShe Campaign (2014) |
| 2015-2020 | SDG Implementation | SDG 5: Gender Equality | #MeToo Movement |
| 2020-2025 | COVID-19 Pandemic | Gender impact of crisis | Generation Equality Forum |

**Historical Inflection Points:**
- **1995**: Beijing Declaration - First comprehensive global framework for women's rights
- **2000**: UNSCR 1325 - Women, Peace and Security agenda
- **2015**: SDG 5 - Gender equality as standalone goal
- **2020**: COVID-19 - Highlighted gender inequalities globally
""",

            "bangladesh_specific_timeline": """
## Bangladesh Gender Discourse Timeline (Expected Analysis)

| Period | Bangladesh Context | Expected Gender Focus | Key Developments |
|--------|-------------------|----------------------|------------------|
| 1974-1990 | Early Independence | Basic women's rights | Constitution guarantees |
| 1990-1995 | Democratic Transition | Women's political participation | First female PM (1991) |
| 1995-2000 | Beijing Implementation | Gender mainstreaming | National Women's Policy |
| 2000-2005 | MDG Era | Education and health focus | Female literacy programs |
| 2005-2010 | Economic Growth | Women's economic empowerment | Microfinance expansion |
| 2010-2015 | Digital Bangladesh | ICT for women's development | Women's entrepreneurship |
| 2015-2020 | SDG Implementation | Comprehensive gender equality | Domestic violence laws |
| 2020-2025 | COVID Response | Gender-responsive recovery | Women's leadership |

**Bangladesh-Specific Milestones:**
- **1971**: Independence with constitutional gender equality
- **1991**: First female Prime Minister (Sheikh Hasina)
- **2010**: Digital Bangladesh initiative
- **2020**: COVID-19 women's economic impact
"""
        }
        
        return template_tables
    
    def generate_limitation_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a comprehensive limitation report."""
        
        report = f"""
# Data Limitation Analysis Report

## Query Analysis
**Requested Analysis:** {analysis_result['query']}
**Countries:** {', '.join(analysis_result['requested_countries'])}
**Years:** {', '.join(map(str, analysis_result['requested_years']))}

## Current Dataset Status
- **Available Years:** {', '.join(map(str, analysis_result['available_data']['years']))}
- **Available Regions:** {', '.join(analysis_result['available_data']['regions'])}
- **Total Speeches:** {analysis_result['available_data']['total_speeches']:,}
- **Total Countries:** {analysis_result['available_data']['total_countries']}

## Data Limitations Identified
{chr(10).join([f"- {limitation}" for limitation in analysis_result['limitations']])}

## Recommendations
{chr(10).join(analysis_result['recommendations'])}

## Alternative Analyses
{chr(10).join(analysis_result['alternative_analysis'])}

## Template Tables for Future Analysis

### {list(analysis_result['template_tables'].keys())[0].replace('_', ' ').title()}
{analysis_result['template_tables'][list(analysis_result['template_tables'].keys())[0]]}

### {list(analysis_result['template_tables'].keys())[1].replace('_', ' ').title()}
{analysis_result['template_tables'][list(analysis_result['template_tables'].keys())[1]]}

### {list(analysis_result['template_tables'].keys())[2].replace('_', ' ').title()}
{analysis_result['template_tables'][list(analysis_result['template_tables'].keys())[2]]}

## Next Steps
1. **Download the complete UNGA corpus** from Harvard Dataverse
2. **Run the data ingestion process** to populate the database
3. **Re-run your analysis** with the full dataset
4. **Use the template tables** to structure your results
5. **Compare with global trends** provided in the templates

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report

# Global instance
data_limitation_handler = DataLimitationHandler()
