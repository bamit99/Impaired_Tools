import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
    return api_key

def create_scraper_config():
    return {
        "llm": {
            "api_key": get_api_key(),
            "model": "openai/gpt-4o-mini",
        },
        "verbose": True,
        "headless": False,
        "user_agent": "CustomWebScraper v1.0",
    }