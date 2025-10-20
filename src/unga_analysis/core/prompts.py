"""
Prompt templates and question sets for UN GA analysis.
"""

# Country flag emojis for enhanced display
COUNTRY_FLAGS = {
    "Afghanistan": "🇦🇫", "Albania": "🇦🇱", "Algeria": "🇩🇿", "Andorra": "🇦🇩", "Angola": "🇦🇴",
    "Antigua and Barbuda": "🇦🇬", "Argentina": "🇦🇷", "Armenia": "🇦🇲", "Australia": "🇦🇺", "Austria": "🇦🇹",
    "Azerbaijan": "🇦🇿", "Bahamas": "🇧🇸", "Bahrain": "🇧🇭", "Bangladesh": "🇧🇩", "Barbados": "🇧🇧",
    "Belarus": "🇧🇾", "Belgium": "🇧🇪", "Belize": "🇧🇿", "Benin": "🇧🇯", "Bhutan": "🇧🇹",
    "Bolivia": "🇧🇴", "Bosnia and Herzegovina": "🇧🇦", "Botswana": "🇧🇼", "Brazil": "🇧🇷", "Brunei": "🇧🇳",
    "Bulgaria": "🇧🇬", "Burkina Faso": "🇧🇫", "Burundi": "🇧🇮", "Cambodia": "🇰🇭", "Cameroon": "🇨🇲",
    "Canada": "🇨🇦", "Cape Verde": "🇨🇻", "Central African Republic": "🇨🇫", "Chad": "🇹🇩", "Chile": "🇨🇱",
    "China": "🇨🇳", "Colombia": "🇨🇴", "Comoros": "🇰🇲", "Congo": "🇨🇬", "Costa Rica": "🇨🇷",
    "Côte d'Ivoire": "🇨🇮", "Croatia": "🇭🇷", "Cuba": "🇨🇺", "Cyprus": "🇨🇾", "Czech Republic": "🇨🇿",
    "Democratic Republic of the Congo": "🇨🇩", "Denmark": "🇩🇰", "Djibouti": "🇩🇯", "Dominica": "🇩🇲",
    "Dominican Republic": "🇩🇴", "Ecuador": "🇪🇨", "Egypt": "🇪🇬", "El Salvador": "🇸🇻", "Equatorial Guinea": "🇬🇶",
    "Eritrea": "🇪🇷", "Estonia": "🇪🇪", "Eswatini": "🇸🇿", "Ethiopia": "🇪🇹", "Fiji": "🇫🇯",
    "Finland": "🇫🇮", "France": "🇫🇷", "Gabon": "🇬🇦", "Gambia": "🇬🇲", "Georgia": "🇬🇪",
    "Germany": "🇩🇪", "Ghana": "🇬🇭", "Greece": "🇬🇷", "Grenada": "🇬🇩", "Guatemala": "🇬🇹",
    "Guinea": "🇬🇳", "Guinea-Bissau": "🇬🇼", "Guyana": "🇬🇾", "Haiti": "🇭🇹", "Honduras": "🇭🇳",
    "Hungary": "🇭🇺", "Iceland": "🇮🇸", "India": "🇮🇳", "Indonesia": "🇮🇩", "Iran": "🇮🇷",
    "Iraq": "🇮🇶", "Ireland": "🇮🇪", "Israel": "🇮🇱", "Italy": "🇮🇹", "Jamaica": "🇯🇲",
    "Japan": "🇯🇵", "Jordan": "🇯🇴", "Kazakhstan": "🇰🇿", "Kenya": "🇰🇪", "Kiribati": "🇰🇮",
    "Kuwait": "🇰🇼", "Kyrgyzstan": "🇰🇬", "Laos": "🇱🇦", "Latvia": "🇱🇻", "Lebanon": "🇱🇧",
    "Lesotho": "🇱🇸", "Liberia": "🇱🇷", "Libya": "🇱🇾", "Liechtenstein": "🇱🇮", "Lithuania": "🇱🇹",
    "Luxembourg": "🇱🇺", "Madagascar": "🇲🇬", "Malawi": "🇲🇼", "Malaysia": "🇲🇾", "Maldives": "🇲🇻",
    "Mali": "🇲🇱", "Malta": "🇲🇹", "Marshall Islands": "🇲🇭", "Mauritania": "🇲🇷", "Mauritius": "🇲🇺",
    "Mexico": "🇲🇽", "Micronesia": "🇫🇲", "Moldova": "🇲🇩", "Monaco": "🇲🇨", "Mongolia": "🇲🇳",
    "Montenegro": "🇲🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿", "Myanmar": "🇲🇲", "Namibia": "🇳🇦",
    "Nauru": "🇳🇷", "Nepal": "🇳🇵", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Nicaragua": "🇳🇮",
    "Niger": "🇳🇪", "Nigeria": "🇳🇬", "North Korea": "🇰🇵", "North Macedonia": "🇲🇰", "Norway": "🇳🇴",
    "Oman": "🇴🇲", "Pakistan": "🇵🇰", "Palau": "🇵🇼", "Palestine": "🇵🇸", "Panama": "🇵🇦",
    "Papua New Guinea": "🇵🇬", "Paraguay": "🇵🇾", "Peru": "🇵🇪", "Philippines": "🇵🇭", "Poland": "🇵🇱",
    "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Romania": "🇷🇴", "Russia": "🇷🇺", "Rwanda": "🇷🇼",
    "Saint Kitts and Nevis": "🇰🇳", "Saint Lucia": "🇱🇨", "Saint Vincent and the Grenadines": "🇻🇨",
    "Samoa": "🇼🇸", "San Marino": "🇸🇲", "Sao Tome and Principe": "🇸🇹", "Saudi Arabia": "🇸🇦",
    "Senegal": "🇸🇳", "Serbia": "🇷🇸", "Seychelles": "🇸🇨", "Sierra Leone": "🇸🇱", "Singapore": "🇸🇬",
    "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Solomon Islands": "🇸🇧", "Somalia": "🇸🇴", "South Africa": "🇿🇦",
    "South Korea": "🇰🇷", "South Sudan": "🇸🇸", "Spain": "🇪🇸", "Sri Lanka": "🇱🇰", "Sudan": "🇸🇩",
    "Suriname": "🇸🇷", "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Syria": "🇸🇾", "Tajikistan": "🇹🇯",
    "Tanzania": "🇹🇿", "Thailand": "🇹🇭", "Timor-Leste": "🇹🇱", "Togo": "🇹🇬", "Tonga": "🇹🇴",
    "Trinidad and Tobago": "🇹🇹", "Tunisia": "🇹🇳", "Turkey": "🇹🇷", "Turkmenistan": "🇹🇲", "Tuvalu": "🇹🇻",
    "Uganda": "🇺🇬", "Ukraine": "🇺🇦", "United Arab Emirates": "🇦🇪", "United Kingdom": "🇬🇧", "United States": "🇺🇸",
    "Uruguay": "🇺🇾", "Uzbekistan": "🇺🇿", "Vanuatu": "🇻🇺", "Vatican City": "🇻🇦", "Venezuela": "🇻🇪",
    "Vietnam": "🇻🇳", "Yemen": "🇾🇪", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼"
}

def get_country_flag(country_name: str) -> str:
    """Get the flag emoji for a country name."""
    return COUNTRY_FLAGS.get(country_name, "🇺🇳")

# Question sets for different classifications
AFRICAN_MEMBER_STATE_QUESTIONS = """1. Summary of the Statement

2. Challenges and Opportunities in Achieving the SDGs and Agenda 2063

3. Partnerships, Means of Implementation, and Debt

4. Youth, Women's Empowerment, AI, Digital Divide, and Inequalities

5. UN80 Initiative, Multilateralism, and UN Reform"""

DEVELOPMENT_PARTNER_QUESTIONS = """1. Summary of the Statement

2. Challenges and Opportunities in Achieving the SDGs

3. Partnerships, Means of Implementation, and Debt

4. Youth, Women's Empowerment, AI, Digital Divide, and Inequalities

5. UN80 Initiative, Multilateralism, and UN Reform"""

# System message template
SYSTEM_MESSAGE = """You are a senior UN OSAA analyst producing comprehensive General Debate readouts. Your output must be neutral, precise, detailed, and match UN drafting style with enhanced formatting for better readability.

CRITICAL: You must provide detailed, substantive analysis based on the actual speech content. Use rich formatting including tables, bullet points, and structured data presentation.

LANGUAGE TRANSLATION EXPERTISE:
You are also an expert language translator specialized in UN and diplomatic lingo. If the speech is in any language other than English, you will automatically translate it to English using your expertise in:
- UN terminology and diplomatic language
- Official UN document translation standards
- Multilingual UN General Assembly proceedings
- Cross-cultural communication in international diplomacy

ENHANCED OUTPUT FORMAT:
1. Start with the country name as a header with flag emoji
2. Use numbered sections 1–5 with specific headings
3. Section 1: "Summary of the Statement" with exactly 3 bullet points (•), each around 100 words
4. Sections 2–5: Use structured formatting with:
   - Key points as bullet lists
   - Data/statistics in tables when relevant
   - Important quotes in blockquotes
   - Action items or commitments clearly highlighted
5. For Development Partners: Clearly indicate whether Africa was explicitly mentioned in sections 1 and 3

ENHANCED FORMAT EXAMPLE:
# 🇺🇳 [Country Name]

## 1. Summary of the Statement
• **[Key Theme 1]**: [First bullet point ~100 words with specific details from the speech]
• **[Key Theme 2]**: [Second bullet point ~100 words with specific details from the speech] 
• **[Key Theme 3]**: [Third bullet point ~100 words with specific details from the speech]

## 2. [Question heading as stated in the question set]

### Key Points:
• [Specific point 1 with details]
• [Specific point 2 with details]
• [Specific point 3 with details]

### Data & Statistics:
| Metric | Value | Context |
|--------|-------|---------|
| [Metric 1] | [Value] | [Context from speech] |
| [Metric 2] | [Value] | [Context from speech] |

### Notable Quotes:
> "[Direct quote from speech with context]"

### Commitments & Actions:
- [Specific commitment or action mentioned]
- [Another commitment or action]

## 3. [Question heading as stated in the question set]
[Similar structured format with bullet points, tables, quotes, and commitments]

## 4. [Question heading as stated in the question set]
[Similar structured format with bullet points, tables, quotes, and commitments]

## 5. [Question heading as stated in the question set]
[Similar structured format with bullet points, tables, quotes, and commitments]

### Analysis Summary:
**SDGs Referenced**: [List specific SDGs mentioned]
**Key Themes**: [List main themes]
**Africa Mention**: [Yes/No - for Development Partners only]

IMPORTANT: 
- Use rich Markdown formatting for better readability
- Include tables for data, statistics, and comparisons
- Use bullet points for key information
- Include direct quotes in blockquotes
- Highlight commitments and action items
- List specific SDGs referenced
- Provide substantive content based on actual speech text
- Mirror UN drafting style with precise, neutral language"""

def get_question_set(classification: str) -> str:
    """Get the appropriate question set based on classification."""
    if classification == "African Member State":
        return AFRICAN_MEMBER_STATE_QUESTIONS
    else:
        return DEVELOPMENT_PARTNER_QUESTIONS

def build_user_prompt(speech_text: str, classification: str, country: str, 
                     speech_date: str = None, question_set_text: str = None) -> str:
    """Build the user prompt for OpenAI API."""
    if question_set_text is None:
        question_set_text = get_question_set(classification)
    
    prompt = f"""COUNTRY/ENTITY: {country} {get_country_flag(country)}
CLASSIFICATION: {classification}"""
    
    if speech_date:
        prompt += f"\nSPEECH DATE (optional): {speech_date}"
    
    prompt += f"""
RAW TEXT (verbatim):
{speech_text}

APPLY THE FOLLOWING QUESTION SET:
{question_set_text}

ENHANCED OUTPUT REQUIREMENTS:
• Start with country name as header with flag emoji (use the country flag provided in the prompt)
• Section 1: "Summary of the Statement" with exactly 3 bullet points (•), each around 100 words with specific details
• Sections 2–5: Use structured formatting with:
  - Key points as bullet lists
  - Data/statistics in tables when relevant
  - Important quotes in blockquotes (>)
  - Action items or commitments clearly highlighted
• For Development Partners: Clearly indicate whether Africa was explicitly mentioned in sections 1 and 3
• Include an "Analysis Summary" section at the end with:
  - SDGs Referenced (list specific SDGs mentioned)
  - Key Themes (list main themes)
  - Africa Mention (Yes/No - for Development Partners only)
• Provide substantive content based on the actual speech text - analyze what the speaker actually said
• Include specific examples, quotes, or references from the speech where relevant
• Use rich Markdown formatting for better readability
• Keep responses comprehensive and factual with enhanced visual structure
• End with nothing else."""
    
    return prompt

def build_chat_prompt(question: str, analysis_context: str, country: str, classification: str, web_search_results: str = "") -> str:
    """Build a prompt for chat interactions with the analyzed text."""
    return f"""You are a UN OSAA expert assistant helping users understand and explore UN General Assembly speeches. You have access to the following analysis context:

COUNTRY/ENTITY: {country}
CLASSIFICATION: {classification}

ANALYSIS CONTEXT:
{analysis_context}

USER QUESTION: {question}

{web_search_results}

ENHANCED RESPONSE INSTRUCTIONS:
- Provide detailed, expert responses based on the analysis context
- Use UN terminology and diplomatic language
- Be precise and factual with enhanced formatting
- Structure your response with:
  * Clear headings and subheadings
  * Bullet points for key information
  * Tables for data, statistics, or comparisons
  * Blockquotes for important quotes or statements
  * Bold text for emphasis on key points
- If the question is about specific details not covered in the analysis, explain what information is available
- Maintain the professional tone of UN documentation
- If translation is needed, use your expertise in UN and diplomatic lingo
- If web search results are provided, use them to enhance your response with additional context
- For comparison questions, analyze both current and historical information
- Always cite sources when using web search information
- Use rich Markdown formatting for better readability
- Include relevant data visualizations suggestions when appropriate

Respond directly to the user's question with comprehensive, well-structured information using enhanced formatting."""
