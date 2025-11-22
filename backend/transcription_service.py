import os
import whisper

# Load Whisper model ONCE when the module is imported
# You can change "base" to "small", "medium", or "large"
# Larger models = better accuracy but slower
print("🔊 Loading Whisper model... (this happens once)")
model = whisper.load_model("base")
print("✅ Whisper model loaded successfully!")


def transcribe_audio(file_path: str):
    """
    Transcribe audio/video file using local Whisper model.
    Works offline.
    Supports: mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm, etc.
    Returns: transcription text on success, or error dict.
    """

    try:
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            print(f"❌ Transcription error: {error_msg}")
            return {"error": error_msg}

        print(f"🎙 Transcribing file: {file_path}")
        file_size = os.path.getsize(file_path)
        print(f"📦 File size: {file_size} bytes")

        # Whisper does the full transcription here
        print("🔄 Running Whisper model...")
        result = model.transcribe(file_path)

        text = result.get("text", "").strip()

        if not text:
            return {"error": "Whisper returned empty transcription"}

        print("✅ Transcription complete!")
        print(f"📝 Text: {text[:100]}...")

        return text

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ Whisper transcription error [{error_type}]: {error_msg}")

        import traceback
        traceback.print_exc()

        return {"error": f"{error_type}: {error_msg}"}
