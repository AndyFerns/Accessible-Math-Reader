from gtts import gTTS
import os, time

def text_to_speech(text: str) -> str:
    """Convert text to speech and save as MP3."""
    output_dir = "static/audio"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"output_{int(time.time())}.mp3"
    filepath = os.path.join(output_dir, filename)
    tts = gTTS(text=text, lang='en')
    tts.save(filepath)
    return filepath
