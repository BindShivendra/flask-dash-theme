from datetime import datetime
from flask import current_app
from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

from app import login_manager


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permission is None:
            self.permission = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permission += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permission -= perm

    def reset_permission(self):
        self.permission = 0

    def has_permission(self, perm):
        return self.permission & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                          Permission.MODERATE],
            'Admin': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                      Permission.MODERATE, Permission.ADMIN]
        }

        default_role = 'User'
        for role in roles:
            r = Role.query.filter_by(name=role).first()
            if r is None:
                r = Role(name=role)
            r.reset_permission()
            for perm in roles[role]:
                r.add_permission(perm)
            r.default = (r.name == default_role)
            db.session.add(r)
        db.session.commit()

    def __repr__(self):
        return f'Role("{self.name}")'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(225), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_has = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    profile = db.relationship("Profile", uselist=False, backref="User")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.profile is None:
            self.profile = Profile(user_id=self.id)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_has = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_has, password)

    def generate_confimation_token(self, expiretion=3600):
        token = Token(current_app.config['SECRET_KEY'], expiretion)
        return token.dumps({'token': self.id}).decode('utf-8')

    def confirm(self, token):
        t = Token(current_app.config['SECRET_KEY'])
        try:
            data = t.loads(token.encode('utf-8'))
        except Exception:
            return False
        if data.get('token') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiretion=3600):
        token = Token(current_app.config['SECRET_KEY'])
        return token.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(self, new_password):
        t = Token(current_app.config['SECRET_KEY'])
        try:
            data = t.loads(new_password.encode('utf-8'))
        except Exception:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False

        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiretion):
        token = Token(current_app.config['SECRET_KEY'])
        return token.dumps(
            {'change_email': self.id,
                'new_email': new_email
             }).decode('utf-8')

    def change_email(self, token):
        t = Token(current_app.config['SECRET_KEY'])
        try:
            data = t.loads(token.encode('utf-8'))
        except Exception:
            return False
        if data.get('change_email') != self.id:
            return False
        if data.ger('new_email') is None:
            return False
        self.email = data.ger('new_email')
        db.session.add(self)
        return True

    # check permissions
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return f'User("{self.username}")'
    #  User(email='john@example.com', username='john', password='thispass')


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_admin(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    profile_image = db.Column(db.String(128))

    def __repr__(self):
        return f'Profile( "{self.name}" )'

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
