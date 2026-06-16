def calculate_average(total, count):
    return total / count

business_name = input("Enter business name: ")
sales = []
jan_sales = float(input("Enter January sales: "))
sales.append(jan_sales)
feb_sales = float(input("Enter February sales: "))
sales.append(feb_sales)
mar_sales = float(input("Enter March sales: "))
sales.append(mar_sales)

total_sales = sum(sales)
highest_sales = max(sales)
lowest_sales = min(sales)
average_sales = round(calculate_average(total_sales, len(sales)), 2)

print("\n--- Sales Report ---")
print("Business Name:", business_name)
print("Sales Figures:", sales)
print("Total Sales:", total_sales)
print("Highest Sales:", highest_sales)
print("Lowest Sales:", lowest_sales)
print("Average Sales:", average_sales)

if average_sales > 3000:
    print("Average sales are ABOVE 3000.")
else:
    print("Average sales are BELOW or EQUAL TO 3000.")