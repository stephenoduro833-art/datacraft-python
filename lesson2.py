business=input("Business name:" )
revenue=int(input("enter revenue: "))
expenses=int(input("enter expenses: "))
profit = revenue-expenses

if profit > 0:
    print(f"{business} made a profit of {profit} ")
elif profit ==0:
    print(f"{business} broke even ")
else:
    print(f"{business} made a loss {profit}")
profit_margin = profit/revenue * 100
print (f"profit_margin)  is {profit_margin}%")