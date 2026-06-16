import streamlit as st
import pandas as pd

st.title("Datacraft Business Dashboard")
st.subheader("Sales Analysis Tool")

st.write("Enter your sales data below:")

data = {
    "Product": ["Rice 5kg", "Cooking Oil", "Sugar", "Eggs", "Water"],
    "Quantity": [10, 5, 8, 20, 15],
    "Price": [45, 28, 12, 35, 4]
}

df = pd.DataFrame(data)
df["Total"] = df["Quantity"] * df["Price"]

st.dataframe(df)

st.metric("Total Revenue", f"GHS {df['Total'].sum():,.2f}")
st.metric("Best Seller", df.loc[df['Quantity'].idxmax(), 'Product'])