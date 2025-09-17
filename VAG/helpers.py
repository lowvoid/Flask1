import os ,secrets
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app

def safe_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return ext if ext in {'.jpg', '.jpeg', '.png', '.gif'} else ''


def save_picture(form_file, folder, size=None):
    filename = secure_filename(form_file.filename or '')
    ext = safe_extension(filename)
    if not ext:
        raise ValueError('Invalid image extension.')

    random_hex = secrets.token_hex(8)
    picture_name = random_hex + ext
    picture_path = os.path.join(current_app.root_path, folder, picture_name)

    os.makedirs(os.path.dirname(picture_path), exist_ok=True)

    i = Image.open(form_file)
    if size:
        i.thumbnail(size)
    i.save(picture_path)
    return picture_name

def delete_picture(picture_name, folder):
    if not picture_name or picture_name.startswith('default'):
        return
    picture_path = os.path.join(current_app.root_path, folder, picture_name)
    try:
        os.remove(picture_path)
    except OSError:
        pass
