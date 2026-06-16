import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔒 Datacraft P&L Analyzer")
        password = st.text_input("Enter password to access", type="password")
        if password == "datacraft2026":
            st.session_state.authenticated = True
            st.rerun()
        elif password:
            st.error("Incorrect password")
        st.stop()

check_password()

st.set_page_config(page_title="P&L Analyzer", page_icon="📊", layout="wide")

st.title("📊 Profit & Loss Analyzer")
st.subheader("by Datacraft")
st.divider()

st.sidebar.header("Enter Your Sales Data")

num_products = st.sidebar.number_input("How many products?", min_value=1, max_value=20, value=3)

products = []
for i in range(num_products):
    st.sidebar.divider()
    name = st.sidebar.text_input(f"Product {i+1} name", key=f"name_{i}")
    sell_price = st.sidebar.number_input(f"Selling price (GHS)", min_value=0.0, key=f"sell_{i}")
    cost_price = st.sidebar.number_input(f"Cost price (GHS)", min_value=0.0, key=f"cost_{i}")
    quantity = st.sidebar.number_input(f"Quantity sold", min_value=0, key=f"qty_{i}")
    
    if name:
        products.append({
            "Product": name,
            "Selling Price": sell_price,
            "Cost Price": cost_price,
            "Quantity": quantity,
            "Revenue": sell_price * quantity,
            "Cost": cost_price * quantity,
            "Profit": (sell_price - cost_price) * quantity,
            "Margin %": round(((sell_price - cost_price) / sell_price * 100) if sell_price > 0 else 0, 2)
        })

if products:
    df = pd.DataFrame(products)
    
    st.subheader("📈 Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"GHS {df['Revenue'].sum():,.2f}")
    col2.metric("Total Cost", f"GHS {df['Cost'].sum():,.2f}")
    col3.metric("Total Profit", f"GHS {df['Profit'].sum():,.2f}")
    col4.metric("Best Performer", df.loc[df['Profit'].idxmax(), 'Product'])
    
    st.divider()
    st.subheader("📋 Product Breakdown")
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    st.subheader("📊 Profit by Product")
    fig, ax = plt.subplots()
    ax.bar(df['Product'], df['Profit'], color='#1a1a2e')
    ax.set_xlabel('Product')
    ax.set_ylabel('Profit (GHS)')
    ax.set_title('Profit by Product')
    plt.xticks(rotation=45)
    st.pyplot(fig)

else:
    st.info("Enter your products in the sidebar to get started.")