import streamlit as st
from auth import authenticate

def login_user():
    st.subheader("Login to Your Account")

    with st.form(key='login_form'):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
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
                st.experimental_rerun()  # Force a rerun to navigate to Analytics
            else:
                st.error('Incorrect username or password. Please try again.')
        except Exception as e:
            st.error(f"An error occurred during login: {e}")

    if st.button("Create new account here"):
        st.session_state['page'] = 'Register'
        st.experimental_rerun()  # Force a rerun to navigate to Register
