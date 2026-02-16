import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config


def allowed_file(filename, file_type='image'):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if file_type == 'image':
        return ext in Config.ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return ext in Config.ALLOWED_VIDEO_EXTENSIONS
    return False


def save_upload(file, subfolder='uploads'):
    filename = secure_filename(file.filename)
    if not filename:
        return None

    # Add unique prefix to avoid collisions
    ext = filename.rsplit('.', 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"

    dest_dir = os.path.join(Config.UPLOAD_FOLDER)
    os.makedirs(dest_dir, exist_ok=True)

    filepath = os.path.join(dest_dir, unique_name)
    file.save(filepath)

    return f'uploads/{unique_name}'


def make_thumbnail(filepath, size=(300, 300)):
    try:
        with Image.open(filepath) as img:
            img.thumbnail(size)
            thumb_path = filepath.rsplit('.', 1)[0] + '_thumb.' + filepath.rsplit('.', 1)[1]
            img.save(thumb_path)
            return thumb_path
    except Exception:
        return None
