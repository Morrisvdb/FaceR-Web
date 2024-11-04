from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv('.env')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['CACHE_TYPE'] = 'simple'
db = SQLAlchemy(app)
cache = Cache(app)