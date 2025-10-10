from gtts import gTTS

def generate_ssml(text):
    """
    Generate SSML markup to make math speech more expressive.
    """
    ssml = f"""
    <speak>
        <prosody rate="medium" pitch="medium">
            {text}
        </prosody>
    </speak>
    """
    return ssml.strip()

def text_to_speech(text, output_path="static/audio/output.mp3"):
    """
    Convert text (or SSML fallback) into speech using gTTS.
    """
    ssml = generate_ssml(text)

    # Fallback since gTTS doesn't support SSML directly
    tts = gTTS(text=text, lang="en")
    tts.save(output_path)

    # Optionally, write SSML version for engines that support it
    with open(output_path.replace(".mp3", ".ssml"), "w", encoding="utf-8") as f:
        f.write(ssml)

    return output_path
