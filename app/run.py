import os
import sys
import streamlit as st
from app_pages.login import login_user
from app_pages.register import register_user
from app_pages.log_data import log_data_form
from app_pages.analytics import analytics_dashboard
from app_pages.profile import profile_management
from app_pages.settings import settings

from database import create_tables, create_user_table
from email_notifications import start_scheduler_thread
from passlib.context import CryptContext

# Set the Streamlit page configuration
st.set_page_config(page_title="BuddyBetes", page_icon="images/page_icon.png")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

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
    if 'dialog_shown' not in st.session_state:
        st.session_state['dialog_shown'] = False

# Dialog function
@st.experimental_dialog("Welcome to BuddyBetes MVP 🎉", width="large")
def welcome_dialog():
    st.markdown("**👋 Hi there! Thank you for trying out the MVP of BuddyBetes. We're excited to have you here!**")
    st.markdown("### Important Information 📢")
    st.markdown("1. **MVP Version**: This is an MVP version, so some features might be limited or in progress. 🛠️")
    st.markdown("2. **Data Persistence**: Currently, the database is not persistent. This means that any data you enter (such as registering an account) will be lost if you close the browser. 😅")
    st.markdown("3. **Best Experience**: For the best experience, please use a **laptop/PC** to view and interact with the application. 🖥️")
    st.markdown("4. **Stay Updated**: You may check out our website at [buddybetes.com](https://buddybetes.com) and **sign up for our newsletter** to get updated on our progress! 🌐")
    
    st.markdown("<br>", unsafe_allow_html=True)  # Adding a line break for better spacing

    if st.button("Okay"):
        st.session_state['dialog_shown'] = True
        st.experimental_rerun()

# Main function to run the app
def main():
    initialize_session_state()

    # Show dialog if not shown already
    if not st.session_state['dialog_shown']:
        welcome_dialog()
        st.session_state['dialog_shown'] = True  # Ensure the state is set regardless of how the dialog is closed

    st.sidebar.image("images/buddybetes_logo.png", use_column_width=True)
    st.sidebar.markdown("This is BuddyBetes, your best friend in diabetes care.")
    st.sidebar.divider()

    if st.session_state['authentication_status']:
        st.sidebar.title(f"Welcome, {st.session_state['name']}!")
        st.sidebar.markdown("Choose any in the menu:")
        
        # Menu for logged-in users
        if st.sidebar.button("Analytics"):
            st.session_state['page'] = 'Analytics'
        if st.sidebar.button("Log Data"):
            st.session_state['page'] = 'Log Data'
        if st.sidebar.button("Profile"):
            st.session_state['page'] = 'Profile'
        if st.sidebar.button("Email Notifications"):
            st.session_state['page'] = 'Settings'
        if st.sidebar.button("Logout"):
            logout_user()
        
        # Automatically redirect to the Analytics page if logged in
        if st.session_state['page'] == 'Login':
            st.session_state['page'] = 'Analytics'
    else:
        # Menu for non-logged-in users
        if st.sidebar.button("Login"):
            st.session_state['page'] = 'Login'
        if st.sidebar.button("Create an Account"):
            st.session_state['page'] = 'Register'

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

def logout_user():
    st.session_state['authentication_status'] = None
    st.session_state['name'] = None
    st.session_state['username'] = None
    st.session_state['page'] = 'Login'
    st.success("You have been logged out successfully.")

start_scheduler_thread()

if __name__ == "__main__":
    main()
