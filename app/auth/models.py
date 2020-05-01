from flask import current_app
from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import login_manager


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

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
        except:
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
        except:
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
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        if data.ger('new_email') is None:
            return False
        self.email = data.ger('new_email')
        db.session.add(self)
        return True

    def __repr__(self):
        return f'User("{self.username}")'
    #  User(email='john@example.com', username='john', password='thispass')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
