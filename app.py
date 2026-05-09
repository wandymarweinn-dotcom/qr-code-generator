from flask import Flask, request, render_template_string
from io import BytesIO
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import base64
from PIL import Image

app = Flask(__name__)

HTML = '''
<!doctype html>
<html>
<head>
    <title>QR Business Card Generator - NIT Meghalaya</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
       .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { color: #0A66C2; margin-top: 0; }
        label { display: block; margin-top: 15px; font-weight: bold; color: #333; }
        input[type=text], input[type=color] { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ddd; border-radius: 6px; }
        input[type=color] { height: 50px; cursor: pointer; }
        input[type=file] { margin: 8px 0; }
       .row { display: flex; gap: 15px; }
       .col { flex: 1; }
        button { background: #0A66C2; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; margin-top: 20px; width: 100%; }
        button:hover { background: #004182; }
       .qr-box { text-align: center; margin-top: 30px; }
        img { margin: 20px 0; border: 1px solid #ddd; padding: 15px; background: white; border-radius: 8px; }
       .download { display: inline-block; margin-top: 10px; background: #28a745; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="card">
        <h2>QR Business Card Generator - NIT Meghalaya</h2>
        <form method=post enctype=multipart/form-data>
            <label>Name:</label>
            <input type=text name=name placeholder="John Doe" value="{{ request.form.name or '' }}">
            
            <label>Place / Company:</label>
            <input type=text name=place placeholder="NIT Meghalaya" value="{{ request.form.place or '' }}">
            
            <label>Instagram:</label>
            <input type=text name=instagram placeholder="@username" value="{{ request.form.instagram or '' }}">
            
            <label>Phone / WhatsApp:</label>
            <input type=text name=phone placeholder="+91 9876543210" value="{{ request.form.phone or '' }}">
            
            <label>Website / URL:</label>
            <input type=text name=url placeholder="https://example.com" value="{{ request.form.url or '' }}">
            
            <div class="row">
                <div class="col">
                    <label>QR Color:</label>
                    <input type=color name=qr_color value="{{ request.form.qr_color or '#000000' }}">
                </div>
                <div class="col">
                    <label>Background Color:</label>
                    <input type=color name=bg_color value="{{ request.form.bg_color or '#FFFFFF' }}">
                </div>
            </div>
            
            <label>Logo (optional):</label>
            <input type=file name=logo accept="image/*">
            
            <button type=submit>Generate QR Business Card</button>
        </form>
        
        {% if qr_img %}
        <div class="qr-box">
            <h3>Your QR Code:</h3>
            <img src="data:image/png;base64,{{ qr_img }}">
            <br>
            <a class="download" href="data:image/png;base64,{{ qr_img }}" download="business-card-qr.png">Download PNG</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_img = None
    if request.method == 'POST':
        name = request.form.get('name', '')
        place = request.form.get('place', '')
        instagram = request.form.get('instagram', '')
        phone = request.form.get('phone', '')
        url = request.form.get('url', '')
        qr_color = request.form.get('qr_color', '#000000')
        bg_color = request.form.get('bg_color', '#FFFFFF')
        
        # Build vCard data for business card
        vcard_data = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
ORG:{place}
TEL:{phone}
URL:{url}
NOTE:Instagram: {instagram}
END:VCARD"""
        
        data = vcard_data if name else url
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SolidFillColorMask(
                front_color=hex_to_rgb(qr_color),
                back_color=hex_to_rgb(bg_color)
            )
        )
        
        # Add logo if uploaded
        logo = request.files.get('logo')
        if logo and logo.filename:
            logo_img = Image.open(logo.stream)
            logo_img = logo_img.convert("RGBA")
            
            # Resize logo
            basewidth = 80
            wpercent = (basewidth / float(logo_img.size[0]))
            hsize = int((float(logo_img.size[1]) * float(wpercent)))
            logo_img = logo_img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
            
            # Paste logo in center
            pos = ((img.size[0] - logo_img.size[0]) // 2, (img.size[1] - logo_img.size[1]) // 2)
            img.paste(logo_img, pos, logo_img)
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        qr_img = base64.b64encode(buf.getvalue()).decode()
    
    return render_template_string(HTML, qr_img=qr_img)

if __name__ == '__main__':
    app.run()
