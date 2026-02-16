import json
import os
from urllib.parse import urlparse
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from models import get_db, get_content, set_content, get_rows, get_unread_count, \
    check_rate_limit, record_login_attempt
from utils.auth import AdminUser, check_password
from utils.uploads import save_upload, allowed_file
from config import Config

admin = Blueprint('admin', __name__, url_prefix='/admin')


def _is_safe_redirect(target):
    """Prevent open redirect by only allowing relative paths on same host."""
    if not target:
        return False
    parsed = urlparse(target)
    return parsed.scheme == '' and parsed.netloc == ''


@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        ip = request.remote_addr or '0.0.0.0'

        # Rate limiting: block after 5 failed attempts in 5 minutes
        if check_rate_limit(ip):
            flash('Too many login attempts. Try again in a few minutes.', 'error')
            return render_template('admin/login.html'), 429

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        db = get_db()
        row = db.execute('SELECT * FROM admin_user WHERE username=?', (username,)).fetchone()
        db.close()

        if row and check_password(password, row['password_hash']):
            user = AdminUser(row['id'], row['username'])
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if _is_safe_redirect(next_page):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))

        record_login_attempt(ip)
        flash('Invalid credentials', 'error')

    return render_template('admin/login.html')


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@admin.route('/')
@login_required
def dashboard():
    unread = get_unread_count()
    pages = [
        {'name': 'About', 'url': url_for('admin.edit_page', page='about')},
        {'name': 'Contact', 'url': url_for('admin.edit_page', page='contact')},
        {'name': 'Gallery', 'url': url_for('admin.edit_gallery')},
        {'name': 'Live', 'url': url_for('admin.edit_live')},
        {'name': 'Music', 'url': url_for('admin.edit_music')},
        {'name': 'Blog', 'url': url_for('admin.edit_page', page='blog')},
        {'name': 'Shop', 'url': url_for('admin.edit_page', page='shop')},
        {'name': 'Lighting', 'url': url_for('admin.edit_lighting')},
        {'name': 'Archive', 'url': url_for('admin.edit_archive')},
        {'name': 'Index / Home', 'url': url_for('admin.edit_page', page='index')},
        {'name': 'Drive', 'url': url_for('admin.drive')},
    ]
    return render_template('admin/dashboard.html', pages=pages, unread=unread)


@admin.route('/edit/<page>')
@login_required
def edit_page(page):
    content = {}
    if page == 'about':
        content['bio'] = get_content('about', 'bio', {'html': ''})
        content['stage_bio'] = get_content('about', 'stage_bio', {'html': ''})
        content['skills'] = get_content('about', 'skills', [])
        content['credits'] = get_content('about', 'credits', [])
    elif page == 'index':
        content['nav_links'] = get_content('index', 'nav_links', [])
        content['social_links'] = get_content('index', 'social_links', [])
        content['mobile_links'] = get_content('index', 'mobile_links', [])
    elif page == 'shop':
        content['shopify_url'] = get_content('shop', 'shopify_url', None)
    elif page == 'contact':
        content['booking_email'] = get_content('contact', 'booking_email', 'booking@emme-em.me')
    elif page == 'blog':
        content['posts'] = get_rows('blog_posts')

    return render_template('admin/edit_page.html', page=page, content=content)


@admin.route('/gallery')
@login_required
def edit_gallery():
    images = get_rows('gallery_images')
    return render_template('admin/edit_gallery.html', images=images)


@admin.route('/live')
@login_required
def edit_live():
    shows = get_rows('shows')
    videos = get_rows('live_videos')
    return render_template('admin/edit_live.html', shows=shows, videos=videos)


@admin.route('/music')
@login_required
def edit_music():
    releases = get_rows('releases')
    tracks = get_rows('soundcloud_tracks')
    wip = get_content('music', 'wip', {'title': '', 'cover': '', 'url': ''})
    listen_links = get_content('music', 'listen_links', [])
    return render_template('admin/edit_music.html', releases=releases,
                           tracks=tracks, wip=wip, listen_links=listen_links)


@admin.route('/lighting')
@login_required
def edit_lighting():
    shows = get_rows('lighting_shows')
    for show in shows:
        if isinstance(show.get('links_json'), str):
            show['links'] = json.loads(show['links_json'])
        else:
            show['links'] = []
    photos = get_rows('lighting_photos')
    return render_template('admin/edit_lighting.html', shows=shows, photos=photos)


@admin.route('/archive')
@login_required
def edit_archive():
    articles = get_rows('archive_articles', order_by='year DESC, id')
    return render_template('admin/edit_archive.html', articles=articles)


@admin.route('/messages')
@login_required
def messages():
    db = get_db()
    msgs = db.execute('SELECT * FROM contact_messages ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/messages.html', messages=[dict(m) for m in msgs])


# --- File Manager (Drive) ---

def _safe_drive_path(subpath):
    """Resolve subpath inside DRIVE_FOLDER, rejecting path traversal."""
    base = os.path.realpath(Config.DRIVE_FOLDER)
    target = os.path.realpath(os.path.join(base, subpath))
    if not target.startswith(base):
        return None
    return target


def _format_size(size_bytes):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size_bytes < 1024:
            return f'{size_bytes:.1f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.1f} TB'


@admin.route('/drive')
@admin.route('/drive/<path:subpath>')
@login_required
def drive(subpath=''):
    target = _safe_drive_path(subpath)
    if not target or not os.path.isdir(target):
        flash('Folder not found', 'error')
        return redirect(url_for('admin.drive'))

    entries = []
    for name in sorted(os.listdir(target)):
        if name.startswith('.'):
            continue
        full = os.path.join(target, name)
        stat = os.stat(full)
        entries.append({
            'name': name,
            'is_dir': os.path.isdir(full),
            'size': _format_size(stat.st_size) if os.path.isfile(full) else '',
            'modified': stat.st_mtime,
            'path': os.path.join(subpath, name) if subpath else name,
        })
    # Sort: folders first, then files
    entries.sort(key=lambda e: (not e['is_dir'], e['name'].lower()))

    # Breadcrumb trail
    parts = subpath.strip('/').split('/') if subpath else []
    breadcrumbs = []
    for i, part in enumerate(parts):
        breadcrumbs.append({
            'name': part,
            'path': '/'.join(parts[:i + 1])
        })

    return render_template('admin/drive.html', entries=entries, subpath=subpath,
                           breadcrumbs=breadcrumbs)


@admin.route('/drive-download/<path:subpath>')
@login_required
def drive_download(subpath):
    target = _safe_drive_path(subpath)
    if not target or not os.path.isfile(target):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    return send_file(target, as_attachment=True)


@admin.route('/drive-upload', methods=['POST'])
@login_required
def drive_upload():
    subpath = request.form.get('path', '')
    target_dir = _safe_drive_path(subpath)
    if not target_dir or not os.path.isdir(target_dir):
        return jsonify({'status': 'error', 'message': 'Invalid folder'}), 400

    uploaded = request.files.getlist('files')
    if not uploaded:
        return jsonify({'status': 'error', 'message': 'No files provided'}), 400

    saved = []
    for f in uploaded:
        if not f.filename:
            continue
        # Sanitize filename: keep only safe chars
        safe_name = ''.join(c for c in f.filename if c.isalnum() or c in '._- ')
        if not safe_name:
            safe_name = 'upload'
        dest = os.path.join(target_dir, safe_name)
        # Don't overwrite — add suffix
        if os.path.exists(dest):
            base, ext = os.path.splitext(safe_name)
            i = 1
            while os.path.exists(dest):
                dest = os.path.join(target_dir, f'{base}_{i}{ext}')
                i += 1
        f.save(dest)
        saved.append(safe_name)

    return jsonify({'status': 'ok', 'files': saved})


@admin.route('/drive-mkdir', methods=['POST'])
@login_required
def drive_mkdir():
    data = request.get_json()
    subpath = data.get('path', '')
    name = data.get('name', '').strip()
    if not name or '/' in name or '..' in name:
        return jsonify({'status': 'error', 'message': 'Invalid folder name'}), 400

    parent = _safe_drive_path(subpath)
    if not parent or not os.path.isdir(parent):
        return jsonify({'status': 'error', 'message': 'Parent folder not found'}), 400

    new_dir = os.path.join(parent, name)
    if os.path.exists(new_dir):
        return jsonify({'status': 'error', 'message': 'Already exists'}), 400

    os.makedirs(new_dir)
    return jsonify({'status': 'ok'})


@admin.route('/drive-delete', methods=['POST'])
@login_required
def drive_delete():
    data = request.get_json()
    subpath = data.get('path', '')
    target = _safe_drive_path(subpath)
    if not target:
        return jsonify({'status': 'error', 'message': 'Invalid path'}), 400

    base = os.path.realpath(Config.DRIVE_FOLDER)
    if target == base:
        return jsonify({'status': 'error', 'message': 'Cannot delete root'}), 400

    if os.path.isfile(target):
        os.remove(target)
    elif os.path.isdir(target):
        import shutil
        shutil.rmtree(target)
    else:
        return jsonify({'status': 'error', 'message': 'Not found'}), 404

    return jsonify({'status': 'ok'})
