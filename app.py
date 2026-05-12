from flask import Flask, render_template, request, redirect
import sqlite3
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# ---------------- DATABASE CONNECTION ---------------- #

def get_connection():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    return conn


# ---------------- CREATE TABLES ---------------- #

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT

)

""")

cursor.execute("""

INSERT OR IGNORE INTO users (id, username, password)

VALUES (1, 'admin', 'admin123')

""")

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

patterns = [

    r"(\bOR\b|\bAND\b).*=.*",

    r"(--|#|\/\*)",

    r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|EXEC|CREATE|TRUNCATE)\b",

    r"\bUNION\b.*\bSELECT\b",

    r";",

    r"\bSLEEP\s*\(",

    r"\bWAITFOR\b",

    r"\bINFORMATION_SCHEMA\b",

    r"0x[0-9a-fA-F]+",

    r"['\"]",

    r"admin\s*--",

    r"xp_cmdshell",

    r"DROP\s+TABLE",

    r"UNION\s+SELECT"

]


# ---------------- DETECTION FUNCTION ---------------- #

def detect_sql_injection(user_input):

    user_input = user_input.upper()

    for pattern in patterns:

        if re.search(pattern, user_input, re.IGNORECASE):

            return True

    return False


# ---------------- EMAIL ALERT ---------------- #

def send_email_alert(message):

    sender_email = "sarthaklakhadive22@gmail.com"

    sender_password = "dcmv pqof wqbl ajjk"

    receiver_emails = [

    "sarthaklakhadive22@gmail.com",
    "lakhadivesarthak@gmail.com",
    "kshirsagar.rohit.ranjit123@gmail.com"

    ]

    msg = MIMEText(message)

    msg['Subject'] = "SQL Injection Alert"

    msg['From'] = sender_email

    msg['To'] = ", ".join(receiver_emails)

    try:

        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login(sender_email, sender_password)

        server.sendmail(
            sender_email,
            receiver_emails,
            msg.as_string()
        )

        server.quit()

    except Exception as e:

        print(e)


# ---------------- HOME PAGE ---------------- #

@app.route('/')
def home():

    return render_template('login.html')


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    combined_input = username + " " + password

    # SQL Injection Detection
    if detect_sql_injection(combined_input):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO attack_logs (input, timestamp)

        VALUES (?, ?)

        """, (combined_input, datetime.now()))

        conn.commit()
        conn.close()

        # Send Email Alert
        send_email_alert(

            f"""
SQL Injection Detected

Username: {username}

Password: {password}

Time: {datetime.now()}
"""
        )

        return redirect('/dashboard')

    # Normal Login
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM users

    WHERE username=? AND password=?

    """, (username, password))

    user = cursor.fetchone()

    conn.close()

    if user:

        return redirect('/dashboard')

    return "Invalid Username or Password"


# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM attack_logs
    ORDER BY id DESC

    """)

    logs = cursor.fetchall()

    count = len(logs)

    conn.close()

    return render_template(

        'dashboard.html',
        logs=logs,
        count=count

    )


# ---------------- RUN APP ---------------- #

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)