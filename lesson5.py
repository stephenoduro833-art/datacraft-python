import csv

businesses = [
    {"name": "Datacraft", "revenue": 5000, "expenses": 3200},
    {"name": "Lunava", "revenue": 8000, "expenses": 5500},
    {"name": "TechHub", "revenue": 12000, "expenses": 7500}
]

with open("business_report.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Business", "Revenue", "Expenses", "Profit", "Margin %"])
    
    for b in businesses:
        profit = b["revenue"] - b["expenses"]
        margin = round((profit / b["revenue"]) * 100, 2)
        writer.writerow([b["name"], b["revenue"], b["expenses"], profit, margin])

print("Report generated")