from flask import Flask, request
import psycopg2
import boto3

app = Flask(__name__)

# --- 1. CONFIGURATION (PASTE YOUR DETAILS HERE) ---
DB_CONFIG = {
    "host": "eventregistrationdb.clgcmw08ak32.ap-south-1.rds.amazonaws.com",
    "database": "eventdb",
    "user": "eventadmin",
    "password": "vivek2208", 
    "sslmode": "require"
}

# The ARN for the Participant Topic (Topic 1)
USER_TOPIC_ARN = "arn:aws:sns:ap-south-1:810774026813:userregistrationtopic" 
# The ARN for the Admin Topic (Topic 2)
ADMIN_TOPIC_ARN = "arn:aws:sns:ap-south-1:810774026813:rotarytopic"

sns_client = boto3.client('sns', region_name='ap-south-1')

# --- 2. THE FORM ---
HTML_FORM = """
<!DOCTYPE html>
<html>
<body style="text-align:center; font-family:sans-serif; padding-top:50px; background:#f4f4f4;">
    <div style="background:white; display:inline-block; padding:30px; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h2>Tech Festival Registration</h2>
        <form method="POST" action="/register">
            <input type="text" name="fullname" placeholder="Full Name" style="width:250px; padding:10px;" required><br><br>
            <input type="email" name="email" placeholder="Email Address" style="width:250px; padding:10px;" required><br><br>
            <button type="submit" style="background:#007bff; color:white; border:none; padding:10px 20px; cursor:pointer;">Register Now</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_FORM

@app.route('/register', methods=['POST'])
def register():
    name = request.form['fullname']
    email = request.form['email']
    
    try:
        # Save to DB
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO attendees (fullname, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        cur.close()
        conn.close()

        # Notification 1: Welcome to User
        sns_client.publish(
            TopicArn=USER_TOPIC_ARN,
            Message=f"Hi {name}, you're registered for the Tech Festival!",
            Subject="Registration Confirmed"
        )

        # Notification 2: Alert to Admin
        sns_client.publish(
            TopicArn=ADMIN_TOPIC_ARN,
            Message=f"NEW ENTRY: {name} ({email}) has just registered.",
            Subject="Admin Alert: New Registration"
        )

        return "<h1>Success!</h1><p>Check your email for confirmation.</p>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
