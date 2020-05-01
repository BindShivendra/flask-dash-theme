from local_settings import LocalConfig
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'jkhjkxf677ern^&56jnfvd98*&njfg4'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in [
        'true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[Dash]'
    MAIL_SENDER = 'Dash Admin <dash@example.com>'
    ADMIN = os.environ.get('ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'dev.sqlite')
    LOG_TO_STDOUT = True
    MAIL_SERVER = LocalConfig.EMAIL_HOST
    MAIL_PORT = LocalConfig.EMAIL_PORT
    MAIL_USE_TLS = LocalConfig.EMAIL_USE_TLS
    MAIL_USERNAME = LocalConfig.EMAIL_HOST_USER
    MAIL_PASSWORD = LocalConfig.SENDGRID_API_KEY
    MAIL_DEFAULT_SENDER = LocalConfig.MAIL_DEFAULT_SENDER
    MAIL_SUBJECT_PREFIX = '[Dash]'
    MAIL_SENDER = 'Dash Admin <dash@email.com>'


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL') or 'sqlite://'  # DB not required
    LOG_TO_STDOUT = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or os.path.join(basedir, 'production.sqlite')
    LOG_TO_STDOUT = False


config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'prod': ProductionConfig,

    'default': DevelopmentConfig
}
