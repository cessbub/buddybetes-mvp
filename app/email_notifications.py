import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import yaml
from datetime import datetime, timedelta
import streamlit as st

# Configure your email credentials
EMAIL_ADDRESS = st.secrets["general"]["EMAIL_ADDRESS"]
EMAIL_PASSWORD = st.secrets["general"]["EMAIL_PASSWORD"]
SMTP_SERVER = "smtp.gmail.com"  # Update this to your SMTP server
SMTP_PORT = 587  # Update this to your SMTP port if necessary

scheduled_jobs = {}  # Dictionary to track scheduled jobs
last_sent_times = {}  # Dictionary to track the last sent time for each user
job_executed = {}  # Dictionary to track if the job was executed in the current minute

def load_last_sent_times():
    global last_sent_times
    try:
        with open('last_sent_times.yaml') as file:
            last_sent_times = yaml.safe_load(file)
        if last_sent_times is None:
            last_sent_times = {}
    except FileNotFoundError:
        last_sent_times = {}
    print("Loaded last_sent_times:", last_sent_times)

def save_last_sent_times():
    with open('last_sent_times.yaml', 'w') as file:
        yaml.safe_dump(last_sent_times, file)
    print("Saved last_sent_times:", last_sent_times)

def send_email(username, subject, content):
    try:
        # Load user email address from config.yaml
        with open('config.yaml') as file:
            config = yaml.safe_load(file)
        user_email = config['credentials']['usernames'][username]['email']

        now = datetime.now().replace(second=0, microsecond=0)  # Remove seconds and microseconds
        # Check if email was sent today
        if username in last_sent_times:
            last_sent_time = datetime.fromisoformat(last_sent_times[username]).replace(second=0, microsecond=0)
            print(f"Last sent time for {username}: {last_sent_time}")
            print(f"Current time: {now}")
            if last_sent_time == now:
                print(f"Email to {user_email} already sent today.")
                return

        print(f"Attempting to send email to {user_email} with subject: {subject}")

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = user_email
        msg['Subject'] = subject

        msg.attach(MIMEText(content, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable TLS
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, user_email, text)
        server.quit()

        print(f"Email sent to {user_email} with subject: {subject}")

        # Update the last sent time
        last_sent_times[username] = now.isoformat()
        save_last_sent_times()
    except Exception as e:
        print(f"Failed to send email: {e}")

def load_reminder_settings(username):
    with open('config.yaml') as file:
        config = yaml.safe_load(file)
    user_settings = config.get('settings', {}).get(username, {})
    email_reminder = user_settings.get('email_reminder', 'None')
    reminder_time = user_settings.get('reminder_time', '12:00')
    return email_reminder, reminder_time

def schedule_email(username, subject, content):
    email_reminder, reminder_time = load_reminder_settings(username)
    job_id = f"{username}_{reminder_time}"
    if email_reminder != "None":
        # Remove any existing job for this user to prevent multiple scheduling
        if job_id in scheduled_jobs:
            print(f"Removing existing job: {job_id}")
            schedule.cancel_job(scheduled_jobs[job_id])
            del scheduled_jobs[job_id]

        print(f"Scheduling email for {username} at {reminder_time}")

        def job():
            now = datetime.now().replace(second=0, microsecond=0)
            if job_id in job_executed and job_executed[job_id] == now:
                print(f"Job already executed for {username} at {reminder_time}")
                return
            job_executed[job_id] = now
            send_email(username, subject, content)
            # Remove the job after execution to prevent multiple sends
            print(f"Cancelling job after execution: {job_id}")
            if job_id in scheduled_jobs:
                schedule.cancel_job(scheduled_jobs[job_id])
                del scheduled_jobs[job_id]

        job = schedule.every().day.at(reminder_time).do(job)
        scheduled_jobs[job_id] = job
        print(f"Job scheduled: {job_id}")

def run_scheduled_emails():
    load_last_sent_times()
    print("Starting email scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # For testing, ensure to schedule email
    schedule_email('user1', '[BUDDYBETES REMINDER] Reminder to log your Health Data!', 'This is your BuddyBetes reminder to log your health data.')
    run_scheduled_emails()
