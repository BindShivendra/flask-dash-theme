import os
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def generate_file_name(filename):
    formate = '%Y-%m-%d-%H-%f'
    now = datetime.now(timezone.utc).strftime(formate)
    return f"{filename.rsplit('.', 1)[0].lower()}-{now}.{filename.rsplit('.', 1)[1].lower()}"


def resize_image_and_save(image, path, username):
    small = 540, 540
    file_name = generate_file_name(secure_filename(image.filename))
    upload_dir = os.path.join(path, username)
    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)
    full_path = os.path.join(upload_dir, file_name)
    image.save(full_path)
    thumbnail_image = Image.open(full_path)
    thumbnail_image.thumbnail(small, Image.LANCZOS)
    thumbnail_image.save(full_path, optimize=True, quality=95)
    return full_path
