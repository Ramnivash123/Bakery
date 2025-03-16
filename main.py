from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite (change for MySQL/PostgreSQL)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ajbscajlcbaljcnalndc'

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords in real applications

# Database Model
class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    fav_item = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=False)

from datetime import datetime
class Bookings(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(100), nullable=False)
    item=db.Column(db.String, nullable=False)
    quantity=db.Column(db.String, nullable=False)
    delivery_date=db.Column(db.Date, nullable=False)
    current_date=db.Column(db.Date, nullable=False, default=datetime.utcnow)
    mobile_no=db.Column(db.Integer, nullable=False)
    address=db.Column(db.String, nullable=False)

# Create database tables before running
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]  # Hash passwords in real applications
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for("signup"))

        # Insert into database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("cakes"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("signin"))

    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("signin"))


@app.route("/cakes", methods=["GET", "POST"])
def cakes():
    if "user_id" not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for("signin"))

    # Fetch all cake reviews from the database
    ratings = Ratings.query.all()
    
    return render_template("cakes.html", username=session.get("username"), ratings=ratings)



# Route to Handle Rating Submission
@app.route("/submit_rating", methods=["POST"])
def submit_rating():
    if "user_id" not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for("signin"))

    username = session.get("username")
    fav_item = request.form.get("fav_item")
    rating = request.form.get("rating")
    feedback = request.form.get("feedback")

    if not fav_item or not rating or not feedback:
        flash("All fields are required!", "danger")
        return redirect(url_for("cakes"))

    new_rating = Ratings(username=username, fav_item=fav_item, rating=int(rating), feedback=feedback)
    db.session.add(new_rating)
    db.session.commit()

    flash("Your rating has been submitted!", "success")
    return redirect(url_for("cakes"))

# Route to display the booking form
@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    if 'username' not in session:
        return redirect(url_for('signin'))  # Redirect to login if user is not logged in

    if request.method == 'POST':
        # Get form data
        username = session['username']
        item = request.form['item']
        quantity = request.form['quantity']
        delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date()
        mobile_no = request.form['mobile_no']
        address = request.form['address']

        # Create a new booking record
        new_booking = Bookings(
            username=username,
            item=item,
            quantity=quantity,
            delivery_date=delivery_date,
            mobile_no=mobile_no,
            address=address
        )

        # Add to database
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('bookings'))  # Redirect back to the bookings page after submission

    # Fetch all bookings from the database
    all_bookings = Bookings.query.all()

    # Render the booking form and all bookings for GET requests
    return render_template('bookings.html', bookings=all_bookings)

# Route to delete a booking
@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'username' not in session:
        return redirect(url_for('signin'))  # Redirect to login if user is not logged in

    # Find the booking by ID
    booking = Bookings.query.get_or_404(booking_id)

    # Ensure the booking belongs to the logged-in user
    if booking.username == session['username']:
        db.session.delete(booking)
        db.session.commit()

    return redirect(url_for('bookings'))


if __name__ == "__main__":
    app.run(debug=True)