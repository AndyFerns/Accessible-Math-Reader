from flask import Flask, render_template, request, send_from_directory
# 1. Import BOTH parser functions
from src.latex_parser import parse_math_input, latex_to_braille_simple
from src.speech_converter import text_to_speech
from src.braille_converter import math_to_braille
import os

app = Flask(__name__)

# Ensure the static/audio directory exists
if not os.path.exists('static/audio'):
    os.makedirs('static/audio')

@app.route('/')
def index():
    # Pass 'input_text' as None or empty on initial load
    # This ensures the placeholder shows
    return render_template('index.html', input_text=None, readable_text=None)

@app.route('/convert', methods=['POST'])
def convert():
    math_input = request.form.get('math_input', '')
    
    # --- This is the new logic ---
    
    # 1. Generate readable text for SPEECH
    # (e.g., "\frac{a}{b}" -> "a divided by b")
    readable_text = parse_math_input(math_input)

    # 2. Generate a simple math string for BRAILLE
    # (e.g., "\frac{a}{b}" -> "a/b")
    simple_math_text = latex_to_braille_simple(math_input)
    
    # 3. Generate Braille text from the SIMPLE string
    # (e.g., "a/b" -> "⠁⠌⠃")
    braille_text = math_to_braille(simple_math_text)
    
    # 4. Generate Speech from the READABLE string
    # (e.g., "a divided by b" -> output.mp3)
    audio_path = text_to_speech(readable_text)
    audio_file = os.path.basename(audio_path)

    # --- End of new logic ---

    return render_template(
        'index.html',
        input_text=math_input,
        readable_text=readable_text,
        audio_file=audio_file,
        braille_text=braille_text 
    )

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    # Ensure the path is correct
    return send_from_directory(os.path.join(app.root_path, 'static/audio'), filename)

if __name__ == '__main__':
    app.run(debug=True)