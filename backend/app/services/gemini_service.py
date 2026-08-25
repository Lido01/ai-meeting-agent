import os
import time
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

backend_dir = Path(__file__).resolve().parents[2]

load_dotenv(dotenv_path=backend_dir / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in the backend .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=api_key)


# ============================================================
# TRANSCRIBE MEETING
# ============================================================

def transcribe_audio(file_path: str) -> str:

    print("===== GEMINI TRANSCRIPTION START =====")

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Meeting file does not exist: {file_path}"
        )

    print(f"File: {file_path}")

    file_size_mb = path.stat().st_size / (1024 * 1024)

    print(f"File size: {file_size_mb:.2f} MB")
    print(f"File extension: {path.suffix}")

    # ========================================================
    # UPLOAD
    # ========================================================

    print("===== UPLOADING FILE TO GEMINI =====")

    uploaded_file = client.files.upload(
        file=str(path)
    )

    print("===== GEMINI FILE UPLOAD COMPLETE =====")
    print(f"Gemini file name: {uploaded_file.name}")
    print(f"Gemini file URI: {uploaded_file.uri}")
    print(f"Gemini MIME type: {uploaded_file.mime_type}")

    # ========================================================
    # WAIT FOR FILE PROCESSING
    # ========================================================

    print("===== WAITING FOR GEMINI FILE PROCESSING =====")

    while True:

        file_info = client.files.get(
            name=uploaded_file.name
        )

        state = getattr(
            file_info.state,
            "name",
            str(file_info.state)
        )

        print(f"Gemini file state: {state}")

        if state == "ACTIVE":
            break

        if state == "FAILED":
            raise RuntimeError(
                "Gemini failed to process the uploaded meeting file."
            )

        time.sleep(2)

    print("===== GEMINI FILE IS READY =====")

    # ========================================================
    # CREATE CHAT
    # ========================================================

    print("===== CREATING GEMINI CHAT =====")

    chat = client.chats.create(
        model="gemini-3.5-flash"
    )

    print("===== GEMINI CHAT CREATED =====")

    # ========================================================
    # TRANSCRIBE
    # ========================================================

    print("===== SENDING TRANSCRIPTION REQUEST =====")

    response = chat.send_message(
        [
            types.Part.from_uri(
                file_uri=uploaded_file.uri,
                mime_type=uploaded_file.mime_type,
            ),
            types.Part.from_text(
                text=(
                    "Transcribe this meeting accurately. "
                    "Identify different speakers when possible. "
                    "Preserve the meaning and wording of the "
                    "conversation. "
                    "Return only the transcript."
                )
            ),
        ]
    )

    print("===== GEMINI TRANSCRIPTION RESPONSE RECEIVED =====")

    transcript = response.text

    if not transcript:
        raise ValueError(
            "Gemini returned an empty transcription."
        )

    print(
        f"Transcript length: {len(transcript)} characters"
    )

    print("===== GEMINI TRANSCRIPTION COMPLETE =====")

    return transcript