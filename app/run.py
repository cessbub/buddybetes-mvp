import os
import sys
import time  # Make sure to import the time module

import streamlit as st

from auth import authenticate, get_user_info, update_user_info
from database import create_connection, create_tables, create_user_table
from email_notifications import send_email, schedule_email, run_scheduled_emails, load_reminder_settings, start_scheduler_thread
from passlib.context import CryptContext
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

def show_modal():
    st.markdown(
        """
        <style>
        #modal {
            position: fixed;
            top: 0;
            left: 0;
            width: calc(100% - 300px); /* Adjust for sidebar width */
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 9999;
        }
        #modal-content {
            max-width: 90%;
            width: 600px;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            position: relative;
            margin-left: 300px; /* Adjust for sidebar width */
        }
        #modal-close-button {
            position: absolute;
            bottom: 20px;
            right: 20px;
            padding: 10px 20px;
            background-color: #009886;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        </style>
        <div id="modal">
            <div id="modal-content">
                <h2>Welcome to BuddyBetes MVP 🎉</h2>
                <p>Hi there! Thank you for trying out the MVP of BuddyBetes. We're excited to have you here!</p>
                <h3>Important Information 📢</h3>
                <ul>
                    <li>This is an <strong>MVP</strong> version, so some features might be limited or in progress.</li>
                    <li>Currently, the database is not persistent. This means that any data you enter will be lost if you refresh the page or close the browser. 😅</li>
                    <li>For the best experience, please use a <strong>laptop/PC</strong> to view and interact with the application. 🖥️</li>
                </ul>
                <p>We appreciate your understanding and look forward to your feedback!</p>
                <button id="modal-close-button" onclick="document.getElementById('modal').style.display='none'">Okay</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# set up the page configuration
st.set_page_config(
    page_title="BuddyBetes",
    page_icon="images/page_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize the database
create_tables()
create_user_table()

# Initialize session state keys
def initialize_session_state():
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'logout' not in st.session_state:
        st.session_state['logout'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Login'  # Set default page to Login
    if 'modal_shown' not in st.session_state:
        st.session_state['modal_shown'] = False

def main():
    initialize_session_state()

    # Show modal after 1 second delay if not shown already
    if not st.session_state['modal_shown']:
        time.sleep(1)
        show_modal()
        st.session_state['modal_shown'] = True

    st.sidebar.image("images/buddybetes_logo.png", use_column_width=True)
    st.sidebar.markdown("This is BuddyBetes, your best friend in diabetes care.")
    st.sidebar.divider()

    if st.session_state['authentication_status']:
        st.sidebar.title(f"Welcome, {st.session_state['name']}!")
        st.sidebar.markdown("Choose any in the menu:")
        
        # Menu for logged-in users
        st.sidebar.button("Analytics", on_click=lambda: set_page('Analytics'), key="btn_analytics")
        st.sidebar.button("Log Data", on_click=lambda: set_page('Log Data'), key="btn_log_data")
        st.sidebar.button("Profile", on_click=lambda: set_page('Profile'), key="btn_profile")
        st.sidebar.button("Email Notifications", on_click=lambda: set_page('Settings'), key="btn_settings")
        st.sidebar.button("Logout", on_click=logout_user, key="btn_logout")
        
        # Automatically redirect to the Analytics page if logged in
        if st.session_state['page'] == 'Login':
            st.session_state['page'] = 'Analytics'
    else:
        # Menu for non-logged-in users
        st.sidebar.button("Login", on_click=lambda: set_page('Login'), key="btn_login")
        st.sidebar.button("Create an Account", on_click=lambda: set_page('Register'), key="btn_register")

    if st.session_state['page'] == 'Login':
        login_user()
    elif st.session_state['page'] == 'Register':
        register_user()
    elif st.session_state['page'] == 'Log Data':
        if st.session_state.get("authentication_status"):
            log_data_form(st.session_state.get("username"))
        else:
            st.warning("Please log in to log your health data.")
    elif st.session_state['page'] == 'Analytics':
        if st.session_state.get("authentication_status"):
            analytics_dashboard(st.session_state.get("username"))
        else:
            st.warning("Please log in to view analytics.")
    elif st.session_state['page'] == 'Profile':
        if st.session_state.get("authentication_status"):
            profile_management(st.session_state.get("username"))
        else:
            st.warning("Please log in to view your profile.")
    elif st.session_state['page'] == 'Settings':
        if st.session_state.get("authentication_status"):
            settings(st.session_state.get("username"))
        else:
            st.warning("Please log in to access settings.")

def set_page(page_name):
    st.session_state['page'] = page_name

def logout_user():
    st.session_state['authentication_status'] = None
    st.session_state['name'] = None
    st.session_state['username'] = None
    st.session_state['page'] = 'Login'
    st.success("You have been logged out successfully.")

def login_user():
    st.subheader("Login to Your Account")

    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

    if submit_button:
        try:
            auth_status, name, user = authenticate(username, password)
            if auth_status:
                st.session_state['authentication_status'] = True
                st.session_state['name'] = name
                st.session_state['username'] = user

                st.sidebar.title(f"Welcome {name}")

                # Redirect to Analytics page after successful login
                st.session_state['page'] = 'Analytics'
                st.experimental_rerun()  # Refresh the page to navigate to Analytics
            else:
                st.error('Incorrect username or password. Please try again.')
        except Exception as e:
            st.error(f"An error occurred during login: {e}")

    if st.button("Create new account here"):
        set_page('Register')



def log_data_form(username):
    st.subheader("Log Your Health Data")

    # create the form
    with st.form(key='health_data_form'):
        date = st.date_input("Date")
        time = st.time_input("Time")
        glucose_level = st.number_input("Glucose Level", min_value=0.0, step=0.1)
        bp_systolic = st.number_input("Blood Pressure (Systolic)", min_value=0)
        bp_diastolic = st.number_input("Blood Pressure (Diastolic)", min_value=0)
        meal_context = st.selectbox("Meal Context", ["Before Breakfast", "After Breakfast", "Before Lunch", "After Lunch", "Before Dinner", "After Dinner", "Other"])
        food_intake = st.text_area("Food Intake")
        mood = st.selectbox("Mood", ["Happy", "Sad", "Neutral", "Anxious", "Stressed"])
        symptoms = st.text_area("Symptoms")

        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO health_data (user_id, date, time, glucose_level, bp_systolic, bp_diastolic, food_intake, mood, symptoms, meal_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, date.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), glucose_level, bp_systolic, bp_diastolic, food_intake, mood, symptoms, meal_context))
            conn.commit()

            # Debug statement: Check number of rows in health_data table
            c.execute('SELECT COUNT(*) FROM health_data')
            count = c.fetchone()[0]
            st.write(f"Total health data entries: {count}")

            conn.close()
            st.success("Health data logged successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def register_user():
    st.subheader("Create New Account")

    with st.form(key='registration_form'):
        username = st.text_input("Username")
        email = st.text_input("Email")
        name = st.text_input("Name")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button(label="Register")

    if submit_button:
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            hashed_password = pwd_context.hash(password)
            try:
                conn = create_connection()
                c = conn.cursor()
                c.execute('''
                    INSERT INTO users (username, email, name, password, email_reminder, reminder_time)
                    VALUES (?, ?, ?, ?, 'Daily', '07:58')
                ''', (username, email, name, hashed_password))
                conn.commit()
                conn.close()
                st.success("User registered successfully! Please log in.")
            except Exception as e:
                st.error(f"An error occurred while registering the user: {e}")
    
    if st.button("Have an account? Login Here"):
        set_page('Login')

def profile_management(username):
    st.subheader("Manage Your Profile")

    user_info = get_user_info(username)
    if user_info:
        with st.form(key='profile_form'):
            new_username = st.text_input("Username", value=user_info[0])
            email = st.text_input("Email", value=user_info[1])
            name = st.text_input("Name", value=user_info[2])
            email_reminder = st.selectbox("Email Reminder Frequency", ["None", "Daily", "Weekly"], index=["None", "Daily", "Weekly"].index(user_info[4]))
            reminder_time = st.time_input("Reminder Time (24:00H Format)", value=pd.to_datetime(user_info[5]).time())
            submit_button = st.form_submit_button(label="Update Profile")

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
        
        
        

def settings(username):
    st.subheader("Email Notification Reminder")

    # Load existing settings
    email_reminder, reminder_time = load_reminder_settings(username)

    with st.form(key='settings_form'):
        email_reminder = st.selectbox(
            "Email Reminder", 
            ["None", "Daily", "Weekly"], 
            index=["None", "Daily", "Weekly"].index(email_reminder), 
            key="email_reminder_selectbox"
        )
        reminder_time = st.time_input(
            "Reminder Time", 
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

def analytics_dashboard(username):
    st.subheader("Analytics Dashboard")

    conn = create_connection()
    query = "SELECT date, time, glucose_level, bp_systolic, bp_diastolic, food_intake, mood, symptoms, meal_context FROM health_data WHERE user_id = ? ORDER BY date DESC, time DESC"
    df = pd.read_sql_query(query, conn, params=(username,))
    conn.close()

    if df.empty:
        st.write("No data available. Please log some health data.")
    else:
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df.set_index('datetime', inplace=True)

        # Overview
        st.write("## Overview")
        last_glucose_level = df['glucose_level'].iloc[0]
        last_bp_systolic = df['bp_systolic'].iloc[0]
        last_bp_diastolic = df['bp_diastolic'].iloc[0]
        last_meal = df['food_intake'].iloc[0]
        last_entry_date = df.index[0].strftime('%Y-%m-%d %H:%M:%S')

        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<h3>Last Recorded Glucose Level</h3><h1>{last_glucose_level}</h1><p style='font-size:small;'>{last_entry_date}</p>", unsafe_allow_html=True)
        col2.markdown(f"<h3>Last Recorded Blood Pressure</h3><h1>{last_bp_systolic}/{last_bp_diastolic}</h1><p style='font-size:small;'>{last_entry_date}</p>", unsafe_allow_html=True)
        col3.markdown(f"<h3>Last Recorded Meal</h3><h1>{last_meal}</h1><p style='font-size:small;'>{last_entry_date}</p>", unsafe_allow_html=True)

        # Glucose Levels Over Time
        st.write("## Glucose Levels Over Time")
        st.line_chart(df['glucose_level'])

        # Blood Pressure Over Time
        st.write("## Blood Pressure Over Time")
        st.line_chart(df[['bp_systolic', 'bp_diastolic']])

        # Mood Distribution
        st.write("## Mood Distribution")
        mood_counts = df['mood'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(mood_counts, labels=mood_counts.index, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        st.pyplot(fig)

        # Symptoms Over Time (Stacked Bar Chart)
        st.write("## Symptoms Over Time")
        symptoms_counts = df.groupby(['datetime', 'symptoms']).size().unstack(fill_value=0)
        symptoms_counts.plot(kind='bar', stacked=True, ax=ax)
        st.pyplot(fig)

        # Meal Context Distribution
        st.write("## Meal Context Distribution")
        meal_context_counts = df['meal_context'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(meal_context_counts, labels=meal_context_counts.index, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        st.pyplot(fig)

        # All Health Logs
        st.write("## All Health Logs")
        st.dataframe(df.reset_index())  # Display the dataframe with the health logs




start_scheduler_thread()

if __name__ == "__main__":
    main()
