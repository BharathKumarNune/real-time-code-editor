import os
import time
import threading
from openai import OpenAI
from app.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)

# Rate limiting settings
RATE_LIMIT = 3  # Max requests per minute
tokens = RATE_LIMIT
last_reset = time.time()
lock = threading.Lock()

def acquire_token():
    """Checks and refills tokens for rate limiting."""
    global tokens, last_reset
    with lock:
        elapsed = time.time() - last_reset
        if elapsed > 60:  # Refill every minute
            tokens = RATE_LIMIT
            last_reset = time.time()
        if tokens > 0:
            tokens -= 1
            return True
        return False

def ai_debug(code: str):
    if not acquire_token():
        return "Rate limit exceeded. Try again later."
    
    try:
        prompt = f"""
        Analyze the following code and provide:
        1. Syntax errors and fixes
        2. Potential bugs and their fixes
        3. Performance improvements
        4. Code readability enhancements

        Code:{code}

        Respond with suggestions in a structured format.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a code review assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        response_text = response.choices[0].message.content.strip()

        return response_text
    except Exception as e:
        return "An error occurred while processing your request."
