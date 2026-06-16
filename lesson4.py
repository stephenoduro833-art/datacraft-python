businesses = {
    "Datacraft": {
        "revenue": 5000,
        "expenses": 3200
    },
    "Lunava": {
        "revenue": 8000,
        "expenses": 5500
    },
    "TechHub": {
        "revenue": 12000,
        "expenses": 7500
    }
}

for name, details in businesses.items():
    profit = details["revenue"] - details["expenses"]
    profit_margin = (profit / details["revenue"]) * 100

    print(f"\nBusiness: {name}")
    print(f"Profit: {profit}")
    print(f"Profit Margin: {profit_margin:.2f}%")