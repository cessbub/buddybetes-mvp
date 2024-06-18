import streamlit as st
import pandas as pd
from email_notifications import schedule_email, load_reminder_settings
from database import create_connection

def settings(username):
    st.subheader("Email Notification Reminder")

    # Load existing settings
    email_reminder, reminder_time = load_reminder_settings(username)

    with st.form(key='settings_form'):
        email_reminder = st.selectbox(
            "Email Reminder Frequency", 
            ["None", "Daily", "Weekly"], 
            index=["None", "Daily", "Weekly"].index(email_reminder), 
            key="email_reminder_selectbox"
        )
        reminder_time = st.time_input(
            "Reminder Time (24:00H Format)", 
            value=pd.to_datetime(reminder_time).time(), 
            key="reminder_time_input"
        )
        submit_button = st.form_submit_button(label="Save Email Notification Reminder")

    if submit_button:
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE users
                SET email_reminder = ?, reminder_time = ?
                WHERE username = ?
            ''', (email_reminder, reminder_time.strftime('%H:%M'), username))
            conn.commit()
            conn.close()

            st.success("Reminder settings saved successfully!")

            # Cancel any existing schedule
            schedule_email(username, "[BUDDYBETES REMINDER] Reminder to log your Health Data!", "This is your BuddyBetes reminder to log your health data.")
        except Exception as e:
            st.error(f"An error occurred while saving the settings: {e}")
