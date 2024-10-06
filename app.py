from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create database connection
def get_db_connection():
    conn = sqlite3.connect('ticket_booking.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            seat_number TEXT NOT NULL,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, password))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!')
            return redirect(url_for('book_ticket'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

# Book Ticket route
@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_name = request.form['event_name']
        seat_number = request.form['seat_number']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tickets (user_id, event_name, seat_number) VALUES (?, ?, ?)",
                       (session['user_id'], event_name, seat_number))
        conn.commit()
        conn.close()
        flash('Ticket booked successfully!')

    return render_template('book_ticket.html')

# View Bookings route
@app.route('/bookings')
def bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT event_name, seat_number, booking_date FROM tickets WHERE user_id = ?", (session['user_id'],))
    bookings = cursor.fetchall()
    conn.close()

    return render_template('bookings.html', bookings=bookings)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Initialize the database before running the app
    init_db()
    app.run(debug=True)
