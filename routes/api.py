import json
import os
import re
from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import get_db, set_content, get_content, check_rate_limit, record_login_attempt
from utils.email import send_contact_email
from utils.uploads import save_upload, allowed_file
from config import Config

api = Blueprint('api', __name__, url_prefix='/api')

# Max input lengths
_MAX_NAME = 200
_MAX_EMAIL = 254
_MAX_SUBJECT = 500
_MAX_MESSAGE = 5000


@api.route('/contact', methods=['POST'])
def contact_submit():
    data = request.get_json() or request.form

    # Honeypot check
    if data.get('website', ''):
        return jsonify({'status': 'ok'})  # Silent reject

    # Rate limit: 10 contact submissions per IP per 10 minutes
    ip = request.remote_addr or '0.0.0.0'
    if check_rate_limit(ip, window_seconds=600, max_attempts=10):
        return jsonify({'status': 'error', 'message': 'Too many submissions. Please try again later.'}), 429

    name = data.get('name', '').strip()[:_MAX_NAME]
    email = data.get('email', '').strip()[:_MAX_EMAIL]
    subject = data.get('subject', '').strip()[:_MAX_SUBJECT]
    message = data.get('message', '').strip()[:_MAX_MESSAGE]

    if not name or not email or not message:
        return jsonify({'status': 'error', 'message': 'Please fill in all required fields.'}), 400

    # Basic email format validation
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return jsonify({'status': 'error', 'message': 'Please enter a valid email address.'}), 400

    # Save to DB
    db = get_db()
    db.execute(
        'INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
        (name, email, subject, message)
    )
    db.commit()
    db.close()

    # Record for rate limiting
    record_login_attempt(ip)

    # Best-effort email
    send_contact_email(name, email, subject, message)

    return jsonify({'status': 'ok', 'message': 'Message sent! Thank you.'})


@api.route('/save-content', methods=['POST'])
@login_required
def save_content():
    data = request.get_json()
    page = data.get('page')
    section = data.get('section')
    content = data.get('content')

    if not page or not section:
        return jsonify({'status': 'error', 'message': 'Missing page or section'}), 400

    set_content(page, section, content)
    return jsonify({'status': 'ok'})


@api.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    # Determine file type
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext in Config.ALLOWED_IMAGE_EXTENSIONS:
        file_type = 'image'
        if request.content_length and request.content_length > Config.MAX_IMAGE_SIZE:
            return jsonify({'status': 'error', 'message': 'Image too large (max 10MB)'}), 400
    elif ext in Config.ALLOWED_VIDEO_EXTENSIONS:
        file_type = 'video'
        if request.content_length and request.content_length > Config.MAX_VIDEO_SIZE:
            return jsonify({'status': 'error', 'message': 'Video too large (max 150MB)'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400

    path = save_upload(file)
    if not path:
        return jsonify({'status': 'error', 'message': 'Upload failed'}), 500

    return jsonify({'status': 'ok', 'path': path})


# --- CRUD endpoints for list tables ---

@api.route('/gallery/add', methods=['POST'])
@login_required
def gallery_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM gallery_images').fetchone()[0]
    db.execute(
        'INSERT INTO gallery_images (filename, alt_text, sort_order) VALUES (?, ?, ?)',
        (data['filename'], data.get('alt_text', ''), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/gallery/delete', methods=['POST'])
@login_required
def gallery_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM gallery_images WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/gallery/reorder', methods=['POST'])
@login_required
def gallery_reorder():
    data = request.get_json()
    db = get_db()
    for i, item_id in enumerate(data['order']):
        db.execute('UPDATE gallery_images SET sort_order=? WHERE id=?', (i, item_id))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/gallery/update', methods=['POST'])
@login_required
def gallery_update():
    data = request.get_json()
    db = get_db()
    db.execute('UPDATE gallery_images SET alt_text=? WHERE id=?', (data.get('alt_text', ''), data['id']))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/shows/add', methods=['POST'])
@login_required
def shows_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM shows').fetchone()[0]
    db.execute(
        'INSERT INTO shows (show_date, venue, city, info_url, sort_order) VALUES (?, ?, ?, ?, ?)',
        (data.get('show_date', ''), data.get('venue', ''), data.get('city', ''),
         data.get('info_url', ''), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/shows/update', methods=['POST'])
@login_required
def shows_update():
    data = request.get_json()
    db = get_db()
    db.execute(
        'UPDATE shows SET show_date=?, venue=?, city=?, info_url=? WHERE id=?',
        (data.get('show_date', ''), data.get('venue', ''), data.get('city', ''),
         data.get('info_url', ''), data['id'])
    )
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/shows/delete', methods=['POST'])
@login_required
def shows_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM shows WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/videos/add', methods=['POST'])
@login_required
def videos_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM live_videos').fetchone()[0]
    db.execute(
        'INSERT INTO live_videos (filename, title, location, sort_order) VALUES (?, ?, ?, ?)',
        (data['filename'], data.get('title', ''), data.get('location', ''), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/videos/delete', methods=['POST'])
@login_required
def videos_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM live_videos WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/videos/reorder', methods=['POST'])
@login_required
def videos_reorder():
    data = request.get_json()
    db = get_db()
    for i, item_id in enumerate(data['order']):
        db.execute('UPDATE live_videos SET sort_order=? WHERE id=?', (i, item_id))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/releases/add', methods=['POST'])
@login_required
def releases_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM releases').fetchone()[0]
    db.execute(
        'INSERT INTO releases (title, cover_image, bandcamp_url, sort_order) VALUES (?, ?, ?, ?)',
        (data['title'], data.get('cover_image', ''), data.get('bandcamp_url', ''), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/releases/delete', methods=['POST'])
@login_required
def releases_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM releases WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/releases/reorder', methods=['POST'])
@login_required
def releases_reorder():
    data = request.get_json()
    db = get_db()
    for i, item_id in enumerate(data['order']):
        db.execute('UPDATE releases SET sort_order=? WHERE id=?', (i, item_id))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/tracks/add', methods=['POST'])
@login_required
def tracks_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM soundcloud_tracks').fetchone()[0]
    db.execute(
        'INSERT INTO soundcloud_tracks (title, url, sort_order) VALUES (?, ?, ?)',
        (data['title'], data.get('url', ''), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/tracks/delete', methods=['POST'])
@login_required
def tracks_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM soundcloud_tracks WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/lighting-shows/add', methods=['POST'])
@login_required
def lighting_shows_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM lighting_shows').fetchone()[0]
    db.execute(
        'INSERT INTO lighting_shows (role, title, venue, location, links_json, sort_order) VALUES (?, ?, ?, ?, ?, ?)',
        (data.get('role', ''), data['title'], data.get('venue', ''),
         data.get('location', ''), json.dumps(data.get('links', [])), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/lighting-shows/update', methods=['POST'])
@login_required
def lighting_shows_update():
    data = request.get_json()
    db = get_db()
    db.execute(
        'UPDATE lighting_shows SET role=?, title=?, venue=?, location=?, links_json=? WHERE id=?',
        (data.get('role', ''), data['title'], data.get('venue', ''),
         data.get('location', ''), json.dumps(data.get('links', [])), data['id'])
    )
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/lighting-shows/delete', methods=['POST'])
@login_required
def lighting_shows_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM lighting_shows WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/lighting-photos/add', methods=['POST'])
@login_required
def lighting_photos_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM lighting_photos').fetchone()[0]
    db.execute(
        'INSERT INTO lighting_photos (filename, alt_text, sort_order) VALUES (?, ?, ?)',
        (data['filename'], data.get('alt_text', ''), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/lighting-photos/delete', methods=['POST'])
@login_required
def lighting_photos_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM lighting_photos WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/archive/add', methods=['POST'])
@login_required
def archive_add():
    data = request.get_json()
    db = get_db()
    db.execute(
        'INSERT INTO archive_articles (year, month_day, title, url, category) VALUES (?, ?, ?, ?, ?)',
        (data.get('year', 2024), data.get('month_day', ''), data['title'],
         data.get('url', ''), data.get('category', ''))
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/archive/update', methods=['POST'])
@login_required
def archive_update():
    data = request.get_json()
    db = get_db()
    db.execute(
        'UPDATE archive_articles SET year=?, month_day=?, title=?, url=?, category=? WHERE id=?',
        (data.get('year', 2024), data.get('month_day', ''), data['title'],
         data.get('url', ''), data.get('category', ''), data['id'])
    )
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/archive/delete', methods=['POST'])
@login_required
def archive_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM archive_articles WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/blog-posts/add', methods=['POST'])
@login_required
def blog_posts_add():
    data = request.get_json()
    db = get_db()
    max_order = db.execute('SELECT COALESCE(MAX(sort_order), 0) FROM blog_posts').fetchone()[0]
    db.execute(
        'INSERT INTO blog_posts (title, url, excerpt, category, date_display, sort_order) VALUES (?, ?, ?, ?, ?, ?)',
        (data['title'], data.get('url', ''), data.get('excerpt', ''),
         data.get('category', ''), data.get('date_display', ''), max_order + 1)
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': row_id})


@api.route('/blog-posts/update', methods=['POST'])
@login_required
def blog_posts_update():
    data = request.get_json()
    db = get_db()
    db.execute(
        'UPDATE blog_posts SET title=?, url=?, excerpt=?, category=?, date_display=? WHERE id=?',
        (data['title'], data.get('url', ''), data.get('excerpt', ''),
         data.get('category', ''), data.get('date_display', ''), data['id'])
    )
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/blog-posts/delete', methods=['POST'])
@login_required
def blog_posts_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM blog_posts WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/messages/mark-read', methods=['POST'])
@login_required
def messages_mark_read():
    data = request.get_json()
    db = get_db()
    db.execute('UPDATE contact_messages SET is_read=1 WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


@api.route('/messages/delete', methods=['POST'])
@login_required
def messages_delete():
    data = request.get_json()
    db = get_db()
    db.execute('DELETE FROM contact_messages WHERE id=?', (data['id'],))
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})
