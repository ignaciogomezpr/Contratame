from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import qrcode
import base64
from io import BytesIO
import os
import mimetypes
from PIL import Image, ImageOps
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(100, 100), max_file_size=10240):
    with Image.open(image_path) as img:
        # Resize the image while maintaining the aspect ratio
        img = ImageOps.contain(img, max_size, method=Image.Resampling.LANCZOS)

        img_byte_arr = io.BytesIO()

        # Determine the image format and use it explicitly
        image_format = img.format if img.format else 'JPEG'  # Default to JPEG if format is unknown
        img.save(img_byte_arr, format=image_format)
        img_byte_arr = img_byte_arr.getvalue()

        # Check if the resulting image is too large
        if len(img_byte_arr) > max_file_size:
            return None

        return base64.b64encode(img_byte_arr).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        formatted_name = f"{first_name} {last_name}"
        phone = request.form.get('phone')
        email = request.form.get('email')
        company = request.form.get('company')
        notes = request.form.get('notes')
        image_file = request.files.get('image')
        weburl = request.form.get('weburl')
        # Remove line breaks and replace with spaces
        notes = notes.replace('\n', '\\n').replace('\r', '')

        base64_string = ""  # Default if no image is uploaded

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            if 'image' in mimetypes.guess_type(image_path)[0]:
                # Resize the image and check file size
                base64_string = resize_image(image_path, max_size=(100, 100), max_file_size=10240)
                if base64_string is None:
                    return "Image is too large", 400
            else:
                return "File is not an image", 400

        vCardString = f"BEGIN:VCARD\n" \
                      f"VERSION:3.0\n" \
                      f"FN:{formatted_name}\n" \
                      f"N:{last_name};{first_name};;;\n" \
                      f"ORG:{company}\n" \
                      f"TEL:{phone}\n" \
                      f"EMAIL:{email}\n" \
                      f"URL:{weburl}\n" \
                      f"NOTE:{notes}\n" \
                      f"PHOTO;ENCODING=b;TYPE=image/jpeg:{base64_string}\n" \
                      f"END:VCARD"

        qr = qrcode.QRCode(
            version=None,  # Manually set a version
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(vCardString)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return render_template('qrcode.html', qr_code=img_str)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
