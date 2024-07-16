import os
from flask import Flask, request, Response
from celery import Celery
from dotenv import load_dotenv
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Configure logging
log_path = os.path.join(os.path.expanduser('~'), 'messaging_system.log')
logging.basicConfig(level=logging.INFO, filename=log_path, filemode='a', format='%(asctime)s - %(message)s')

# Celery task to send email
@celery.task
def send_email(to_email):
    from_email = os.getenv('EMAIL_USER')
    from_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = 'smtp.mail.yahoo.com'
    smtp_port = 465
    subject = 'Official Email from Flask Application'
    body = 'This is a test email sent from the Flask application.'
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        logging.info(f'Connecting to SMTP server {smtp_server}:{smtp_port}')
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            logging.info('Logging in to SMTP server')
            server.login(from_email, from_password)
            logging.info('Sending email')
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            logging.info(f'{datetime.now()} - Email sent to {to_email}')
    except Exception as e:
        logging.error(f'Failed to send email: {e}')

# Flask routes
@app.route('/', methods=['GET'])
def index():
    if 'sendmail' in request.args:
        send_email.apply_async(args=[request.args.get('sendmail')])
        logging.info(f'{datetime.now()} - Email queued for: {request.args.get("sendmail")}')
        return 'Email queued.'
    elif 'talktome' in request.args:
        logging.info(f'{datetime.now()} - Logged the current time.')
        return 'Logged the current time.'
    else:
        return 'Welcome to the messaging system. Use /?sendmail=email or /?talktome.'

@app.route('/logs', methods=['GET'])
def logs():
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_content = f.readlines()
        filtered_logs = [line for line in log_content if 'Email sent to' in line or 'Email queued for' in line]
        return Response(''.join(filtered_logs), mimetype='text/plain')
    else:
        return "Log file not found.", 404

# Main entry point
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
