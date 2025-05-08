from flask import Flask, render_template, request, redirect, url_for
import io
import pytesseract
from PIL import Image

app = Flask(__name__)

@app.route('/ocr', methods=['GET', 'POST'])
def ocr():
    extracted_text = ""
    error = ""
    if request.method == 'POST':
        if 'image' not in request.files:
            error = "No file part in the request"
            return render_template('index.html', extracted_text=extracted_text, error=error)
        file = request.files['image']
        if file.filename == '':
            error = "No file selected"
            return render_template('index.html', extracted_text=extracted_text, error=error)
        if file:
            try:
                img_bytes = file.read();
                img = Image.open(io.BytesIO(img_bytes))
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                custom_config = r'-l vie+eng'
                
                extracted_text = pytesseract.image_to_string(img, config=custom_config)
            except Exception as e:
                error = f"Failed to process image. Error: {str(e)}"
            return render_template('index.html', extracted_text=extracted_text, error=error)
    return render_template('index.html', extracted_text=extracted_text, error=error)

@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text():
    return render_template('speech-to-text.html', converted_text='')

if __name__ == '__main__':
    app.run(debug=True) 