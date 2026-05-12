from flask import Flask, render_template, request
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)

# ---------------- DATABASE CONNECTION ---------------- #

def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- CREATE TABLE ---------------- #

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attack_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

# ---------------- SQL INJECTION PATTERNS ---------------- #

sql_patterns = [

    r"(\bOR\b|\bAND\b)\s+\d+=\d+",

    r"(--|#|\/\*)",

    r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|EXEC)\b",

    r"\bUNION\b.*\bSELECT\b",

    r";",

    r"\bSLEEP\(|\bWAITFOR\b",

    r"\bINFORMATION_SCHEMA\b",

    r"0x[0-9a-fA-F]+",

    r"['\"]{2,}"
]

# ---------------- DETECTION FUNCTION ---------------- #

def detect_sql_injection(user_input):

    for pattern in sql_patterns:

        if re.search(pattern, user_input, re.IGNORECASE):
            return True

    return False

# ---------------- HOME PAGE ---------------- #

@app.route('/')
def home():
    return render_template('login.html')

# ---------------- LOGIN PAGE ---------------- #

@app.route('/login', methods=['POST'])

def login():

    username = request.form['username']
    password = request.form['password']

    combined_input = username + " " + password

    if detect_sql_injection(combined_input):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO attack_logs (input, timestamp)
        VALUES (?, ?)
        """, (combined_input, datetime.now()))

        conn.commit()
        conn.close()

        return "SQL Injection Attack Detected!"

    return "Login Successful"

# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')

def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM attack_logs
    ORDER BY timestamp DESC
    """)

    logs = cursor.fetchall()

    count = len(logs)

    conn.close()

    return render_template(
        'dashboard.html',
        logs=logs,
        count=count
    )

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)