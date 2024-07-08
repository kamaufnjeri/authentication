import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    random_key = os.urandom(24).hex()
    SECRET_KEY = os.environ.get('SECRET_KEY') or random_key
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or random_key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'test.db')
