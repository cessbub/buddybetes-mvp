import streamlit as st
from database import create_connection

def log_data_form(username):
    st.subheader("Log Your Health Data")

    # create the form
    with st.form(key='health_data_form'):
        date = st.date_input("Date")
        time = st.time_input("Time")
        glucose_level_str = st.text_input("Glucose Level (mg/dL)", placeholder="70")
        bp_systolic_str = st.text_input("Blood Pressure (Systolic) (mmHg)", placeholder="180")
        bp_diastolic_str = st.text_input("Blood Pressure (Diastolic) (mmHg)", placeholder="20")
        meal_context = st.selectbox("Meal Context", ["Before Breakfast", "After Breakfast", "Before Lunch", "After Lunch", "Before Dinner", "After Dinner", "Other"])
        food_intake = st.text_area("Food Intake", placeholder="Describe your food intake")
        mood = st.selectbox("Mood", ["Happy", "Sad", "Neutral", "Anxious", "Stressed"])
        symptoms = st.text_area("Symptoms", placeholder="Describe any symptoms")

        submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        try:
            # Convert text inputs to appropriate types
            glucose_level = float(glucose_level_str) if glucose_level_str else 0.0
            bp_systolic = int(bp_systolic_str) if bp_systolic_str else 0
            bp_diastolic = int(bp_diastolic_str) if bp_diastolic_str else 0

            conn = create_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO health_data (user_id, date, time, glucose_level, bp_systolic, bp_diastolic, food_intake, mood, symptoms, meal_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, date.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), glucose_level, bp_systolic, bp_diastolic, food_intake, mood, symptoms, meal_context))
            conn.commit()

            conn.close()
            st.success("Health data logged successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

