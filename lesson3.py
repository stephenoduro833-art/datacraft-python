def calculate_profit(revenue, expenses):
    profit = revenue- expenses
    return profit
result = calculate_profit(5000, 3200)
print(f"profit: {result}")
def calculate_margin(profit, revenue):
    margin = profit / revenue * 100
    return margin 
result = calculate_margin(1800, 5000)
print(f"profit margin: {result}")