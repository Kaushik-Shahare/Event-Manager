from flask import Flask


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False

app.secret_key = 'SECRET_KEY'

from modules import *
from .models import *
from .authentication import *
from .user import *
from .event import *
