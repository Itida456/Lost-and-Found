from flask import Flask
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lostfound.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from models import ReportedItem, ClaimedItem, User

with app.app_context():
    db.create_all()

from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
