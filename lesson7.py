import math

print(math.sqrt(144))
print(math.pi)
print(math.ceil(4.3))
print(math.floor(4.9))

from datetime import date, datetime

print(date.today())
print(datetime.now())

import random
print(random.randint(1, 100))
print(random.choice(["Datacraft", "Lunava", "TechHub"]))

import pandas as pd


data = {
    "Business": ["Datacraft", "Lunava", "TechHub"],
    "Revenue": [5000, 8000, 12000],
    "Expenses": [3200, 5500, 7500]
}

df = pd.DataFrame(data)
print(df)
df["Profit"] = df["Revenue"] - df["Expenses"]
df["Margin %"] = round((df["Profit"] / df["Revenue"]) * 100, 2)
print(df)
df.to_excel("business_report.xlsx", index=False)
print("Excel file created")
df2 = pd.read_excel("business_report.xlsx")
print(df2)