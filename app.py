from flask import Flask, request, render_template_string
from io import BytesIO
import qrcode
import base64
from PIL import Image

app = Flask(__name__)

HTML = '''
<!doctype html>
<html>
<head>
    <title>QR Code Generator - NIT Meghalaya</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
        h2 { color: #333; }
        input[type=text] { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        input[type=file] { margin: 10px 0; }
        button { background: #0066cc; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #0052a3; }
        img { margin: 20px 0; border: 1px solid #ddd; padding: 10px; }
        a { display: inline-block; margin-top: 10px; background: #28a745; color: white; padding: 10px 15px; text-decoration: none; }
        a:hover { background: #218838; }
    </style>
</head>
<body>
    <h2>QR Code Generator - NIT Meghalaya</h2>
    <form method=post enctype=multipart/form-data>
        <label>Text or URL:</label><br>
        <input type=text name=text placeholder="Enter text or URL" required><br>
        <label>Logo (optional):</label><br>
        <input type=file name=logo accept="image/*"><br>
        <button type=submit>Generate QR</button>
    </form>
    {% if img %}
        <h3>Your QR Code:</h3>
        <img src="data:image/png;base64,{{ img }}" alt="QR Code">
        <br>
        <a download="qr-code.png" href="data:image/png;base64,{{ img }}">Download QR</a>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        logo_file = request.files.get('logo')
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        if logo_file and logo_file.filename:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((60, 60))
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, logo)
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        
        return render_template_string(HTML, img=img_b64)
    
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)
