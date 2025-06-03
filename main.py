from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import logging
import difflib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create static folder if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')
    print("Created static folder")

# Create Flask app with explicit static folder
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Debug directory structure and environment
print("Current working directory:", os.getcwd())
print("Static folder path:", app.static_folder)
print("Static folder absolute path:", os.path.abspath(app.static_folder))
print("Checking if static folder exists:", os.path.exists(app.static_folder))
if os.path.exists(app.static_folder):
    print("Files in static folder:", os.listdir(app.static_folder))

# Enhanced debugging for request handling
@app.before_request
def before_request():
    if request.path.startswith('/static/'):
        print(f"Static file requested: {request.path}")
        static_file = request.path.replace('/static/', '')
        file_path = os.path.join(app.static_folder, static_file)
        print(f"Looking for file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")

# Disable caching for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://aditi:1234@localhost/lost_and_found"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define models
class ReportedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    item_desc = db.Column(db.Text, nullable=False)
    date_lost = db.Column(db.Date, nullable=False)
    location_lost = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

class ClaimedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    item_desc = db.Column(db.Text, nullable=False)
    date_claimed = db.Column(db.Date, nullable=False)
    location_lost = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.String(9), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Direct CSS route
@app.route('/css')
def css():
    return app.send_static_file('styles.css')

# Test route with inline styles
@app.route('/test')
def test():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { background-color: #328e6e; color: white; font-family: Arial; padding: 30px; }
            h1 { text-align: center; }
            .container { background-color: white; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>Test Page</h1>
        <div class="container">
            <p>This is a test page with inline styles. If you can see this styled correctly (green background and white text in the body, with a white container), then your Flask server is working correctly.</p>
            <p>The issue is likely with how static files are being served.</p>
        </div>
    </body>
    </html>
    """

# Route for the login page
@app.route('/')
def index():
    return render_template('websiteskeleton.html')

# Route for the main options page
@app.route('/web2')
def web2():
    return render_template('web2.html')

# Route for reporting a lost item
@app.route('/report_item')
def report_item():
    return render_template('report_item.html')

# Route for claiming a lost item
@app.route('/claim_item')
def claim_item():
    return render_template('claim_item.html')

# Route for submitting a lost item report
@app.route('/submit_report', methods=['POST'])
def submit_report():
    try:
        # Get form data
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        date_lost = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        location = request.form.get('location')
        contact_email = request.form.get('contact_email')
        
        # Validate form data
        if not all([item_name, description, date_lost, location, contact_email]):
            flash("All fields are required", "error")
            return redirect(url_for('report_item'))

        # Create new reported item
        new_report = ReportedItem(
            item_name=item_name,
            item_desc=description,
            date_lost=date_lost,
            location_lost=location,
            contact_email=contact_email
        )
        
        # Add to database
        db.session.add(new_report)
        db.session.commit()
        
        flash("Your item has been reported successfully!", "success")
        return redirect(url_for('web2'))
    
    except Exception as e:
        logging.error(f"Error submitting report: {e}")
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for('report_item'))

# Route for submitting a claim
@app.route('/submit_claim', methods=['POST'])
def submit_claim():
    try:
        # Get form data
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        date_claimed = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        location = request.form.get('location')
        email = request.form.get('email')
        
        # Validate form data
        if not all([item_name, description, date_claimed, location, email]):
            flash("All fields are required", "error")
            return redirect(url_for('claim_item'))
        
        # Create new claimed item
        new_claim = ClaimedItem(
            item_name=item_name,
            item_desc=description,
            date_claimed=date_claimed,
            location_lost=location,
            email=email,
            status='pending'
        )
        
        # Add to database
        db.session.add(new_claim)
        db.session.commit()
        
        # Check for matching items in database
        reported_items = ReportedItem.query.all()
        
        match_found = False
        match_email = None
        
        for item in reported_items:
            # Check if item names match
            name_similarity = difflib.SequenceMatcher(None, item_name.lower(), item.item_name.lower()).ratio()
            
            # Check if descriptions are similar
            desc_similarity = difflib.SequenceMatcher(None, description.lower(), item.item_desc.lower()).ratio()
            
            # If both name and description are similar enough, it's a match
            if name_similarity > 0.7 and desc_similarity > 0.6:
                match_found = True
                match_email = item.contact_email
                
                # Update the claim status
                new_claim.status = 'matched'
                db.session.commit()
                break
        
        if match_found:
            message = "Match found! Please collect your item from the lost and found office. The owner has been notified."
            # In a real application, you would send an email to both the claimer and the item owner
        else:
            message = "No exact match found for your item. We will contact you via email if a match is made later."
        
        return render_template('match_result.html', message=message)
    
    except Exception as e:
        logging.error(f"Error submitting claim: {e}")
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for('claim_item'))

# Route for handling user login
@app.route('/login', methods=['POST'])
def login():
    try:
        full_name = request.form.get('fullName')
        reg_number = request.form.get('regNumber')
        email = request.form.get('email')
        
        # Validate inputs
        if not all([full_name, reg_number, email]):
            flash("All fields are required", "error")
            return redirect(url_for('index'))
        
        if not reg_number.isdigit() or len(reg_number) != 9:
            flash("Registration number must be 9 digits", "error")
            return redirect(url_for('index'))
        
        if "@" not in email:
            flash("Please enter a valid email", "error")
            return redirect(url_for('index'))
        
        # Check if user exists
        user = User.query.filter_by(reg_number=reg_number).first()
        
        if not user:
            # Create new user if not exists
            user = User(
                full_name=full_name,
                reg_number=reg_number,
                email=email
            )
            db.session.add(user)
        else:
            # Update existing user's data
            user.full_name = full_name
            user.email = email
            user.last_login = datetime.utcnow()
        
        db.session.commit()
        
        # Store user information in session
        session['full_name'] = full_name
        session['reg_number'] = reg_number
        session['email'] = email
        
        return redirect(url_for('web2'))
    
    except Exception as e:
        logging.error(f"Error during login: {e}")
        flash("An error occurred during login. Please try again.", "error")
        return redirect(url_for('index'))

# Route for logging out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Route for about us page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for contact and support page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Static files route
@app.route('/static/<path:filename>')
def custom_static(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)