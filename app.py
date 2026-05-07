from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secretkey"

# Database connection
try:
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="inocrypt"
    )
    mycursor = database.cursor(dictionary=True)
    
    # Ensure the user table exists
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255)
        )
    """)
    
    # Ensure the ino_tb table exists for registration inquiries
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS ino_tb (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Full_Name VARCHAR(255),
            Email_Address VARCHAR(255),
            Contact_Number VARCHAR(255),
            Skype VARCHAR(255)
        )
    """)
    database.commit()
except mysql.connector.Error as err:
    print(f"Database error: {err}")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="inocrypt"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            first_name = request.form['First name']
            last_name = request.form['Last name']
            username = request.form['username']
            password = request.form['Password']
            confirm_password = request.form['Confirm Password']
            
            if password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for('signup'))

            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Check if user already exists
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            if cursor.fetchone():
                db.close()
                flash("Username already exists!", "danger")
                return redirect(url_for('signup'))
                
            sql = "INSERT INTO user (first_name, last_name, username, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (first_name, last_name, username, password))
            db.commit()
            db.close()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error during signup: {str(e)}", "danger")
            return redirect(url_for('signup'))
    return render_template('sign.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            db.close()
            
            if not existing_user:
                flash("User not found. Please signup.", "warning")
                return redirect(url_for('signup'))
                
            if existing_user['password'] == password:
                session['user'] = username
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password!", "danger")
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error during login: {str(e)}", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    print("Register route hit!")
    try:
        Full_name = request.form['Full_Name']
        Email = request.form['Email_Address']
        Contact_number = request.form['Contact_Number']
        Skype = request.form['Skype']
        print(f"Form data: {Full_name}, {Email}, {Contact_number}, {Skype}")

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # Check if this email inquiry already exists (since Email_Address is primary key in your current table)
        cursor.execute("SELECT * FROM ino_tb WHERE Email_Address = %s", (Email,))
        if cursor.fetchone():
            db.close()
            flash("An inquiry with this email has already been submitted!", "warning")
            return redirect(url_for('dashboard'))

        # Note: 'skype' is lowercase in your current database schema
        sql = "INSERT INTO ino_tb(Full_Name, Email_Address, Contact_Number, skype) VALUES(%s, %s, %s, %s)"
        cursor.execute(sql, (Full_name, Email, Contact_number, Skype))
        db.commit()
        db.close()
        
        flash("Your inquiry has been sent successfully!", "success")
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error submitting inquiry: {str(e)}", "danger")
        print(f"Error: {str(e)}")
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
