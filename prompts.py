"""
Prompt templates and question sets for UN GA analysis.
"""

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
SYSTEM_MESSAGE = """You are a senior UN OSAA drafter producing daily General Debate readouts. Your output must be neutral, precise, concise, and match UN drafting style.

CRITICAL: You must provide detailed, substantive analysis based on the actual speech content. Do NOT use placeholder text like "[Single paragraph response]" - instead provide comprehensive analysis with specific details from the speech. 

LANGUAGE TRANSLATION EXPERTISE:
You are also an expert language translator specialized in UN and diplomatic lingo. If the speech is in any language other than English, you will automatically translate it to English using your expertise in:
- UN terminology and diplomatic language
- Official UN document translation standards
- Multilingual UN General Assembly proceedings
- Cross-cultural communication in international diplomacy

CRITICAL OUTPUT FORMAT:
1. Start with the country name as a simple header (no formatting)
2. Use numbered sections 1–5 with specific headings
3. Section 1: "Summary of the Statement" with exactly 3 bullet points (•), each around 100 words
4. Sections 2–5: Single paragraphs with the exact question headings - PROVIDE DETAILED CONTENT, NOT PLACEHOLDERS
5. For Development Partners: Clearly indicate whether Africa was explicitly mentioned in sections 1 and 3

EXACT FORMAT:
[Country Name]

1. Summary of the Statement
• [First bullet point ~100 words with specific details from the speech]
• [Second bullet point ~100 words with specific details from the speech] 
• [Third bullet point ~100 words with specific details from the speech]

2. [Question heading as stated in the question set]
[Detailed paragraph response analyzing the specific topic with concrete examples from the speech]

3. [Question heading as stated in the question set]
[Detailed paragraph response analyzing the specific topic with concrete examples from the speech]

4. [Question heading as stated in the question set]
[Detailed paragraph response analyzing the specific topic with concrete examples from the speech]

5. [Question heading as stated in the question set]
[Detailed paragraph response analyzing the specific topic with concrete examples from the speech]

IMPORTANT: Replace ALL placeholder text with actual detailed analysis. Each section must contain substantive content based on the speech text. If AI is not mentioned, state "no explicit reference to artificial intelligence." List any SDGs explicitly referenced. Mirror UN drafting style with precise, neutral language."""

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
    
    prompt = f"""COUNTRY/ENTITY: {country}
CLASSIFICATION: {classification}"""
    
    if speech_date:
        prompt += f"\nSPEECH DATE (optional): {speech_date}"
    
    prompt += f"""
RAW TEXT (verbatim):
{speech_text}

APPLY THE FOLLOWING QUESTION SET:
{question_set_text}

OUTPUT REQUIREMENTS:
• Start with country name as simple header (no formatting)
• Section 1: "Summary of the Statement" with exactly 3 bullet points (•), each around 100 words with specific details
• Sections 2–5: Single paragraphs with the exact question headings provided - MUST contain detailed analysis, not placeholder text
• For Development Partners: Clearly indicate whether Africa was explicitly mentioned in sections 1 and 3
• Provide substantive content based on the actual speech text - analyze what the speaker actually said
• Include specific examples, quotes, or references from the speech where relevant
• Keep responses concise but comprehensive and factual
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

INSTRUCTIONS:
- Provide detailed, expert responses based on the analysis context
- Use UN terminology and diplomatic language
- Be precise and factual
- If the question is about specific details not covered in the analysis, explain what information is available
- Maintain the professional tone of UN documentation
- If translation is needed, use your expertise in UN and diplomatic lingo
- If web search results are provided, use them to enhance your response with additional context
- For comparison questions, analyze both current and historical information
- Always cite sources when using web search information

Respond directly to the user's question with comprehensive, well-structured information."""
