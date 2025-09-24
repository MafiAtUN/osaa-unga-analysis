"""
Prompt templates and question sets for UN GA analysis.
"""

# Question sets for different classifications
AFRICAN_MEMBER_STATE_QUESTIONS = """1. Please provide a brief summary of the statement in three bullet points (around 100 words each) focusing on the challenges and opportunities related to (i) Africa's peace and security and human rights; (ii) Africa's sustainable development, including the SDGs and their means of implementation (Sevilla Commitment), Agenda 2063 and climate change; and (iii) the implementation of the outcomes of the Summit of the Future of 2024, including the Pact for the Future, Global Digital Compact and Declaration on Future Generations.

2. What are the challenges and opportunities that the speaker highlights in achieving Sustainable Development Goals (SDGs) and the goals and aspirations of Agenda 2063? Of the 17 SDGs, which ones are mentioned explicitly?

3. Please summarize the key issues related to partnerships and the means of implementation with a focus on the outcome of the Fourth International Conference on Financing for Development (FfD4), the Sevilla Commitment, and Africa's ongoing debt crisis and measures to address debt sustainability in the long term.

4. Please summarize the key issues related to youth, women's empowerment, artificial intelligence, bridging the digital divide and addressing inequalities.

5. Please highlight any references and responses to the UN80 Initiative as well as any other proposals related to multilateralism, including the reform of the UN system, the Security Council and the reform of the international financial architecture."""

DEVELOPMENT_PARTNER_QUESTIONS = """1. Please provide a brief summary of the statement in three bullet points (around 100 words each) focusing on the challenges and opportunities related to (i) Africa's peace and security; (ii) Africa's sustainable development, including the SDGs and their means of implementation (Sevilla Commitment), Agenda 2063 and climate change; and (iii) the implementation of the outcomes of the Summit of the Future of 2024, including the Pact for the Future, Global Digital Compact and Declaration on Future Generations. Please highlight whether or not there is any specific mention of Africa in the remarks.

2. What are the challenges and opportunities that the speaker highlights in achieving sustainable development goals (SDGs)? Of the 17 SDGs, which ones are mentioned explicitly?

3. Please summarize the key issues related to partnerships and the means of implementation with a focus on the outcome of the Fourth International Conference on Financing for Development (FfD4), the Sevilla Commitment, and Africa's ongoing debt crisis and measures to address debt sustainability in the long term. Please highlight any specific mention of Africa in this context.

4. Please summarize the key issues related to youth, women's empowerment, artificial intelligence, bridging the digital divide and addressing inequalities.

5. Please highlight any references and responses to the UN80 Initiative as well as any other proposals related to multilateralism, including the reform of the UN system, the Security Council and the reform of the international financial architecture."""

# System message template
SYSTEM_MESSAGE = """You are a senior UN OSAA drafter producing daily General Debate readouts. Your output must be neutral, precise, concise, and match UN drafting style. Use numbered headings 1–5. Do not add extra headings. Keep the first section to three bullets of ~100 words each, dense with facts. Reference "Africa" explicitly for Development Partners where applicable. If AI is not mentioned in the speech, state "no explicit reference to artificial intelligence." Detect and list any SDGs explicitly referenced. Mirror the tone and structure used in prior OSAA readouts."""

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
• Title line: "### {country}"
• Sections 1–5 exactly as in the question set, with crisp, factual, UN-style bullets/paragraphs.
• For Development Partners, clearly indicate whether Africa was explicitly mentioned (in section 1 or 3 as relevant).
• End with nothing else."""
    
    return prompt
