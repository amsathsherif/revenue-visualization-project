import streamlit as st
from pages.dashboard import dashboard_page
import psycopg2

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
     

if __name__ == "__main__":
    main()
