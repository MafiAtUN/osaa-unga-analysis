"""
OpenAI API integration with retry logic and error handling.
"""

import time
import logging
from typing import Optional, Dict, Any
from openai import AzureOpenAI
import tiktoken

logger = logging.getLogger(__name__)

class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken.
    
    Args:
        text: Text to count tokens for
        model: Model name to use for encoding
        
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to cl100k_base encoding
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

def validate_token_limits(system_message: str, user_message: str, 
                         model: str = "gpt-4", max_input_tokens: int = 100000) -> bool:
    """
    Validate that messages are within token limits.
    
    Args:
        system_message: System message text
        user_message: User message text
        model: Model name
        max_input_tokens: Maximum input tokens allowed
        
    Returns:
        True if within limits, False otherwise
    """
    total_tokens = count_tokens(system_message + user_message, model)
    return total_tokens <= max_input_tokens

def run_analysis(system_msg: str, user_msg: str, model: str = "gpt-4o", 
                client: Optional[AzureOpenAI] = None, max_retries: int = 3) -> str:
    """
    Run analysis using Azure OpenAI Chat Completions API with retry logic.
    
    Args:
        system_msg: System message
        user_msg: User message
        model: Model to use (default: gpt-4o)
        client: Azure OpenAI client instance
        max_retries: Maximum number of retry attempts
        
    Returns:
        Generated response text
        
    Raises:
        OpenAIError: If API call fails after all retries
    """
    if not client:
        raise ValueError("Azure OpenAI client is required")
    
    # Validate token limits
    if not validate_token_limits(system_msg, user_msg, model):
        raise OpenAIError("Input exceeds token limits for the selected model")
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,  # Low temperature for consistent output
                max_tokens=4000,  # Reasonable limit for analysis output
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.RateLimitError as e:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Rate limit exceeded, waiting {wait_time}s before retry {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise OpenAIError(f"Rate limit exceeded after {max_retries} attempts: {e}")
                
        except openai.APITimeoutError as e:
            wait_time = 2 ** attempt
            logger.warning(f"API timeout, waiting {wait_time}s before retry {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise OpenAIError(f"API timeout after {max_retries} attempts: {e}")
                
        except openai.APIConnectionError as e:
            wait_time = 2 ** attempt
            logger.warning(f"API connection error, waiting {wait_time}s before retry {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise OpenAIError(f"API connection failed after {max_retries} attempts: {e}")
                
        except openai.BadRequestError as e:
            # Don't retry on bad requests
            raise OpenAIError(f"Bad request to OpenAI API: {e}")
            
        except openai.AuthenticationError as e:
            # Don't retry on authentication errors
            raise OpenAIError(f"Authentication failed: {e}")
            
        except Exception as e:
            wait_time = 2 ** attempt
            logger.warning(f"Unexpected error: {e}, waiting {wait_time}s before retry {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise OpenAIError(f"Unexpected error after {max_retries} attempts: {e}")

def chunk_and_synthesize(system_msg: str, user_msg: str, model: str = "gpt-4o",
                        client: Optional[AzureOpenAI] = None, max_chunk_size: int = 20000) -> str:
    """
    Handle long texts by chunking and synthesizing.
    
    Args:
        system_msg: System message
        user_msg: User message
        model: Model to use
        client: Azure OpenAI client instance
        max_chunk_size: Maximum chunk size in characters
        
    Returns:
        Synthesized analysis
    """
    # Extract speech text from user message
    speech_start = user_msg.find("RAW TEXT (verbatim):")
    if speech_start == -1:
        return run_analysis(system_msg, user_msg, model, client)
    
    speech_text = user_msg[speech_start + len("RAW TEXT (verbatim):"):]
    preamble = user_msg[:speech_start]
    
    # Check if chunking is needed
    if len(speech_text) <= max_chunk_size:
        return run_analysis(system_msg, user_msg, model, client)
    
    # Split into chunks
    chunks = []
    current_chunk = ""
    paragraphs = speech_text.split('\n\n')
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= max_chunk_size:
            current_chunk += paragraph + '\n\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Analyze each chunk
    chunk_analyses = []
    for i, chunk in enumerate(chunks):
        chunk_user_msg = f"{preamble}RAW TEXT (verbatim):\n{chunk}"
        try:
            chunk_analysis = run_analysis(system_msg, chunk_user_msg, model, client)
            chunk_analyses.append(f"Chunk {i+1} Analysis:\n{chunk_analysis}")
        except Exception as e:
            logger.warning(f"Failed to analyze chunk {i+1}: {e}")
            continue
    
    if not chunk_analyses:
        raise OpenAIError("Failed to analyze any chunks")
    
    # Synthesize the chunk analyses
    synthesis_prompt = f"""Please synthesize the following chunk analyses into a single, coherent analysis following the same format and structure. Combine insights while maintaining the numbered sections and UN drafting style:

{chr(10).join(chunk_analyses)}"""
    
    synthesis_user_msg = f"{preamble}RAW TEXT (verbatim):\n{synthesis_prompt}"
    
    return run_analysis(system_msg, synthesis_user_msg, model, client)

def get_available_models() -> list[str]:
    """
    Get list of available OpenAI models for the dropdown.
    
    Returns:
        List of model names
    """
    return [
        "model-router-osaa",
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]

def estimate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4o") -> float:
    """
    Estimate the cost of an API call.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
        
    Returns:
        Estimated cost in USD
    """
    # Pricing per 1K tokens (as of 2024)
    pricing = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }
    
    model_pricing = pricing.get(model, pricing["gpt-4o"])
    input_cost = (input_tokens / 1000) * model_pricing["input"]
    output_cost = (output_tokens / 1000) * model_pricing["output"]
    
    return input_cost + output_cost
