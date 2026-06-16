try:
    revenue = int(input("Enter revenue: "))
    expenses = int(input("Enter expenses: "))
    profit = revenue / (revenue - expenses)
    print(f"Result: {profit}")
except ValueError:
    print("Invalid input. Please enter numbers only.")
except ZeroDivisionError:
    print("Error. Revenue and expenses cannot be equal.")
try:
    revenue = int(input("Enter revenue: "))
    print(f"Revenue: {revenue}")
except ValueError:
    print("Invalid input. Please enter a number.")
finally:
    print("Program finished.")