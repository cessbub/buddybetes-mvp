import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

import streamlit as st
from app.auth import authenticator
from app.database import create_connection, create_tables
from app.email_notifications import send_email, schedule_email, run_scheduled_emails, load_reminder_settings
from passlib.context import CryptContext
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import threading

# set up the page configuration
st.set_page_config(
    page_title="BuddyBetes",
    page_icon="images/page_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize session state keys
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'logout' not in st.session_state:
    st.session_state['logout'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'Analytics'  # Set default page to Analytics

# Initialize the database
create_tables()

def main():
    st.sidebar.image("images/buddybetes_logo.png", use_column_width=True)
    st.sidebar.markdown("This is BuddyBetes, your best friend in diabetes care.")
    st.sidebar.divider() 
    
    if st.session_state['authentication_status']:
        st.sidebar.title(f"Welcome, {st.session_state['name']}!")
        st.sidebar.markdown("Choose any in the menu:")
        
        # Menu for logged-in users
        st.sidebar.button("Analytics", on_click=lambda: set_page('Analytics'))
        st.sidebar.button("Log Data", on_click=lambda: set_page('Log Data'))
        st.sidebar.button("Profile", on_click=lambda: set_page('Profile'))
        st.sidebar.button("Email Notifications", on_click=lambda: set_page('Settings'))
        st.sidebar.button("Logout", on_click=logout_user)
    else:
        # Menu for non-logged-in users
        st.sidebar.button("Login", on_click=lambda: set_page('Login'))
        st.sidebar.button("Register", on_click=lambda: set_page('Register'))

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
    st.session_state['page'] = 'Analytics'
    st.success("You have been logged out successfully.")

def login_user():
    fields = {
        'Form name': 'Login',
        'Username': 'Username',
        'Password': 'Password',
        'Login': 'Login'
    }

    name, authentication_status, username = authenticator.login('main', fields=fields)

    if authentication_status:
        st.session_state['authentication_status'] = authentication_status
        st.session_state['name'] = name
        st.session_state['username'] = username

        st.sidebar.title(f"Welcome {name}")
        authenticator.logout('Logout', 'sidebar')

        st.session_state['page'] = 'Analytics'
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

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
            new_user = {
                'email': email,
                'name': name,
                'password': hashed_password
            }

            with open('config.yaml') as file:
                config = yaml.safe_load(file)

            config['credentials']['usernames'][username] = new_user

            with open('config.yaml', 'w') as file:
                yaml.safe_dump(config, file)

            st.success("User registered successfully! Please log in.")

def profile_management(username):
    st.subheader("Manage Your Profile")

    with open('config.yaml') as file:
        config = yaml.safe_load(file)

    user_info = config['credentials']['usernames'][username]

    with st.form(key='profile_form'):
        new_username = st.text_input("Username", value=username)
        email = st.text_input("Email", value=user_info['email'])
        name = st.text_input("Name", value=user_info['name'])
        submit_button = st.form_submit_button(label="Update Profile")

    if submit_button:
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

            # Update username in the config
            config['credentials']['usernames'][new_username] = config['credentials']['usernames'].pop(username)
            st.session_state['username'] = new_username

        config['credentials']['usernames'][new_username]['email'] = email
        config['credentials']['usernames'][new_username]['name'] = name

        with open('config.yaml', 'w') as file:
            yaml.safe_dump(config, file)

        st.success("Profile updated successfully!")

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
        # Save settings to config.yaml
        with open('config.yaml') as file:
            config = yaml.safe_load(file)

        if 'settings' not in config:
            config['settings'] = {}
        config['settings'][username] = {
            'email_reminder': email_reminder,
            'reminder_time': reminder_time.strftime('%H:%M')
        }

        with open('config.yaml', 'w') as file:
            yaml.safe_dump(config, file)

        st.success("Reminder settings saved successfully!")

        # Cancel any existing schedule
        schedule_email(username, "[BUDDYBETES REMINDER] Reminder to log your Health Data!", "This is your BuddyBetes reminder to log your health data.")

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


if __name__ == "__main__":
    email_scheduler_thread = threading.Thread(target=run_scheduled_emails, daemon=True)
    email_scheduler_thread.start()
    main()
