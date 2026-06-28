from google import genai
from dotenv import load_dotenv
import os

load_dotenv()


def _get_client(api_key=None):
    if api_key is None:
        api_key = os.getenv("APIKEY")

    if not api_key:
        raise ValueError(
            "No API key provided. Set APIKEY in your environment or Streamlit secrets."
        )

    return genai.Client(api_key=api_key)


def Generatetxt(text, api_key=None):
    client = _get_client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text,
    )
    return response.text
