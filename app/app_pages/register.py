import streamlit as st
from auth import authenticate
from database import create_connection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_user():
    st.subheader("Create New Account")

    with st.form(key='registration_form'):
        username = st.text_input("Username", placeholder="Enter your username")
        email = st.text_input("Email", placeholder="Enter your email")
        name = st.text_input("Name", placeholder="Enter your name")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit_button = st.form_submit_button(label="Register")

    if submit_button:
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            hashed_password = pwd_context.hash(password)
            try:
                conn = create_connection()
                c = conn.cursor()
                c.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
                if c.fetchone()[0] > 0:
                    st.error("Username already exists. Please choose a different username.")
                else:
                    c.execute('''
                        INSERT INTO users (username, email, name, password, email_reminder, reminder_time)
                        VALUES (?, ?, ?, ?, 'Daily', '07:58')
                    ''', (username, email, name, hashed_password))
                    conn.commit()
                    st.success("User registered successfully! Please log in.")
                conn.close()
            except Exception as e:
                st.error(f"An error occurred while registering the user: {e}")
    
    if st.button("Have an account? Login Here"):
        st.session_state['page'] = 'Login'
        st.experimental_rerun()  # Force a rerun to navigate to Login
