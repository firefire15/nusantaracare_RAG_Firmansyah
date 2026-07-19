import os
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI

DEFAULT_OPENAI_BASE_URL = "https://api.notispaces.cloud/v1"
DEFAULT_OPENAI_MODEL = "notispace-v1"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

load_dotenv()
@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    base_url = os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL)
    return OpenAI(api_key=api_key, base_url=base_url)