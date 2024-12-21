from flask import Flask, request, jsonify
from email_classifier import classify_email
from order_processing import extract_order_details
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

app = Flask(__name__)

@app.route("/process_email", methods=["POST"])
def process_email():
    """
    Processes incoming email to classify it and extract order details if applicable.
    """
    email_data = request.json
    email_subject = email_data.get("subject")
    email_body = email_data.get("body")
    
    # Classify the email
    category = classify_email(email_subject, email_body)
    
    response = {
        "category": category
    }
    
    if category == "Order":
        order_details = extract_order_details(email_body)
        response["order_details"] = order_details

    return jsonify(response)

def send_email(subject, body, to_email):
    """
    Sends an email using SMTP.
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    app.run(debug=True)
