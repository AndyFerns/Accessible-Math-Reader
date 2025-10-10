from flask import Flask, render_template, request, send_from_directory
from src.latex_parser import parse_math_input
from src.speech_converter import text_to_speech
from src.braille_converter import math_to_braille
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    math_input = request.form.get('math_input', '')
    readable_text = parse_math_input(math_input)

    # Generate Braille text from the readable string
    braille_text = math_to_braille(readable_text) # pyright: ignore[reportArgumentType] #type: ignore

    audio_path = text_to_speech(readable_text)
    audio_file = os.path.basename(audio_path)

    return render_template(
        'index.html',
        input_text=math_input,
        readable_text=readable_text,
        audio_file=audio_file,
        braille_text=braille_text  # <-- 3. PASS THE NEW VARIABLE
    )

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

if __name__ == '__main__':
    app.run(debug=True)
