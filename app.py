import os
import secrets
import sys
from datetime import datetime
from flask import Flask, request, g
from config import Config
from models import init_db
from utils.auth import login_manager, create_admin

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)

    # Init Flask-Login
    login_manager.init_app(app)

    # Init database
    init_db()

    # Create admin user if ADMIN_PASSWORD is set and no admin exists
    admin_pass = os.getenv('ADMIN_PASSWORD')
    if admin_pass:
        from models import get_db
        db = get_db()
        row = db.execute('SELECT COUNT(*) as c FROM admin_user').fetchone()
        db.close()
        if row['c'] == 0:
            create_admin(Config.ADMIN_USERNAME, admin_pass)
            print(f'Admin user "{Config.ADMIN_USERNAME}" created.')

    # Register blueprints
    from routes.public import public
    from routes.admin import admin
    from routes.api import api
    app.register_blueprint(public)
    app.register_blueprint(admin)
    app.register_blueprint(api)

    # Ensure drive folder exists
    os.makedirs(Config.DRIVE_FOLDER, exist_ok=True)

    # Jinja2 filters
    @app.template_filter('timestamp')
    def timestamp_filter(ts):
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    # --- Security middleware ---

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # CSRF token generation for forms
    @app.before_request
    def generate_csrf_token():
        if 'csrf_token' not in request.cookies:
            g.new_csrf_token = secrets.token_hex(32)
        else:
            g.new_csrf_token = None

    @app.after_request
    def set_csrf_cookie(response):
        if g.get('new_csrf_token'):
            response.set_cookie('csrf_token', g.new_csrf_token,
                                httponly=False, samesite='Lax')
        return response

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
