import os
import sys

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import yaml
from datetime import datetime, timedelta
import streamlit as st
from database import create_connection
import logging
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure your email credentials
EMAIL_ADDRESS = st.secrets["general"]["EMAIL_ADDRESS"]
EMAIL_PASSWORD = st.secrets["general"]["EMAIL_PASSWORD"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

scheduled_jobs = {}  # Dictionary to track scheduled jobs
last_sent_times = {}  # Dictionary to track the last sent time for each user
job_executed = {}  # Dictionary to track if the job was executed in the current minute

def load_last_sent_times():
    global last_sent_times
    try:
        with open('last_sent_times.yaml', 'r') as file:
            last_sent_times = yaml.safe_load(file)
        if last_sent_times is None:
            last_sent_times = {}
        logger.info("Loaded last_sent_times: %s", last_sent_times)
    except FileNotFoundError:
        last_sent_times = {}
        logger.warning("last_sent_times.yaml file not found. Initializing empty dictionary.")
    except Exception as e:
        logger.error("Error loading last_sent_times.yaml: %s", e)
        last_sent_times = {}

def save_last_sent_times():
    try:
        with open('last_sent_times.yaml', 'w') as file:
            yaml.safe_dump(last_sent_times, file)
        logger.info("Saved last_sent_times: %s", last_sent_times)
    except Exception as e:
        logger.error("Error saving last_sent_times.yaml: %s", e)

def send_email(username, subject, content):
    try:
        conn = create_connection()
        c = conn.cursor()
        c.execute('SELECT email FROM users WHERE username = ?', (username,))
        user_email = c.fetchone()[0]
        conn.close()

        now = datetime.now().replace(second=0, microsecond=0)
        if username in last_sent_times:
            last_sent_time = datetime.fromisoformat(last_sent_times[username]).replace(second=0, microsecond=0)
            logger.info("Last sent time for %s: %s", username, last_sent_time)
            logger.info("Current time: %s", now)
            if last_sent_time == now:
                logger.info("Email to %s already sent today.", user_email)
                return

        logger.info("Attempting to send email to %s with subject: %s", user_email, subject)

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = user_email
        msg['Subject'] = subject

        msg.attach(MIMEText(content, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, user_email, text)
        server.quit()

        logger.info("Email sent to %s with subject: %s", user_email, subject)

        last_sent_times[username] = now.isoformat()
        save_last_sent_times()
    except Exception as e:
        logger.error("Failed to send email: %s", e)

def load_reminder_settings(username):
    try:
        conn = create_connection()
        c = conn.cursor()
        c.execute('SELECT email_reminder, reminder_time FROM users WHERE username = ?', (username,))
        user_settings = c.fetchone()
        conn.close()

        if user_settings:
            email_reminder, reminder_time = user_settings
        else:
            email_reminder, reminder_time = 'None', '12:00'
        return email_reminder, reminder_time
    except Exception as e:
        logger.error("Error loading reminder settings for %s: %s", username, e)
        return 'None', '12:00'

def schedule_email(username, subject, content):
    email_reminder, reminder_time = load_reminder_settings(username)
    job_id = f"{username}_{reminder_time}"
    if email_reminder != "None":
        if job_id in scheduled_jobs:
            logger.info("Removing existing job: %s", job_id)
            schedule.cancel_job(scheduled_jobs[job_id])
            del scheduled_jobs[job_id]

        logger.info("Scheduling email for %s at %s", username, reminder_time)

        def job():
            now = datetime.now().replace(second=0, microsecond=0)
            logger.info("Executing job for %s at %s", username, now)
            if job_id in job_executed and job_executed[job_id] == now:
                logger.info("Job already executed for %s at %s", username, reminder_time)
                return
            job_executed[job_id] = now

            try:
                send_email(username, subject, content)
                logger.info("Email sent for job: %s", job_id)
            except Exception as e:
                logger.error("Error in job execution for %s: %s", job_id, e)

            logger.info("Cancelling job after execution: %s", job_id)
            if job_id in scheduled_jobs:
                schedule.cancel_job(scheduled_jobs[job_id])
                del scheduled_jobs[job_id]

        job = schedule.every().day.at(reminder_time).do(job)
        scheduled_jobs[job_id] = job
        logger.info("Job scheduled: %s", job_id)

def run_scheduled_emails():
    load_last_sent_times()
    logger.info("Starting email scheduler...")
    while True:
        schedule.run_pending()
        logger.info("Checking for pending jobs...")
        time.sleep(1)


def start_scheduler_thread():
    thread = threading.Thread(target=run_scheduled_emails, daemon=True)
    thread.start()
