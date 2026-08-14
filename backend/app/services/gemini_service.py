import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Get API key from .env
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def transcribe_audio(file_path: str) -> str:
    """
    Send meeting audio to Gemini
    and return the transcript.
    """

    # Upload audio file to Gemini
    uploaded_file = client.files.upload(
        file=file_path
    )

    # Ask Gemini to transcribe the meeting
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            uploaded_file,
            "Transcribe this meeting accurately. "
            "Identify different speakers when possible."
        ]
    )

    return response.text