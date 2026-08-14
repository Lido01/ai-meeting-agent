import os
from pathlib import Path
from google import genai
# from google.genai import types
from dotenv import load_dotenv

# Force find the .env file in the exact directory of this script
backend_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=backend_dir / ".env")

# Debugging fallback print statement to catch failures early
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL BUG: Python is still completely failing to read your GEMINI_API_KEY from the .env file!")

# Initialize Client
client = genai.Client(api_key=api_key)

def transcribe_audio(file_path: str) -> str:
    """
    Send meeting audio to Gemini
    and return the transcript.
    """
    # Upload audio file to Gemini
    uploaded_file = client.files.upload(file=file_path)

    # Ask Gemini to transcribe the meeting
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            uploaded_file,
            "Transcribe this meeting accurately. Identify different speakers when possible."
        ]
    )

    return response.text
