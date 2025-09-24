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

CRITICAL OUTPUT FORMAT:
1. Start with the country name as a simple header (no formatting)
2. Use numbered sections 1–5 with specific headings
3. Section 1: "Summary of the Statement" with exactly 3 bullet points (•), each around 100 words
4. Sections 2–5: Single paragraphs with the exact question headings
5. For Development Partners: Clearly indicate whether Africa was explicitly mentioned in sections 1 and 3

EXACT FORMAT:
[Country Name]

1. Summary of the Statement
• [First bullet point ~100 words]
• [Second bullet point ~100 words] 
• [Third bullet point ~100 words]

2. [Question heading as stated in the question set]
[Single paragraph response]

3. [Question heading as stated in the question set]
[Single paragraph response]

4. [Question heading as stated in the question set]
[Single paragraph response]

5. [Question heading as stated in the question set]
[Single paragraph response]

Keep responses concise and factual. If AI is not mentioned, state "no explicit reference to artificial intelligence." List any SDGs explicitly referenced. Mirror UN drafting style with precise, neutral language."""

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
• Section 1: "Summary of the Statement" with exactly 3 bullet points (•), each around 100 words
• Sections 2–5: Single paragraphs with the exact question headings provided
• For Development Partners: Clearly indicate whether Africa was explicitly mentioned in sections 1 and 3
• Keep responses concise and factual
• End with nothing else."""
    
    return prompt
