import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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