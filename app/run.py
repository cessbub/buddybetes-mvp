import streamlit as st

# Initialize session state keys
if 'modal_shown' not in st.session_state:
    st.session_state['modal_shown'] = False

# Function to show modal
def show_modal():
    st.markdown(
        """
        <style>
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 9999;
        }
        .modal-content {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 600px;
        }
        .modal-button {
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
        <div class="modal">
            <div class="modal-content">
                <h2>Welcome to BuddyBetes MVP 🎉</h2>
                <p>Hi there! Thank you for trying out the MVP of BuddyBetes. We're excited to have you here!</p>
                <h3>Important Information 📢</h3>
                <ul>
                    <li>This is an <strong>MVP</strong> version, so some features might be limited or in progress.</li>
                    <li>Currently, the database is not persistent. This means that any data you enter will be lost if you refresh the page or close the browser. 😅</li>
                    <li>For the best experience, please use a <strong>laptop/PC</strong> to view and interact with the application. 🖥️</li>
                </ul>
                <p>We appreciate your understanding and look forward to your feedback!</p>
                <button class="modal-button" onclick="close_modal()">Okay</button>
            </div>
        </div>
        <script>
        function close_modal() {
            document.querySelector('.modal').style.display = 'none';
            fetch('/?modal_shown=true');
        }
        </script>
        """,
        unsafe_allow_html=True,
    )

# Main function to run the app
def main():
    # Initialize session state
    if 'modal_shown' not in st.session_state:
        st.session_state['modal_shown'] = False

    # Show modal if not shown already
    if not st.session_state['modal_shown']:
        show_modal()
        st.session_state['modal_shown'] = True

    st.write("This is the main app content.")

if __name__ == "__main__":
    main()
