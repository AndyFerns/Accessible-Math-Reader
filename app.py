from flask import Flask, render_template, request, send_from_directory
from src.latex_parser import parse_math_input
from src.speech_converter import text_to_speech
from src.braille_converter import math_to_braille
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    math_input = request.form['math_input']
    parsed_text = parse_math_input(math_input)
    braille_output = math_to_braille(parsed_text)
    audio_path = text_to_speech(parsed_text)
    return render_template('index.html', 
                           braille_output=braille_output,
                           audio_file=os.path.basename(audio_path),
                           input_text=math_input)

@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory('static/audio', filename)

if __name__ == '__main__':
    app.run(debug=True)
