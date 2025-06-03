from flask import Flask
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database - Use MySQL for deployment
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://aditi:1234@localhost/lost_and_found"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Import models (do this after db is initialized)
from models import ReportedItem, ClaimedItem, User

# Initialize database
with app.app_context():
    db.create_all()

# Import routes after app and db are created
from routes import *

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
