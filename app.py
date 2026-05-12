from flask import Flask, render_template, request, redirect
from db_config import get_connection
import re
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)


def detect_sql_injection(user_input):

    patterns = [

        
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

    
    if len(user_input) > 50:
        return True

    for pattern in patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True

    return False



def is_safe_input(user_input):
    return re.match("^[a-zA-Z0-9_@. ]+$", user_input)



def send_alert(message):

    sender_email = "sarthaklakhadive22@gmail.com"
    sender_password = "dcmv pqof wqbl ajjk"

    receiver_emails = [ 
                    "sarthaklakhadive22@gmail.com",
                     "lakhadivesarthak@gmail.com",
                     "kshirsagar.rohit.ranjit123@gmail.com"
    ]
    msg = MIMEText(message)

    msg['Subject'] = "⚠ SQL Injection Alert"
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


    except Exception :
        pass



@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        
        ip_address = request.remote_addr

        
        if (not is_safe_input(username)) or \
           (not is_safe_input(password)) or \
           detect_sql_injection(username) or \
           detect_sql_injection(password):

            
            alert_message = f"""
SQL Injection Detected!

Username Input: {username}
Password Input: {password}
IP Address: {ip_address}
"""

            
            send_alert(alert_message)

            
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO attack_logs (input_text)
                VALUES (%s)
                """,
                (f"{username} | {password} | IP: {ip_address}",)
            )

            conn.commit()
            conn.close()

            return "⚠ SQL Injection Detected! Request Blocked."

        
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM users
        WHERE username=%s AND password=%s
        """

        cursor.execute(query, (username, password))

        result = cursor.fetchone()

        conn.close()

        if result:
            return redirect('/dashboard')

        else:
            return "Invalid Credentials"

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    
    cursor.execute("SELECT COUNT(*) FROM attack_logs")
    count = cursor.fetchone()[0]

    
    cursor.execute(
        """
        SELECT * FROM attack_logs
        ORDER BY timestamp DESC
        """
    )

    logs = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        logs=logs,
        count=count
    )



   if__name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)