from flask import Flask, render_template_string, request, send_file
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
import io
import base64

app = Flask(__name__)

HTML = '''
<!doctype html>
<title>QR Generator Pro</title>
<style>
body { font-family: Arial; max-width: 600px; margin: 20px auto; padding: 20px }
input, button, select { padding: 10px; margin: 6px 0; width: 100%; box-sizing: border-box }
.tabs button { width: 49%; display: inline-block }
.tab { display: none; border: 1px solid #ddd; padding: 15px; margin-top: 10px }
.active { display: block }
</style>

<h2>QR Generator Pro</h2>
<div class="tabs">
  <button onclick="showTab('text')">Text/Link</button>
  <button onclick="showTab('vcard')">Business Card</button>
</div>

<div id="text" class="tab active">
<form method=post enctype=multipart/form-data>
  <input name=text placeholder="Enter link, text, WhatsApp number" required>
  <label>QR Color:</label>
  <input type=color name=color value="#000000">
  <label>Background Color:</label>
  <input type=color name=bgcolor value="#ffffff">
  <label>Center Logo (optional):</label>
  <input type=file name=logo accept="image/*">
  <button type=submit name=mode value=text>Generate QR</button>
</form>
</div>

<div id="vcard" class="tab">
<form method=post enctype=multipart/form-data>
  <input name=name placeholder="Full Name" required>
  <input name=phone placeholder="Phone: +91 9876543210" required>
  <input name=email placeholder="Email">
  <input name=company placeholder="Company/Shop Name">
  <input name=url placeholder="Website or Instagram">
  <label>QR Color:</label>
  <input type=color name=color value="#000000">
  <label>Background Color:</label>
  <input type=color name=bgcolor value="#ffffff">
  <button type=submit name=mode value=vcard>Generate vCard QR</button>
</form>
</div>

{% if img %}
<h3>Your QR:</h3>
<img src="data:image/png;base64,{{ img }}" width=300><br><br>
<a href="/download?data={{ img }}" download="my_qr.png">
  <button style="background:#4CAF50;color:white">Download QR</button>
</a>
{% endif %}

<script>
function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}
</script>
'''

def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

@app.route('/', methods=['GET', 'POST'])
def home():
    img_b64 = None
    if request.method == 'POST':
        # 4. vCard vs Simple text
        if request.form['mode'] == 'vcard':
            data = f"""BEGIN:VCARD
VERSION:3.0
FN:{request.form['name']}
TEL:{request.form['phone']}
EMAIL:{request.form.get('email','')}
ORG:{request.form.get('company','')}
URL:{request.form.get('url','')}
END:VCARD"""
        else:
            data = request.form['text']
        
        # 2. Colors
        fill = hex_to_rgb(request.form.get('color', '#000000'))
        back = hex_to_rgb(request.form.get('bgcolor', '#ffffff'))
        
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(image_factory=StyledPilImage, 
                           color_mask=SolidFillColorMask(back_color=back, front_color=fill))
        
        # 2. Add logo if uploaded
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((60, 60))
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, logo)
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_b64 = base64.b64encode(buf.getvalue()).decode()
    
    return render_template_string(HTML, img=img_b64)

# 1. Download button route
@app.route('/download')
def download():
    img_data = request.args.get('data')
    buf = io.BytesIO(base64.b64decode(img_data))
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='qr_code.png')

if __name__ == '__main__':
    app.run(debug=True)