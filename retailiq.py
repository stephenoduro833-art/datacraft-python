import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="datacraft",
            database="retailiq"
        )
    except mysql.connector.Error:
        st.error("Database connection unavailable. Please contact your administrator.")
        st.stop()

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

def get_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.product_name, p.category, p.selling_price, i.quantity 
        FROM products p 
        JOIN inventory i ON p.product_id = i.product_id 
        WHERE p.is_active = TRUE AND i.quantity > 0
    """)
    products = cursor.fetchall()
    conn.close()
    return products

def save_sale(cashier_id, cart, payment_method):
    conn = get_connection()
    cursor = conn.cursor()
    total = sum(item['subtotal'] for item in cart)
    now = datetime.now()
    cursor.execute("""
        INSERT INTO sales (cashier_id, sale_date, sale_time, payment_method, total_amount)
        VALUES (%s, %s, %s, %s, %s)
    """, (cashier_id, now.date(), now.time(), payment_method, total))
    sale_id = cursor.lastrowid
    for item in cart:
        cursor.execute("""
            INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """, (sale_id, item['product_id'], item['quantity'], item['unit_price'], item['subtotal']))
        cursor.execute("""
            UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s
        """, (item['quantity'], item['product_id']))
        cursor.execute("""
            INSERT INTO stock_movements (product_id, movement_type, quantity, reason, recorded_by)
            VALUES (%s, 'sale', %s, %s, %s)
        """, (item['product_id'], item['quantity'], f"Sale ID {sale_id}", cashier_id))
    conn.commit()
    conn.close()
    return sale_id

st.set_page_config(page_title="RetailIQ", page_icon="🛒", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #f4f4f4;
    }
    section[data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: white;
        color: #1a1a2e !important;
        border: none;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🛒 RetailIQ")
    st.subheader("by Datacraft")
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
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
        menu = st.sidebar.selectbox("Menu", ["POS - New Sale"])

    if st.sidebar.button("Logout"):
        log_activity(user['user_id'], "LOGOUT", f"{user['full_name']} logged out")
        st.session_state.user = None
        st.rerun()

    st.title(f"🛒 RetailIQ — {menu}")
    st.divider()

    if menu == "POS - New Sale":
        if "cart" not in st.session_state:
            st.session_state.cart = []
        products = get_products()
        product_names = [p['product_name'] for p in products]
        product_map = {p['product_name']: p for p in products}
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Add Item")
            selected = st.selectbox("Select Product", product_names)
            product = product_map[selected]
            st.write(f"Price: GHS {product['selling_price']} | Stock: {product['quantity']}")
            qty = st.number_input("Quantity", min_value=1, max_value=product['quantity'], value=1)
            if st.button("Add to Cart"):
                existing = next((i for i in st.session_state.cart if i['product_id'] == product['product_id']), None)
                if existing:
                    existing['quantity'] += qty
                    existing['subtotal'] = existing['quantity'] * existing['unit_price']
                else:
                    st.session_state.cart.append({
                        "product_id": product['product_id'],
                        "product_name": product['product_name'],
                        "quantity": qty,
                        "unit_price": product['selling_price'],
                        "subtotal": qty * product['selling_price']
                    })
                st.success(f"Added {qty} x {selected}")
        with col2:
            st.subheader("Cart")
            if st.session_state.cart:
                cart_df = pd.DataFrame(st.session_state.cart)[['product_name', 'quantity', 'unit_price', 'subtotal']]
                cart_df.columns = ['Product', 'Qty', 'Unit Price', 'Subtotal']
                st.dataframe(cart_df, use_container_width=True)
                total = sum(i['subtotal'] for i in st.session_state.cart)
                st.metric("Total", f"GHS {total:,.2f}")
                payment = st.selectbox("Payment Method", ["cash", "momo", "card"])
                if st.button("Confirm Sale"):
                    sale_id = save_sale(user['user_id'], st.session_state.cart, payment)
                    log_activity(user['user_id'], "SALE", f"Sale ID {sale_id} - GHS {total}")
                    st.session_state.cart = []
                    st.success(f"Sale #{sale_id} confirmed successfully")
                    st.rerun()
                if st.button("Clear Cart"):
                    st.session_state.cart = []
                    st.rerun()
            else:
                st.info("Cart is empty. Add products to get started.")

    elif menu == "Sales Dashboard":
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.sale_id, s.sale_date, s.sale_time, u.full_name AS cashier,
                   s.payment_method, s.total_amount, s.is_voided
            FROM sales s
            JOIN users u ON s.cashier_id = u.user_id
            ORDER BY s.sale_date DESC, s.sale_time DESC
        """)
        sales = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(sales)
        active_sales = df[df['is_voided'] == 0]
        total_revenue = active_sales['total_amount'].sum()
        total_transactions = len(active_sales)
        avg_transaction = active_sales['total_amount'].mean() if total_transactions > 0 else 0
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"GHS {total_revenue:,.2f}")
        col2.metric("Total Transactions", total_transactions)
        col3.metric("Avg Transaction", f"GHS {avg_transaction:,.2f}")
        st.divider()
        st.subheader("Sales by Cashier")
        cashier_sales = active_sales.groupby('cashier')['total_amount'].sum().reset_index()
        cashier_sales.columns = ['Cashier', 'Total Sales']
        st.dataframe(cashier_sales, use_container_width=True)
        st.divider()
        st.subheader("Sales by Payment Method")
        payment_sales = active_sales.groupby('payment_method')['total_amount'].sum().reset_index()
        payment_sales.columns = ['Payment Method', 'Total']
        st.dataframe(payment_sales, use_container_width=True)
        st.divider()
        st.subheader("All Transactions")
        st.dataframe(df, use_container_width=True)

    elif menu == "Stock Management":
        st.subheader("Record New Stock")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.product_id, p.product_name, i.quantity 
            FROM products p 
            JOIN inventory i ON p.product_id = i.product_id
            WHERE p.is_active = TRUE
        """)
        all_products = cursor.fetchall()
        conn.close()
        product_names = [p['product_name'] for p in all_products]
        product_map = {p['product_name']: p for p in all_products}
        selected = st.selectbox("Select Product", product_names)
        product = product_map[selected]
        st.write(f"Current Stock: {product['quantity']}")
        qty_in = st.number_input("Quantity Received", min_value=1, value=1)
        reason = st.text_input("Supplier / Notes", placeholder="e.g. Delivered by ABC Suppliers")
        if st.button("Record Stock In"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inventory SET quantity = quantity + %s WHERE product_id = %s",
                (qty_in, product['product_id'])
            )
            cursor.execute("""
                INSERT INTO stock_movements (product_id, movement_type, quantity, reason, recorded_by)
                VALUES (%s, 'stock_in', %s, %s, %s)
            """, (product['product_id'], qty_in, reason, user['user_id']))
            conn.commit()
            conn.close()
            log_activity(user['user_id'], "STOCK IN", f"{qty_in} units of {selected} recorded")
            st.success(f"Stock updated. {selected} now has {product['quantity'] + qty_in} units.")
            st.rerun()

    elif menu == "Inventory":
        st.subheader("Current Inventory")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.product_name, p.category, p.selling_price, p.cost_price,
                   i.quantity, p.reorder_level,
                   CASE WHEN i.quantity <= p.reorder_level THEN 'Low Stock' ELSE 'OK' END AS status
            FROM products p
            JOIN inventory i ON p.product_id = i.product_id
            WHERE p.is_active = TRUE
            ORDER BY i.quantity ASC
        """)
        inventory = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(inventory)
        total_products = len(df)
        low_stock = len(df[df['status'] == 'Low Stock'])
        col1, col2 = st.columns(2)
        col1.metric("Total Products", total_products)
        col2.metric("Low Stock Alerts", low_stock)
        st.divider()
        st.dataframe(df, use_container_width=True)
        st.divider()
        st.subheader("Stock Movement History")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sm.movement_date, p.product_name, sm.movement_type,
                   sm.quantity, sm.reason, u.full_name
            FROM stock_movements sm
            JOIN products p ON sm.product_id = p.product_id
            JOIN users u ON sm.recorded_by = u.user_id
            ORDER BY sm.movement_date DESC
            LIMIT 50
        """)
        movements = cursor.fetchall()
        conn.close()
        movements_df = pd.DataFrame(movements)
        st.dataframe(movements_df, use_container_width=True)

    elif menu == "Staff Activity Log":
        st.subheader("Staff Activity Log")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT al.logged_at, u.full_name, u.role, al.action, al.details
            FROM activity_log al
            JOIN users u ON al.user_id = u.user_id
            ORDER BY al.logged_at DESC
            LIMIT 100
        """)
        logs = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True)

    elif menu == "Void Sales":
        st.subheader("Void a Sale")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.sale_id, s.sale_date, s.sale_time, u.full_name AS cashier,
                   s.payment_method, s.total_amount
            FROM sales s
            JOIN users u ON s.cashier_id = u.user_id
            WHERE s.is_voided = FALSE
            ORDER BY s.sale_date DESC, s.sale_time DESC
        """)
        active_sales = cursor.fetchall()
        conn.close()
        if active_sales:
            df = pd.DataFrame(active_sales)
            st.dataframe(df, use_container_width=True)
            sale_ids = [s['sale_id'] for s in active_sales]
            selected_id = st.selectbox("Select Sale ID to Void", sale_ids)
            void_reason = st.text_input("Reason for Void", placeholder="e.g. Customer returned items")
            if st.button("Void Sale"):
                if void_reason:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE sales SET is_voided = TRUE, voided_by = %s, void_reason = %s
                        WHERE sale_id = %s
                    """, (user['user_id'], void_reason, selected_id))
                    conn.commit()
                    conn.close()
                    log_activity(user['user_id'], "VOID", f"Sale ID {selected_id} voided. Reason: {void_reason}")
                    st.success(f"Sale #{selected_id} has been voided.")
                    st.rerun()
                else:
                    st.warning("Please enter a reason for voiding this sale.")
        else:
            st.info("No active sales to void.")