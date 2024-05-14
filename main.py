import streamlit as st
import psycopg2
from datetime import date
import pandas as pd
import plotly.express as px
from PIL import Image

# Establish a connection to PostgreSQL
mydb = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="1234",
    database="irb_projects",
    port="5432"
)
mycursor = mydb.cursor()
print("Connection Established")

user_login = {
    "mvr": "1234",
    "tcbot": "2345",
    "kkbot": "3456",
    "admin": "admin"
}

def validate_user(username, password):
    return user_login.get(username.lower()) == password

def main():
    st.title("IRB_Revenue Entering sheet")

    if 'login_state' not in st.session_state:
        st.session_state.login_state = "initial"

    if st.session_state.login_state != "authenticated":
        username_input = st.text_input("Username", key="username_input")
        password_input = st.text_input("Password", type="password", key="password_input")
        
        if st.button("Login"):
            if validate_user(username_input, password_input):
                st.session_state.login_state = "authenticated"
                st.session_state.username = username_input  # Store username in session state
            else:
                st.error("Invalid username or password!")
                return

    if st.session_state.login_state == "authenticated":
        username_display = st.text_input("Username", key="username_display", value=st.session_state.username)
        st.success("Welcome " + username_display.capitalize())

        # Logout Button
        if st.button("Logout"):
            st.session_state.login_state = "initial"
            st.session_state.username = None

        # Check if username is not None before using lower()
        if st.session_state.username and st.session_state.username.lower() in ["mvr", "tcbot", "kkbot"]:
            st.empty() 
            st.subheader(f"Enter the Revenue details and transaction details of {username_input}")
            project_name = username_input
            Total_collection = st.text_input("Enter the total collection")
            Total_ETC_collection = st.text_input("Enter the ETC Collection")
            Total_Exempted_transaction = st.text_input("Enter the Exempted transactions")
            entry_date = st.date_input("Enter the Date", value=date.today())
            if st.button("Update"):
                sql = "insert into users (project_name,Total_collection,Total_ETC_collection,Total_Exempted_transaction,entry_date)values(%s,%s,%s,%s,%s)"
                val = (project_name, Total_collection, Total_ETC_collection, Total_Exempted_transaction, entry_date)
                mycursor.execute(sql, val)
                mydb.commit()
                st.success("Record Updated Successfully!!!")

        elif st.session_state.username and st.session_state.username.lower() == "admin":
            st.empty()  
            query_total_collection = "SELECT project_name, total_collection FROM users"
            df_total_collection = pd.read_sql(query_total_collection, mydb)

            query_total_etc_collection = "SELECT project_name, total_etc_collection FROM users"
            df_total_etc_collection = pd.read_sql(query_total_etc_collection, mydb)

            if not df_total_collection.empty:
                st.subheader("Sunburst Chart - Total Collection")
                fig1 = px.sunburst(df_total_collection, path=['project_name'], values='total_collection')
                st.plotly_chart(fig1)
            
            if not df_total_etc_collection.empty:
                st.subheader("Bar Chart - Total ETC Collection")
                fig2 = px.bar(df_total_etc_collection, x='project_name', y='total_etc_collection', title='Total ETC Collection per Project')
                st.plotly_chart(fig2)

if __name__ == "__main__":
    main()
