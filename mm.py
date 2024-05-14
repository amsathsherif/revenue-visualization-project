import streamlit as st
from pages.dashboard import dashboard_page
import psycopg2
from datetime import date
import pandas as pd
import plotly.express as px

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
    image_path = r"IRB_New_Logo.png"
    st.image(image_path, width=380, caption='Highways are growing while we choose the IRB Projects')

    if 'login_state' not in st.session_state:
        st.session_state.login_state = "initial"

    if st.session_state.login_state == "initial":
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")

        if st.button("Login"):
            if validate_user(username, password):
                st.session_state.login_state = "valid"
                st.session_state.username = username
            else:
                st.error("Invalid username or password!")
    elif st.session_state.login_state == "valid":
        dashboard_page()  # Display the dashboard content


def dashboard_page():
    st.title("Dashboard")

    # Add logout button in the top left corner
    logout_clicked = st.button("Logout")

    if logout_clicked:
        st.session_state.login_state = "initial"
        st.experimental_rerun()

    # Access username from session state
    username = st.session_state.username

    # Conditional content based on user role
    if username.lower() in ["mvr", "tcbot", "kkbot"]:
        st.subheader(f"Enter the Revenue details and transaction details of {username}")
        project_name = username
        Total_collection = st.text_input("Enter the total collection")
        Total_ETC_collection = st.text_input("Enter the ETC Collection")
        Total_Exempted_transaction = st.text_input("Enter the Exempted transactions")
        entry_date = st.date_input("Enter the Date", min_value=date.today(), value=date.today())

        if st.button("Update"):
            # Check if the record for this user and date already exists
            check_query = f"SELECT * FROM users WHERE project_name = '{project_name}' AND entry_date = '{entry_date}'"
            mycursor.execute(check_query)
            existing_record = mycursor.fetchone()

            if existing_record:
                st.error("You have already entered details for this date.")
            else:
                # Insert the new record
                sql = "insert into users (project_name,Total_collection,Total_ETC_collection,Total_Exempted_transaction,entry_date)values(%s,%s,%s,%s,%s)"
                val = (project_name, Total_collection, Total_ETC_collection, Total_Exempted_transaction, entry_date)
                mycursor.execute(sql, val)
                mydb.commit()
                st.success("Record Updated Successfully!!!")

    elif username.lower() == "admin":  # Visualizations for admin
        st.empty()  
        start_date = st.date_input("Select start date")
        end_date = st.date_input("Select end date")
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        if st.button("Submit"):
            query_total_collection = f"SELECT project_name, total_collection FROM users WHERE entry_date BETWEEN '{start_date_str}' AND '{end_date_str}'"
            df_total_collection = pd.read_sql(query_total_collection, mydb)

            query_total_etc_collection = f"SELECT project_name, total_etc_collection FROM users WHERE entry_date BETWEEN '{start_date_str}' AND '{end_date_str}'"
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
