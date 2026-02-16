import bcrypt
from flask_login import LoginManager, UserMixin
from models import get_db

login_manager = LoginManager()
login_manager.login_view = 'admin.login'


class AdminUser(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    row = db.execute('SELECT * FROM admin_user WHERE id=?', (user_id,)).fetchone()
    db.close()
    if row:
        return AdminUser(row['id'], row['username'])
    return None


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_admin(username, password):
    db = get_db()
    pw_hash = hash_password(password)
    db.execute(
        'INSERT OR REPLACE INTO admin_user (id, username, password_hash) VALUES (1, ?, ?)',
        (username, pw_hash)
    )
    db.commit()
    db.close()
