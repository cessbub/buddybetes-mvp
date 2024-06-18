import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import create_connection

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
        fig, ax = plt.subplots()
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
