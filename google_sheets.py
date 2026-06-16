import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

spreadsheet = client.open("Datacraft Test")
sales_sheet = spreadsheet.sheet1
summary_sheet = spreadsheet.worksheet("Summary")

all_data = sales_sheet.get_all_records()
df = pd.DataFrame(all_data)

df["Total"] = df["Quantity"] * df["Price"]

total_revenue = float(df["Total"].sum())
best_seller = str(df.groupby("Product")["Quantity"].sum().idxmax())
total_transactions = int(len(df))

summary_sheet.clear()

rows = [
    ["Metric", "Value"],
    ["Total Revenue", total_revenue],
    ["Best Selling Product", best_seller],
    ["Total Transactions", total_transactions]
]

summary_sheet.update("A1", rows)

print("Summary written to Google Sheets")