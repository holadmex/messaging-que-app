
# Python Messaging Queue App Development


**Hello** guys,

Today we'll be developing a **Python Messaging Queue Test**, which consist of the following 'Tools' as our requirement.

1. RabbitMQ
2. Celery
3. Ngrok
4. Nginx


Lets talk about the theoretical aspect of the core tools we'll be using in the course of the task curtesy of **(HNG Internship)**


What is **RabbitMQ**?

RabbitMQ is an open-source messaging software that implements the Advanced Message Queuing Protocol (AMQP) and is widely used for managing messaging queues. RabbitMQ here also servers as Amazon Simple Queue Service(SQ) distributed messaging system which is fully managed by AWS, makes it easy to decouple and scale microservices, distributed systems, and serverless applications.


What is **Celery**?

Celery is an asynchronous task queue/job queue based on distributed message passing. its main purpose is to handle "asynchronous" task queue/job queue that handles the execution of background tasks.

(Asynchronous programming is a form of programming that allows a unit of work (like a function or a task) to start processing before the previous unit of work finishes which also means its serves task to function independently.


What is **Ngrok**?
    
Ngrok is a tool that creates secure tunnels from a public endpoint (like the internet) to a locally running web service or application. It allows developers to expose their local development stage environment to the internet securely, making it easier to test and share work-in-progress applications with team members without deploying them to a live environment. 


What is **Nginx** 

Nginx is a web server and reverse proxy server that is widely used for serving web content, handling load balancing, and acting as a proxy for email services. It's known for its speed, reliability, and low resource usage mainly in development to production stage.



**Lets hop into the business of the day, getting hands on the project task as we progress in the course of the blog post.**


## **Installation Prerequisite**

`sudo apt-get update`

`sudo apt-get install rabbitmq-server`

`sudo apt install nginx -y`

`{% embed https://ngrok.com/docs/guides/device-gateway/linux/ %}` (Redirection link to installl Ngrok)

On successful completion of installing Ngrok, log on to {% embed https://ngrok.com/ %} and sign up, to have a generate token which will be integrated with your project directory on your Linux terminal environment. Run the command below

`ngrok authtoken <your generate token>`


**Hold still, we'll be writing few couple blocks of code using python and installing the required Python Framework/Library to execute our Python blocks of code functions.**

First we'll open a directory on our Linux Vm (e.g Ubuntu)


`mkdir messaging-queue-app`

`cd messaging-queue-app`

`touch app.py .env ngnix.conf`

Created **app.py** File context

```
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
    app.run(debug=True, host='0.0.0.0', port=5000)
```


 ## NB:
 The Python Messaging queue application development here was setup to make use of (Yahoomail SMTP Send). You you're to put in your email address, and also generate an app token in your Yahoomail account security path, and make the configuration changes in the (.env)

Created .env File context

```
EMAIL_USER="ojewumi_dimeji@ymail.com"
EMAIL_PASSWORD="clndcnbjfpaelrj1"
SMTP_SERVER="smtp.mail.yahoo.com"
SMTP_PORT=465
```

Created nginx.conf File context

```
server {
    listen 80;
    server_name localhost;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```


On filling each files with their respective blocks of codes, there are few more Python requirement Frameworks/libraries to be installed right in our project directory using the (virtual Linux environment cmd)

## Installation

`sudo apt-get install python3-venv`

Right after the `python3-venv installation`, execute the following command below on your Linux terminal. This command create a separate virtual environment in your project directory for your block of code function to carry out its functions.

```
python3 -m venv messaging-queue
source messaging-queue/bin/activate
```

On carry out the above, we'll commence installation of our Python Frameworks/Libraries right inside our created (`venv messaging-queue`) which you  will be redirected to on executing the (`source messaging-queue/bin/activate`) cmd

```
pip install celery
pip install flask
pip install python-dotenv
pip freeze > requirements.txt (This CMD output all the installed Python pip installation for the application to run successfully)
```


Freight not, lol, we're  95% done to the completion of our project on carrying out the following command to execute our Python Messaging Queue Test.

**First step:**

`sudo rabbitmq-server` (This CMD launch our **RabbitMQ** sever to run for the course of our python messaging queue app test)

`sudo rabbitmq-server -detached` (This helps to run your RabbitMQ sever in the background without holding the terminal as hostage)

Open another sperate terminal (Optiona, but a must on first attempt with cmd above and below)

**Second step:**

`celery -A app.celery worker --loglevel=info` (This opens your **Celery** monitoring environment on checking for errors and successful `?sendmail` execution of your python messaging queue app)

`celery -A app.celery worker --loglevel=info --detach` (This helps to run your **Celery** in the background without holding the terminal as hostage)

**Third step:**

`python3 app.py` (This CMD lunch your web app development URL to be accessed on your localhost web browser.)

nohup python3 app.py > app.log 2>&1 & (This helps to lunch the app in the background without holding the terminal as hostage, and also output the return function to app.log.)


Finally, on exposing our `Local Development Test` to other team members, carry out the installation below;

`sudo apt-get install screen`

On completion of the installation, run;

`screen -S ngrok`

`ngrok http 5000` (You should see an outputted endpoint "https://e7c9-44-202-0-101.ngrok-free.app/" which serves as your URL to be publicly accessed.)


We've come to the End of the Task,

Celebrate yourself for not holding back on the success of completing the Python Messaging Queue App Development,

Happy reading,
Thank you.
Dimeji...




