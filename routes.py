import difflib
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session
import logging
from app import app, db
from models import ReportedItem, ClaimedItem, User

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

@app.route('/submit_report', methods=['POST'])
def submit_report():
    try:
        # Get form data
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        date_lost = request.form.get('date')
        location = request.form.get('location')
        contact_email = request.form.get('contact_email')

        print("Received form data:")
        print(item_name, description, date_lost, location, contact_email)

        if not all([item_name, description, date_lost, location, contact_email]):
            flash("All fields are required", "error")
            return redirect(url_for('report_item'))

        # Convert date
        date_lost = datetime.strptime(date_lost, '%Y-%m-%d').date()

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
        print("Item successfully saved to the database.")

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