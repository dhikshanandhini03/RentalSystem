from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change this if your username is different
        password="Dhiksha@03",  # Replace with your actual MySQL password
        database="agri_rental"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]  # Assuming role is in 4th column
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', role=session['role'])

@app.route('/products')
def products():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/request_product', methods=['GET', 'POST'])
def request_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        product_id = request.form['product_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO rental_requests (user_id, product_id) VALUES (%s, %s)', 
                      (session['user_id'], product_id))
        conn.commit()
        conn.close()
        flash('Rental request submitted')
        return redirect(url_for('rental_history'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('request_product.html', products=products)

@app.route('/rental_history')
def rental_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT r.*, p.name FROM rental_requests r JOIN products p ON r.product_id = p.id WHERE r.user_id = %s', 
                  (session['user_id'],))
    rentals = cursor.fetchall()
    conn.close()
    return render_template('rental_history.html', rentals=rentals)

@app.route('/payment_history')
def payment_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments WHERE user_id = %s', (session['user_id'],))
    payments = cursor.fetchall()
    conn.close()
    return render_template('payment_history.html', payments=payments)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)