from flask import Flask, render_template, request, redirect, url_for
import io
import pytesseract
from PIL import Image

import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile

from pdf2image import convert_from_path

app = Flask(__name__)

# using PyTesseract & Tesseract-OCR
@app.route('/ocr', methods=['GET', 'POST'])
def ocr():
    extracted_text = ""
    error = ""
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if request.method == 'POST':
        custom_config = r'-l ' + request.form.get('lang')
        if 'image' not in request.files:
            error = "No file part in the request"
            return render_template('index.html', extracted_text=extracted_text, error=error)
        file = request.files['image']
        if file.filename == '':
            error = "No file selected"
            return render_template('index.html', extracted_text=extracted_text, error=error)
        if os.path.splitext(file.filename)[1].lower() == '.pdf':
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                    file.save(tmp.name)
                    pdf_path = tmp.name
                pages = convert_from_path(pdf_path, 500, poppler_path=r'C:\Users\Admin\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin')
                for i, page_data in enumerate(pages):
                    extracted_text = extracted_text + pytesseract.image_to_string(page_data, config=custom_config) + '\n'
                os.unlink(pdf_path)
            except Exception as e:
                error = f'Failed to process image. Error: {str(e)}'
            return render_template('index.html', extracted_text=extracted_text, error=error)
        else:
            try:
                img_bytes = file.read();
                img = Image.open(io.BytesIO(img_bytes))
                extracted_text = pytesseract.image_to_string(img, config=custom_config)
            except Exception as e:
                error = f'Failed to process image. Error: {str(e)}'
            return render_template('index.html', extracted_text=extracted_text, error=error)
    return render_template('index.html', extracted_text=extracted_text, error=error)
# using SpeechRecognition
@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text():
    recognized_text = ""
    error = ""
    if request.method == 'POST':
        if 'record' not in request.files:
            error = "No audio record part in the request"
            return render_template('index.html', recognized_text=recognized_text, error=error)
        file = request.files['record']
        if file.filename == '':
            error = "No file selected"
            return render_template('speech-to-text.html', recognized_text=recognized_text, error=error)
        if file:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                    file.save(tmp.name)
                    audio_path = tmp.name
                audio_text = os.path.splitext(audio_path)[1].lower()
                if audio_text != '.wav':
                    sound = AudioSegment.from_file(audio_path)
                    AudioSegment.converter = r'C:\Users\Admin\Downloads\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe';
                    wav_path = audio_path + ".wav"
                    sound.export(wav_path, format="wav")
                    os.unlink(audio_path)
                    audio_path = wav_path
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio_data = recognizer.record(source)
                    recognized_text = recognizer.recognize_google(audio_data, language=request.form.get('lang'))
                os.unlink(audio_path)
            except sr.UnknownValueError as e:
                error = f"Couldn't specify audio value. Error: {str(e)}"
            except sr.RequestError as e:
                error = f"Couldn't request results from Google Speech Recognition"
            except Exception as e:
                error = f"Failed to process audio file. Error: {str(e)}"
    return render_template('speech-to-text.html', recognized_text=recognized_text, error=error)

if __name__ == '__main__':
    app.run(debug=True) 