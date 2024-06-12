import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configure your email credentials
EMAIL_ADDRESS = "pventures@up.edu.ph"
EMAIL_PASSWORD = "wzhc wubm yorz ohdw"
SMTP_SERVER = "smtp.gmail.com"  # Update this to your SMTP server
SMTP_PORT = 587  # Update this to your SMTP port if necessary

def send_test_email(to, subject, content):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = "cess.ventures209@gmail.com"
        msg['Subject'] =  subject

        msg.attach(MIMEText(content, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable TLS
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to, text)
        server.quit()

        print(f"Email sent to {to} with subject: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

send_test_email("cess.ventures209@gmail.com", "Test Email", "This is a test email from BuddyBetes.")
