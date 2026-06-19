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
            database="retailiq_v2"
        )
    except mysql.connector.Error:
        st.error("Database connection unavailable. Please contact your administrator.")
        st.stop()

def log_activity(user_id, action, details=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
        (user_id, action, details)
    )
    conn.commit()
    conn.close()

def login(pin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE pin = %s AND is_active = TRUE", (pin,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.barcode, p.product_name, p.category,
               p.cost_price, p.selling_price, p.reorder_level, p.is_active,
               COALESCE(i.quantity, 0) AS quantity
        FROM products p
        LEFT JOIN inventory i ON p.product_id = i.product_id
        ORDER BY p.product_name
    """)
    products = cursor.fetchall()
    conn.close()
    return products

def get_all_staff():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users ORDER BY full_name")
    staff = cursor.fetchall()
    conn.close()
    return staff

def get_available_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.product_name, p.selling_price, i.quantity
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
        cursor.execute(
            "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s",
            (item['quantity'], item['product_id'])
        )
        cursor.execute("""
            INSERT INTO stock_movements (product_id, movement_type, quantity, reason, recorded_by)
            VALUES (%s, 'sale', %s, %s, %s)
        """, (item['product_id'], item['quantity'], f"Sale ID {sale_id}", cashier_id))
    conn.commit()
    conn.close()
    return sale_id

def get_inventory_data():
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
    data = cursor.fetchall()
    conn.close()
    return data

def get_sales_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.sale_id, s.sale_date, s.sale_time, u.full_name AS cashier,
               s.payment_method, s.total_amount, s.is_voided
        FROM sales s
        JOIN users u ON s.cashier_id = u.user_id
        ORDER BY s.sale_date DESC, s.sale_time DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_expenses_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.expense_id, e.expense_date, e.category, e.description,
               e.amount, u.full_name AS recorded_by
        FROM expenses e
        JOIN users u ON e.recorded_by = u.user_id
        ORDER BY e.expense_date DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data


st.set_page_config(page_title="RetailIQ", page_icon="🛒", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: #F5F7FA;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    section[data-testid="stSidebar"] {
        background-color: #0E2A47;
    }
    section[data-testid="stSidebar"] * {
        color: #F5F7FA !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1B4F8C !important;
        color: #F5F7FA !important;
        border-color: #2EC4DE !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #F5F7FA !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #F5F7FA !important;
    }
    ul[data-baseweb="menu"] {
        background-color: #1B4F8C !important;
    }
    ul[data-baseweb="menu"] li {
        color: #F5F7FA !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #2EC4DE;
        color: #0E2A47 !important;
        border: none;
        font-weight: 600;
    }
    h1, h2, h3 {
        color: #0E2A47;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        border-top: 3px solid #2EC4DE;
        padding: 12px 16px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(14,42,71,0.08);
    }
    .stButton button {
        background-color: #1B4F8C;
        color: white;
        border-radius: 4px;
        border: none;
    }
    .stButton button:hover {
        background-color: #2EC4DE;
        color: #0E2A47;
    }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    col_a, col_b, col_c = st.columns([1.5, 1, 1.5])
    with col_b:
        st.image("assets/logo.png", width=220)
    st.markdown("<h2 style='text-align:center;color:#0E2A47;'>RetailIQ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#5C7A99;'>Where Data Meets Craft</p>", unsafe_allow_html=True)
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.subheader("Staff Login")
        pin = st.text_input("Enter your PIN", type="password", max_chars=10)
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
    st.sidebar.image("assets/logo.png", use_container_width=True)
    st.sidebar.markdown("<p style='color:#2EC4DE;font-size:13px;'>Where Data Meets Craft</p>", unsafe_allow_html=True)
    st.sidebar.divider()
    st.sidebar.title(f"Welcome, {user['full_name']}")
    st.sidebar.write(f"Role: {user['role'].title()}")
    st.sidebar.divider()

    if user['role'] == 'manager':
        menu = st.sidebar.selectbox("Menu", [
            "Sales Dashboard",
            "POS - New Sale",
            "Stock Management",
            "Inventory",
            "Product Management",
            "Staff Management",
            "Expense Tracking",
            "Profit & Loss",
            "Reports",
            "Staff Activity Log",
            "Void Sales"
        ])
    else:
        menu = st.sidebar.selectbox("Menu", ["POS - New Sale"])

    if st.sidebar.button("Logout"):
        log_activity(user['user_id'], "LOGOUT", f"{user['full_name']} logged out")
        st.session_state.user = None
        st.rerun()

    st.markdown(f"""
    <h2 style='color:#0E2A47;'>RetailIQ <span style='color:#2EC4DE;'>—</span> {menu}</h2>
    <div style='height:3px;width:80px;background:linear-gradient(90deg,#0E2A47,#2EC4DE);margin-bottom:20px;'></div>
    """, unsafe_allow_html=True)

    if menu == "POS - New Sale":
        if "cart" not in st.session_state:
            st.session_state.cart = []

        products = get_available_products()
        product_names = [p['product_name'] for p in products]
        product_map = {p['product_name']: p for p in products}

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Add Item")
            if product_names:
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
            else:
                st.warning("No products available. Add products first.")

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
        sales = get_sales_data()
        df = pd.DataFrame(sales)

        inventory = get_inventory_data()
        inv_df = pd.DataFrame(inventory)
        low_stock_items = inv_df[inv_df['status'] == 'Low Stock']
        if not low_stock_items.empty:
            st.warning(f"⚠️ **{len(low_stock_items)} product(s) are low on stock!**")
            with st.expander("View Low Stock Items"):
                st.dataframe(
                    low_stock_items[['product_name', 'category', 'quantity', 'reorder_level']],
                    use_container_width=True
                )
            st.divider()

        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            filter_mode = st.selectbox("Period", ["Today", "This Week", "This Month", "Custom Range", "All Time"])

        today = datetime.now().date()
        if filter_mode == "Today":
            start_date = end_date = today
        elif filter_mode == "This Week":
            start_date = today - pd.Timedelta(days=today.weekday())
            end_date = today
        elif filter_mode == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif filter_mode == "Custom Range":
            with col_f2:
                start_date = st.date_input("From", value=today.replace(day=1))
            with col_f3:
                end_date = st.date_input("To", value=today)
        else:
            start_date = end_date = None

        if not df.empty:
            df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
            active_sales = df[df['is_voided'] == 0]
            if start_date and end_date:
                active_sales = active_sales[
                    (active_sales['sale_date'] >= start_date) &
                    (active_sales['sale_date'] <= end_date)
                ]
        else:
            active_sales = df

        total_revenue = active_sales['total_amount'].sum() if not active_sales.empty else 0
        total_transactions = len(active_sales)
        avg_transaction = active_sales['total_amount'].mean() if total_transactions > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"GHS {total_revenue:,.2f}")
        col2.metric("Total Transactions", total_transactions)
        col3.metric("Avg Transaction", f"GHS {avg_transaction:,.2f}")

        st.divider()
        st.subheader("📅 Daily Sales Summary")
        if not active_sales.empty:
            daily = active_sales.groupby('sale_date')['total_amount'].agg(['sum', 'count']).reset_index()
            daily.columns = ['Date', 'Total Sales (GHS)', 'Transactions']
            daily = daily.sort_values('Date', ascending=False)
            st.dataframe(daily, use_container_width=True)
        else:
            st.info("No sales data for selected period.")

        st.divider()
        st.subheader("Sales by Cashier")
        if not active_sales.empty:
            cashier_sales = active_sales.groupby('cashier')['total_amount'].sum().reset_index()
            cashier_sales.columns = ['Cashier', 'Total Sales']
            st.dataframe(cashier_sales, use_container_width=True)
        else:
            st.info("No data.")

        st.divider()
        st.subheader("Sales by Payment Method")
        if not active_sales.empty:
            payment_sales = active_sales.groupby('payment_method')['total_amount'].sum().reset_index()
            payment_sales.columns = ['Payment Method', 'Total']
            st.dataframe(payment_sales, use_container_width=True)
        else:
            st.info("No data.")

        st.divider()
        st.subheader("All Transactions")
        st.dataframe(active_sales, use_container_width=True)

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

        movement_type = st.selectbox("Movement Type", ["stock_in", "adjustment", "damaged"])
        qty_change = st.number_input("Quantity", min_value=1, value=1)
        reason = st.text_input("Reason / Notes")

        if st.button("Record Movement"):
            conn = get_connection()
            cursor = conn.cursor()
            if movement_type == "stock_in":
                cursor.execute(
                    "UPDATE inventory SET quantity = quantity + %s WHERE product_id = %s",
                    (qty_change, product['product_id'])
                )
            else:
                cursor.execute(
                    "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s",
                    (qty_change, product['product_id'])
                )
            cursor.execute("""
                INSERT INTO stock_movements (product_id, movement_type, quantity, reason, recorded_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (product['product_id'], movement_type, qty_change, reason, user['user_id']))
            conn.commit()
            conn.close()
            log_activity(user['user_id'], "STOCK MOVEMENT", f"{movement_type} - {qty_change} units of {selected}")
            st.success(f"Stock movement recorded for {selected}.")
            st.rerun()

    elif menu == "Inventory":
        st.subheader("Current Inventory")
        inventory = get_inventory_data()
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

    elif menu == "Product Management":
        tab1, tab2 = st.tabs(["Add Product", "Manage Products"])
        with tab1:
            st.subheader("Add New Product")
            col1, col2 = st.columns(2)
            with col1:
                barcode = st.text_input("Barcode (optional)")
                product_name = st.text_input("Product Name")
                category = st.text_input("Category")
            with col2:
                cost_price = st.number_input("Cost Price (GHS)", min_value=0.0, format="%.2f")
                selling_price = st.number_input("Selling Price (GHS)", min_value=0.0, format="%.2f")
                reorder_level = st.number_input("Reorder Level", min_value=0, value=5)
                opening_stock = st.number_input("Opening Stock", min_value=0, value=0)

            if cost_price > 0 and selling_price > 0:
                margin = ((selling_price - cost_price) / selling_price) * 100
                color = "green" if margin >= 20 else "orange" if margin >= 10 else "red"
                st.markdown(f"**Profit Margin:** :{color}[{margin:.1f}%]")

            if st.button("Add Product"):
                if product_name and selling_price > 0 and cost_price > 0:
                    conn = get_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT product_id FROM products WHERE LOWER(product_name) = LOWER(%s)",
                        (product_name,)
                    )
                    existing = cursor.fetchone()
                    conn.close()
                    if existing:
                        st.warning(
                            f"A product named **{product_name}** already exists. "
                            "Edit it in the Manage Products tab instead."
                        )
                    else:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO products (barcode, product_name, category, cost_price, selling_price, reorder_level)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (barcode or None, product_name, category, cost_price, selling_price, reorder_level))
                        product_id = cursor.lastrowid
                        cursor.execute(
                            "INSERT INTO inventory (product_id, quantity) VALUES (%s, %s)",
                            (product_id, opening_stock)
                        )
                        conn.commit()
                        conn.close()
                        log_activity(user['user_id'], "ADD PRODUCT", f"Added {product_name}")
                        st.success(f"{product_name} added successfully.")
                        st.rerun()
                else:
                    st.warning("Please fill in product name, cost price and selling price.")

        with tab2:
            st.subheader("All Products")
            products = get_all_products()

            col_search, col_cat, col_status = st.columns([2, 1, 1])
            with col_search:
                search_query = st.text_input("🔍 Search by name", placeholder="e.g. Rice")
            with col_cat:
                categories = sorted(set(p["category"] for p in products if p["category"]))
                cat_filter = st.selectbox("Category", ["All"] + categories)
            with col_status:
                status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])

            filtered = products
            if search_query:
                filtered = [p for p in filtered if search_query.lower() in p["product_name"].lower()]
            if cat_filter != "All":
                filtered = [p for p in filtered if p["category"] == cat_filter]
            if status_filter == "Active":
                filtered = [p for p in filtered if p["is_active"]]
            elif status_filter == "Inactive":
                filtered = [p for p in filtered if not p["is_active"]]

            if filtered:
                df = pd.DataFrame(filtered)
                df["margin_%"] = df.apply(
                    lambda r: round(((r["selling_price"] - r["cost_price"]) / r["selling_price"]) * 100, 1)
                    if r["selling_price"] > 0 else 0,
                    axis=1
                )
                df["status"] = df["is_active"].map({True: "✅ Active", False: "❌ Inactive"})
                display_cols = ["product_name", "category", "barcode", "cost_price",
                                "selling_price", "margin_%", "quantity", "reorder_level", "status"]
                st.dataframe(df[display_cols], use_container_width=True)
            else:
                st.info("No products match your filters.")

            st.divider()
            st.subheader("Edit Product")
            product_names = [p["product_name"] for p in products]

            if product_names:
                selected = st.selectbox("Select Product", product_names)
                product = next(p for p in products if p["product_name"] == selected)

                if product["selling_price"] > 0:
                    margin = ((product["selling_price"] - product["cost_price"]) / product["selling_price"]) * 100
                    st.caption(f"Current margin: **{margin:.1f}%**")

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_cost = st.number_input("Cost Price", value=float(product["cost_price"]), format="%.2f")
                    new_sell = st.number_input("Selling Price", value=float(product["selling_price"]), format="%.2f")
                    new_reorder = st.number_input("Reorder Level", value=int(product["reorder_level"]))
                    active = st.checkbox("Active", value=bool(product["is_active"]))

                with col_e2:
                    if new_sell > 0:
                        new_margin = ((new_sell - new_cost) / new_sell) * 100
                        color = "green" if new_margin >= 20 else "orange" if new_margin >= 10 else "red"
                        st.markdown(f"**New Margin:** :{color}[{new_margin:.1f}%]")

                    st.markdown("**Stock Adjustment**")
                    st.caption(f"Current stock: **{product['quantity']}** units")
                    adj_type = st.selectbox("Adjustment Type", ["Add Stock", "Remove Stock", "Set Exact Quantity"])
                    adj_qty = st.number_input("Quantity", min_value=0, value=0)
                    adj_reason = st.text_input("Reason (optional)", placeholder="e.g. Stocktake correction")

                col_btn1, col_btn2 = st.columns([1, 1])

                with col_btn1:
                    if st.button("Update Product"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE products
                            SET cost_price=%s, selling_price=%s, reorder_level=%s, is_active=%s
                            WHERE product_id=%s
                        """, (new_cost, new_sell, new_reorder, active, product["product_id"]))

                        if adj_qty > 0:
                            current_qty = product["quantity"]
                            if adj_type == "Add Stock":
                                new_qty = current_qty + adj_qty
                            elif adj_type == "Remove Stock":
                                new_qty = max(0, current_qty - adj_qty)
                            else:
                                new_qty = adj_qty
                            cursor.execute(
                                "UPDATE inventory SET quantity=%s WHERE product_id=%s",
                                (new_qty, product["product_id"])
                            )
                            log_activity(
                                user["user_id"], "STOCK ADJUSTMENT",
                                f"{selected}: {adj_type} {adj_qty} | Reason: {adj_reason or 'N/A'}"
                            )

                        conn.commit()
                        conn.close()
                        log_activity(user["user_id"], "EDIT PRODUCT", f"Updated {selected}")
                        st.success(f"{selected} updated successfully.")
                        st.rerun()

                with col_btn2:
                    if product["is_active"]:
                        if st.button("🚫 Deactivate Product", type="secondary"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE products SET is_active=FALSE WHERE product_id=%s",
                                (product["product_id"],)
                            )
                            conn.commit()
                            conn.close()
                            log_activity(user["user_id"], "DEACTIVATE PRODUCT", f"Deactivated {selected}")
                            st.success(f"{selected} has been deactivated.")
                            st.rerun()
                    else:
                        if st.button("✅ Reactivate Product", type="secondary"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE products SET is_active=TRUE WHERE product_id=%s",
                                (product["product_id"],)
                            )
                            conn.commit()
                            conn.close()
                            log_activity(user["user_id"], "REACTIVATE PRODUCT", f"Reactivated {selected}")
                            st.success(f"{selected} has been reactivated.")
                            st.rerun()

    elif menu == "Staff Management":
        tab1, tab2 = st.tabs(["Add Staff", "Manage Staff"])
        with tab1:
            st.subheader("Add New Staff Member")
            full_name = st.text_input("Full Name")
            new_pin = st.text_input("Set PIN (4-6 digits)", max_chars=6)
            role = st.selectbox("Role", ["cashier", "manager"])
            if st.button("Add Staff"):
                if full_name and new_pin:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO users (full_name, pin, role) VALUES (%s, %s, %s)",
                        (full_name, new_pin, role)
                    )
                    conn.commit()
                    conn.close()
                    log_activity(user['user_id'], "ADD STAFF", f"Added {full_name} as {role}")
                    st.success(f"{full_name} added successfully as {role}.")
                    st.rerun()
                else:
                    st.warning("Please enter a name and PIN.")
        with tab2:
            st.subheader("All Staff")
            staff = get_all_staff()
            df = pd.DataFrame(staff)[['user_id', 'full_name','role', 'is_active', 'created_at']]
            st.dataframe(df, use_container_width=True)
            st.divider()
            st.subheader("Update Staff")
            staff_names = [f"{s['full_name']} ({s['role']})" for s in staff]
            selected = st.selectbox("Select Staff Member", staff_names)
            selected_staff = staff[staff_names.index(selected)]
            new_pin = st.text_input("Reset PIN", value="", max_chars=6, placeholder="Leave blank to keep current PIN")
            active = st.checkbox("Active", value=bool(selected_staff['is_active']))
            if st.button("Update Staff"):
                conn = get_connection()
                cursor = conn.cursor()
                if new_pin:
                    cursor.execute(
                        "UPDATE users SET pin=%s, is_active=%s WHERE user_id=%s",
                        (new_pin, active, selected_staff['user_id'])
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET is_active=%s WHERE user_id=%s",
                        (active, selected_staff['user_id'])
                    )
                conn.commit()
                conn.close()
                log_activity(user['user_id'], "UPDATE STAFF", f"Updated {selected_staff['full_name']}")
                st.success(f"{selected_staff['full_name']} updated successfully.")
                st.rerun()

    elif menu == "Expense Tracking":
        st.subheader("Record New Expense")
        col1, col2 = st.columns(2)
        with col1:
            exp_date = st.date_input("Date")
            category = st.selectbox("Category", ["Rent", "Electricity", "Water", "Salaries", "Supplies", "Transport", "Other"])
        with col2:
            description = st.text_input("Description")
            amount = st.number_input("Amount (GHS)", min_value=0.0, format="%.2f")
        if st.button("Record Expense"):
            if amount > 0:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expenses (expense_date, category, description, amount, recorded_by)
                    VALUES (%s, %s, %s, %s, %s)
                """, (exp_date, category, description, amount, user['user_id']))
                conn.commit()
                conn.close()
                log_activity(user['user_id'], "EXPENSE", f"{category} - GHS {amount}")
                st.success("Expense recorded successfully.")
                st.rerun()
            else:
                st.warning("Please enter an amount.")
        st.divider()
        st.subheader("All Expenses")
        expenses = get_expenses_data()
        exp_df = pd.DataFrame(expenses)
        st.dataframe(exp_df, use_container_width=True)
        if not exp_df.empty:
            st.metric("Total Expenses", f"GHS {exp_df['amount'].sum():,.2f}")
            st.divider()
            st.subheader("📊 Expenses by Category")
            cat_summary = exp_df.groupby('category')['amount'].sum().reset_index()
            cat_summary.columns = ['Category', 'Amount (GHS)']
            cat_summary = cat_summary.sort_values('Amount (GHS)', ascending=False)
            st.dataframe(cat_summary, use_container_width=True)
            st.bar_chart(cat_summary.set_index('Category')['Amount (GHS)'])

    elif menu == "Profit & Loss":
        sales = get_sales_data()
        sales_df = pd.DataFrame(sales)
        active_sales = sales_df[sales_df['is_voided'] == 0]
        total_revenue = active_sales['total_amount'].sum()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT SUM(si.quantity * p.cost_price) AS total_cogs
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.is_voided = FALSE
        """)
        cogs_result = cursor.fetchone()
        conn.close()
        total_cogs = cogs_result['total_cogs'] or 0

        expenses = get_expenses_data()
        exp_df = pd.DataFrame(expenses)
        total_expenses = exp_df['amount'].sum() if not exp_df.empty else 0

        gross_profit = total_revenue - total_cogs
        net_profit = gross_profit - total_expenses

        col1, col2 = st.columns(2)
        col1.metric("Total Revenue", f"GHS {total_revenue:,.2f}")
        col2.metric("Cost of Goods Sold", f"GHS {total_cogs:,.2f}")

        col3, col4 = st.columns(2)
        col3.metric("Gross Profit", f"GHS {gross_profit:,.2f}")
        col4.metric("Total Expenses", f"GHS {total_expenses:,.2f}")

        st.divider()
        st.metric("Net Profit", f"GHS {net_profit:,.2f}")

    elif menu == "Reports":
        st.subheader("Export Reports")
        sales = get_sales_data()
        sales_df = pd.DataFrame(sales)
        st.write("Sales Report")
        st.dataframe(sales_df, use_container_width=True)

        csv = sales_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Sales Report (CSV)", csv, "sales_report.csv", "text/csv")

        inventory = get_inventory_data()
        inv_df = pd.DataFrame(inventory)
        st.write("Inventory Report")
        st.dataframe(inv_df, use_container_width=True)

        csv2 = inv_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Inventory Report (CSV)", csv2, "inventory_report.csv", "text/csv")

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