import streamlit as st
import mysql.connector
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="datacraft",
        database="retailiq"
    )

def login(pin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE pin = %s AND is_active = TRUE", (pin,))
    user = cursor.fetchone()
    conn.close()
    return user

def log_activity(user_id, action, details=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
        (user_id, action, details)
    )
    conn.commit()
    conn.close()

st.set_page_config(page_title="RetailIQ", page_icon="🛒", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🛒 RetailIQ")
    st.subheader("by Datacraft")
    st.divider()
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.subheader("Staff Login")
        pin = st.text_input("Enter your PIN", type="password", max_chars=6)
        
        if st.button("Login"):
            if pin:
                user = login(pin)
                if user:
                    st.session_state.user = user
                    log_activity(user['user_id'], "LOGIN", f"{user['full_name']} logged in")
                    st.rerun()
                else:
                    st.error("Invalid PIN. Please try again.")
            else:
                st.warning("Please enter your PIN.")

else:
    user = st.session_state.user
    
    st.sidebar.title(f"Welcome, {user['full_name']}")
    st.sidebar.write(f"Role: {user['role'].title()}")
    st.sidebar.divider()
    
    if user['role'] == 'manager':
        menu = st.sidebar.selectbox("Menu", [
            "Sales Dashboard",
            "POS - New Sale",
            "Stock Management",
            "Inventory",
            "Staff Activity Log",
            "Void Sales"
        ])
    else:
        menu = st.sidebar.selectbox("Menu", [
            "POS - New Sale"
        ])
    
    if st.sidebar.button("Logout"):
        log_activity(user['user_id'], "LOGOUT", f"{user['full_name']} logged out")
        st.session_state.user = None
        st.rerun()
    
    st.title(f"🛒 RetailIQ — {menu}")
    st.divider()
    
    if menu == "POS - New Sale":
        st.info("POS coming soon")
    elif menu == "Sales Dashboard":
        st.info("Sales Dashboard coming soon")
    elif menu == "Stock Management":
        st.info("Stock Management coming soon")
    elif menu == "Inventory":
        st.info("Inventory coming soon")
    elif menu == "Staff Activity Log":
        st.info("Activity Log coming soon")
    elif menu == "Void Sales":
        st.info("Void Sales coming soon")