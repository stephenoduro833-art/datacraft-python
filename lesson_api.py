import requests

response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
data = response.json()
rates = data["rates"]

amount_usd = float(input("Enter amount in USD: "))

ghs = round(amount_usd * rates["GHS"], 2)
gbp = round(amount_usd * rates["GBP"], 2)
eur = round(amount_usd * rates["EUR"], 2)

print(f"\n${amount_usd} USD =")
print(f"  GHS {ghs}")
print(f"  GBP {gbp}")
print(f"  EUR {eur}")