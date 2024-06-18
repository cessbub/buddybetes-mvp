import streamlit as st
import pandas as pd  # Import pandas
from auth import get_user_info, update_user_info
from database import create_connection

def profile_management(username):
    st.subheader("Manage Your Profile")

    user_info = get_user_info(username)
    if user_info:
        with st.form(key='profile_form'):
            new_username = st.text_input("Username", value=user_info[0], placeholder="Enter your new username")
            email = st.text_input("Email", value=user_info[1], placeholder="Enter your email")
            name = st.text_input("Name", value=user_info[2], placeholder="Enter your name")
            email_reminder = st.selectbox("Email Reminder Frequency", ["None", "Daily", "Weekly"], index=["None", "Daily", "Weekly"].index(user_info[4]))
            reminder_time = st.time_input("Reminder Time (24:00H Format)", value=pd.to_datetime(user_info[5]).time())
            submit_button = st.form_submit_button(label="Update Profile")  # Add submit button

        if submit_button:
            try:
                if new_username != username:
                    # Update username in the database
                    conn = create_connection()
                    c = conn.cursor()
                    c.execute('''
                        UPDATE health_data
                        SET user_id = ?
                        WHERE user_id = ?
                    ''', (new_username, username))
                    conn.commit()
                    conn.close()

                update_user_info(username, new_username, email, name, email_reminder, reminder_time.strftime('%H:%M'))
                st.session_state['username'] = new_username
                st.success("Profile updated successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("User not found.")
