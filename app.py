from flask import Flask, request
import psycopg2
import boto3

# 1. Initialize the App (CRITICAL: This must be here!)
app = Flask(__name__)

# 2. Database & SNS Config
DB_CONFIG = {
    "host": "eventregistrationdb.clgcmw08ak32.ap-south-1.rds.amazonaws.com",
    "database": "eventdb",
    "user": "eventadmin",
    "password": "vivek2208",
    "sslmode": "require"
}

SNS_CLIENT = boto3.client('sns', region_name='ap-south-1')
TOPIC_ARN = "arn:aws:sns:ap-south-1:810774026813:rotarytopic" # Replace with your ARN

HTML_FORM = """
<!DOCTYPE html>
<html>
<body style="text-align:center; font-family: sans-serif; padding-top: 50px;">
    <h2>Tech Festival Registration</h2>
    <form method="POST" action="/register">
        <input type="text" name="fullname" placeholder="Full Name" required><br><br>
        <input type="email" name="email" placeholder="Email Address" required><br><br>
        <button type="submit" style="background: blue; color: white; padding: 10px;">Register Me!</button>
    </form>
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
        # Save to Database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO attendees (fullname, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        
        # Send SNS Notification
        SNS_CLIENT.publish(
            TopicArn=TOPIC_ARN,
            Message=f"New Registration! Name: {name}, Email: {email}",
            Subject="New Tech Fest Attendee"
        )
        
        cur.close()
        conn.close()
        return f"<h1>Success!</h1><p>Thanks {name}, you are registered and we've notified the team.</p><a href='/'>Back</a>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    # Using port 80 requires 'sudo'
    app.run(host='0.0.0.0', port=80)
