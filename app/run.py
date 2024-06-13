import streamlit as st
from streamlit_modal import Modal

# Initialize session state keys
if 'modal_shown' not in st.session_state:
    st.session_state['modal_shown'] = False

# Function to show modal
def show_modal():
    modal = Modal("Welcome Modal", key="welcome-modal", padding=20, max_width=744)
    if not st.session_state["modal_shown"]:
        modal.open()
        st.session_state["modal_shown"] = True

    if modal.is_open():
        with modal.container():
            st.write("Hi there! Thank you for trying out the MVP of BuddyBetes. We're excited to have you here!")
            st.markdown("### Important Information 📢")
            st.markdown("- This is an **MVP** version, so some features might be limited or in progress.")
            st.markdown("- Currently, the database is not persistent. This means that any data you enter will be lost if you refresh the page or close the browser. 😅")
            st.markdown("- For the best experience, please use a **laptop/PC** to view and interact with the application. 🖥️")
            st.markdown("We appreciate your understanding and look forward to your feedback!")

            if st.button("Okay"):
                modal.close()

# Main function to run the app
def main():
    # Show modal if not shown already
    show_modal()

    st.write("This is the main app content.")

if __name__ == "__main__":
    main()
