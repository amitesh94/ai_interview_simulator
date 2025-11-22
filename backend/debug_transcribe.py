import os
import sys

# Ensure backend package imports work
sys.path.append(os.path.dirname(__file__))

from transcription_service import transcribe_audio

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    print("No uploads directory found")
    sys.exit(0)

files = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
if not files:
    print("No files in uploads directory")
    sys.exit(0)

files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
latest = files[0]
print("Testing transcription for:", latest)

result = transcribe_audio(latest)
print("TRANSCRIBE RESULT:\n", repr(result))
