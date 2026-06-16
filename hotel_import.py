import pandas as pd
import mysql.connector
from datetime import datetime, date

# ── Configuration ──────────────────────────────────────────────
EXCEL_FILE = r"C:\Users\user\Desktop\Excel Projects\Hotel_Data.xlsx"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "datacraft",  # Replace with your MySQL password if you have one
    "database": "hotel_practice"
}

# ── Connect to MySQL ───────────────────────────────────────────
print("Connecting to MySQL...")
conn = mysql.connector.connect(
    host=DB_CONFIG["host"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"]
)
cursor = conn.cursor()

# ── Create Database ────────────────────────────────────────────
print("Creating database...")
cursor.execute("CREATE DATABASE IF NOT EXISTS hotel_practice")
cursor.execute("USE hotel_practice")

# ── Create Tables ──────────────────────────────────────────────
print("Creating tables...")

cursor.execute("DROP TABLE IF EXISTS expenses")
cursor.execute("DROP TABLE IF EXISTS restaurant_revenue")
cursor.execute("DROP TABLE IF EXISTS bookings")
cursor.execute("DROP TABLE IF EXISTS staff")
cursor.execute("DROP TABLE IF EXISTS rooms")

cursor.execute("""
CREATE TABLE rooms (
    room_number VARCHAR(10) PRIMARY KEY,
    room_type VARCHAR(50),
    floor INT,
    capacity INT,
    price_per_night DECIMAL(10,2),
    status VARCHAR(20),
    amenities TEXT
)
""")

cursor.execute("""
CREATE TABLE bookings (
    booking_id VARCHAR(20) PRIMARY KEY,
    guest_name VARCHAR(100),
    nationality VARCHAR(50),
    room_number VARCHAR(10),
    room_type VARCHAR(50),
    check_in DATE,
    check_out DATE,
    nights INT,
    price_per_night DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    booking_source VARCHAR(50),
    payment_method VARCHAR(50),
    status VARCHAR(20)
)
""")

cursor.execute("""
CREATE TABLE restaurant_revenue (
    revenue_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    meal_type VARCHAR(20),
    covers INT,
    revenue DECIMAL(10,2)
)
""")

cursor.execute("""
CREATE TABLE staff (
    staff_id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100),
    role VARCHAR(50),
    department VARCHAR(50),
    salary DECIMAL(10,2),
    status VARCHAR(20)
)
""")

cursor.execute("""
CREATE TABLE expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    month VARCHAR(30),
    category VARCHAR(50),
    description VARCHAR(200),
    amount DECIMAL(10,2)
)
""")

# ── Helper: Convert Excel serial date to Python date ──────────
def excel_date(serial):
    try:
        if isinstance(serial, (int, float)):
            return datetime.fromordinal(datetime(1899, 12, 30).toordinal() + int(serial)).date()
        elif isinstance(serial, (datetime, date)):
            return serial if isinstance(serial, date) else serial.date()
        else:
            return None
    except:
        return None

# ── Load and Insert Rooms ──────────────────────────────────────
print("Loading Rooms...")
df_rooms = pd.read_excel(EXCEL_FILE, sheet_name="Rooms")
df_rooms.columns = ["room_number", "room_type", "floor", "capacity", "price_per_night", "status", "amenities"]

for _, row in df_rooms.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO rooms VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        str(row["room_number"]),
        row["room_type"],
        int(row["floor"]),
        int(row["capacity"]),
        float(row["price_per_night"]),
        row["status"],
        row["amenities"]
    ))

# ── Load and Insert Bookings ───────────────────────────────────
print("Loading Bookings...")
df_bookings = pd.read_excel(EXCEL_FILE, sheet_name="Bookings")
df_bookings.columns = [
    "booking_id", "guest_name", "nationality", "room_number", "room_type",
    "check_in", "check_out", "nights", "price_per_night", "total_amount",
    "booking_source", "payment_method", "status"
]

for _, row in df_bookings.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO bookings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["booking_id"],
        row["guest_name"],
        row["nationality"],
        str(row["room_number"]),
        row["room_type"],
        excel_date(row["check_in"]),
        excel_date(row["check_out"]),
        int(row["nights"]),
        float(row["price_per_night"]),
        float(row["total_amount"]),
        row["booking_source"],
        row["payment_method"],
        row["status"]
    ))

# ── Load and Insert Restaurant Revenue ────────────────────────
print("Loading Restaurant Revenue...")
df_restaurant = pd.read_excel(EXCEL_FILE, sheet_name="Restaurant Revenue")
df_restaurant.columns = ["date", "meal_type", "covers", "revenue"]

for _, row in df_restaurant.iterrows():
    cursor.execute("""
        INSERT INTO restaurant_revenue (date, meal_type, covers, revenue)
        VALUES (%s, %s, %s, %s)
    """, (
        excel_date(row["date"]),
        row["meal_type"],
        int(row["covers"]),
        float(row["revenue"])
    ))

# ── Load and Insert Staff ──────────────────────────────────────
print("Loading Staff...")
df_staff = pd.read_excel(EXCEL_FILE, sheet_name="Staff")
df_staff.columns = ["staff_id", "full_name", "role", "department", "salary", "status"]

for _, row in df_staff.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO staff VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        row["staff_id"],
        row["full_name"],
        row["role"],
        row["department"],
        float(row["salary"]),
        row["status"]
    ))

# ── Load and Insert Expenses ───────────────────────────────────
print("Loading Expenses...")
df_expenses = pd.read_excel(EXCEL_FILE, sheet_name="Expenses")
df_expenses.columns = ["month", "category", "description", "amount"]

for _, row in df_expenses.iterrows():
    cursor.execute("""
        INSERT INTO expenses (month, category, description, amount)
        VALUES (%s, %s, %s, %s)
    """, (
        row["month"],
        row["category"],
        row["description"],
        float(row["amount"])
    ))

# ── Finish ─────────────────────────────────────────────────────
conn.commit()
cursor.close()
conn.close()

print("")
print("Done. All data loaded into hotel_practice database.")
print("Tables created: rooms, bookings, restaurant_revenue, staff, expenses")
