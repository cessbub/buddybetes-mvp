import streamlit as st
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz
from database import create_connection

# Constants for email configuration
EMAIL_ADDRESS = st.secrets["general"]["EMAIL_ADDRESS"]
EMAIL_PASSWORD = st.secrets["general"]["EMAIL_PASSWORD"]
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Setting up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Dictionary to store the last sent times
last_sent_times = {}

# Timezone setup
PHT = pytz.timezone('Asia/Manila')

def send_email(username, subject, content):
    try:
        conn = create_connection()
        c = conn.cursor()
        c.execute('SELECT email FROM users WHERE username = ?', (username,))
        user_email = c.fetchone()[0]
        conn.close()

        now = datetime.now(PHT).replace(second=0, microsecond=0)
        if username in last_sent_times:
            last_sent_time = datetime.fromisoformat(last_sent_times[username]).replace(second=0, microsecond=0)
            last_sent_time = PHT.localize(last_sent_time)  # Ensure last sent time is in PHT
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
            now = datetime.now(PHT).replace(second=0, microsecond=0)
            logger.info(f"Executing job for {username} at {now}")
            logger.info(f"Job ID: {job_id}, Scheduled for: {reminder_time}")

            if job_id in job_executed and job_executed[job_id] == now:
                logger.info(f"Job already executed for {username} at {reminder_time}")
                return

            job_executed[job_id] = now

            try:
                logger.info(f"Calling send_email for {username}")
                send_email(username, subject, content)
                logger.info(f"Email sent for job: {job_id}")
            except Exception as e:
                logger.error(f"Error in job execution for {job_id}: {e}")

            logger.info(f"Cancelling job after execution: {job_id}")
            if job_id in scheduled_jobs:
                schedule.cancel_job(scheduled_jobs[job_id])
                del scheduled_jobs[job_id]

        job = schedule.every().day.at(reminder_time).do(job)
        scheduled_jobs[job_id] = job
        logger.info(f"Job scheduled: {job_id}")
    else:
        logger.info(f"No email reminder set for {username}")

# Ensure to update save_last_sent_times() and load_reminder_settings() functions to handle persistence correctly.
