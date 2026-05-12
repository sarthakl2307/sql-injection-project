from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route('/')
def home():
    return render_template("login.html")


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE username=? AND password=?"
        cursor.execute(query, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))

        return "Invalid Username or Password"

    return render_template("login.html")


# DASHBOARD PAGE
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attack_logs ORDER BY id DESC")
    logs = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        logs=logs,
        username=session['user']
    )


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# RUN APP
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)