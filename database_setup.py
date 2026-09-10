import sqlite3
import random
from datetime import datetime, timedelta

def create_and_populate_db(db_path="ecommerce_analytics.db"):
    """
    Creates an E-Commerce SQLite database with 10 relational tables
    and populates it with 500+ synthetic records.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables to allow clean re-runs
    tables = [
        "inventory_logs", "reviews", "payments", "order_items", "orders",
        "products", "categories", "customers", "shippers", "suppliers"
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # 1. Categories
    cursor.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL,
        description TEXT
    )
    """)

    # 2. Suppliers
    cursor.execute("""
    CREATE TABLE suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        contact_person TEXT,
        country TEXT
    )
    """)

    # 3. Shippers
    cursor.execute("""
    CREATE TABLE shippers (
        shipper_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipper_name TEXT NOT NULL,
        phone TEXT
    )
    """)

    # 4. Customers
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        city TEXT,
        signup_date DATE
    )
    """)

    # 5. Products
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category_id INTEGER,
        supplier_id INTEGER,
        price REAL NOT NULL,
        stock_quantity INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(category_id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
    )
    """)

    # 6. Orders
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        shipper_id INTEGER,
        order_date DATE,
        total_amount REAL,
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (shipper_id) REFERENCES shippers(shipper_id)
    )
    """)

    # 7. Order Items
    cursor.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # 8. Payments
    cursor.execute("""
    CREATE TABLE payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        payment_method TEXT,
        payment_date DATE,
        amount REAL,
        status TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
    """)

    # 9. Reviews
    cursor.execute("""
    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        rating INTEGER,
        review_date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # 10. Inventory Logs
    cursor.execute("""
    CREATE TABLE inventory_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        change_quantity INTEGER,
        log_date DATE,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    # --- SEED DATA (500+ Records Total) ---

    # Seed Categories
    cats = [
        ("Electronics", "Gadgets, smartphones, and accessories"),
        ("Apparel", "Clothing, footwear, and fashion items"),
        ("Home & Kitchen", "Furniture, cookware, and appliances"),
        ("Books", "Fiction, non-fiction, and textbooks"),
        ("Sports & Outdoors", "Fitness equipment and camping gear")
    ]
    cursor.executemany("INSERT INTO categories (category_name, description) VALUES (?, ?)", cats)

    # Seed Suppliers
    sups = [
        ("TechSupply Inc.", "John Doe", "USA"),
        ("Global Apparel Ltd.", "Jane Smith", "India"),
        ("HomeComfort Co.", "Carlos Ray", "Vietnam"),
        ("PaperBack Pubs", "Emily White", "UK"),
        ("FitGear Global", "Mark Lee", "China")
    ]
    cursor.executemany("INSERT INTO suppliers (supplier_name, contact_person, country) VALUES (?, ?, ?)", sups)

    # Seed Shippers
    ships = [
        ("FedEx Express", "+1-800-555-0199"),
        ("DHL Logistics", "+49-180-6345300"),
        ("BlueDart Express", "+91-22-67980000")
    ]
    cursor.executemany("INSERT INTO shippers (shipper_name, phone) VALUES (?, ?)", ships)

    # Seed Customers (50 records)
    cities = ["Mumbai", "Delhi", "Bengaluru", "Kolkata", "Hyderabad", "Chennai", "Pune", "Ahmedabad"]
    first_names = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Sneha", "Rahul", "Kavya", "Aditya", "Meera"]
    last_names = ["Sharma", "Verma", "Patel", "Rao", "Nair", "Gupta", "Singh", "Reddy", "Joshi", "Kumar"]

    cust_list = []
    base_date = datetime(2024, 1, 1)
    for i in range(1, 51):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        city = random.choice(cities)
        s_date = (base_date + timedelta(days=random.randint(0, 200))).strftime("%Y-%m-%d")
        cust_list.append((name, email, city, s_date))
    cursor.executemany("INSERT INTO customers (name, email, city, signup_date) VALUES (?, ?, ?, ?)", cust_list)

    # Seed Products (25 records)
    prod_names = [
        ("Wireless Headphones", 1, 1, 149.99, 120),
        ("Smartphone Pro", 1, 1, 899.99, 45),
        ("4K Monitor 27-inch", 1, 1, 329.50, 60),
        ("Mechanical Keyboard", 1, 1, 89.00, 150),
        ("Bluetooth Speaker", 1, 1, 49.99, 200),
        ("Men Denim Jacket", 2, 2, 79.99, 80),
        ("Running Shoes", 2, 2, 119.50, 90),
        ("Cotton T-Shirt 3-Pack", 2, 2, 29.99, 300),
        ("Formal Leather Belt", 2, 2, 34.50, 110),
        ("Summer Dress", 2, 2, 59.99, 70),
        ("Ergonomic Office Chair", 3, 3, 249.00, 30),
        ("Stainless Steel Cookware Set", 3, 3, 179.99, 40),
        ("Air Fryer 5L", 3, 3, 99.50, 85),
        ("Memory Foam Mattress", 3, 3, 499.00, 20),
        ("LED Desk Lamp", 3, 3, 25.00, 150),
        ("Data Science & ML Handbook", 4, 4, 45.00, 200),
        ("System Design Interview", 4, 4, 38.50, 180),
        ("Python Crash Course", 4, 4, 29.99, 250),
        ("Financial Intelligence", 4, 4, 24.50, 140),
        ("Clean Code Guide", 4, 4, 42.00, 160),
        ("Yoga Mat Extra Thick", 5, 5, 22.99, 190),
        ("Adjustable Dumbbell Set", 5, 5, 189.99, 35),
        ("Waterproof Camping Tent", 5, 5, 139.50, 50),
        ("Mountain Bike Helmet", 5, 5, 54.99, 75),
        ("Hydration Sports Bottle", 5, 5, 14.99, 400)
    ]
    cursor.executemany("INSERT INTO products (product_name, category_id, supplier_id, price, stock_quantity) VALUES (?, ?, ?, ?, ?)", prod_names)

    # Seed Orders (150 records)
    statuses = ["Completed", "Shipped", "Pending", "Cancelled"]
    orders_list = []
    for i in range(1, 151):
        c_id = random.randint(1, 50)
        s_id = random.randint(1, 3)
        o_date = (datetime(2024, 3, 1) + timedelta(days=random.randint(0, 150))).strftime("%Y-%m-%d")
        tot = round(random.uniform(30.0, 1200.0), 2)
        stat = random.choice(statuses)
        orders_list.append((c_id, s_id, o_date, tot, stat))
    cursor.executemany("INSERT INTO orders (customer_id, shipper_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)", orders_list)

    # Seed Order Items (250 records)
    items_list = []
    for i in range(1, 251):
        o_id = random.randint(1, 150)
        p_id = random.randint(1, 25)
        qty = random.randint(1, 5)
        u_price = round(random.uniform(15.0, 300.0), 2)
        items_list.append((o_id, p_id, qty, u_price))
    cursor.executemany("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)", items_list)

    # Seed Payments (150 records)
    p_methods = ["Credit Card", "UPI", "Net Banking", "Debit Card", "PayPal"]
    p_statuses = ["Success", "Success", "Success", "Failed", "Pending"]
    pay_list = []
    for i in range(1, 151):
        o_id = i
        method = random.choice(p_methods)
        p_date = (datetime(2024, 3, 1) + timedelta(days=random.randint(0, 150))).strftime("%Y-%m-%d")
        amt = round(random.uniform(30.0, 1200.0), 2)
        p_stat = random.choice(p_statuses)
        pay_list.append((o_id, method, p_date, amt, p_stat))
    cursor.executemany("INSERT INTO payments (order_id, payment_method, payment_date, amount, status) VALUES (?, ?, ?, ?, ?)", pay_list)

    # Seed Reviews (80 records)
    rev_list = []
    for i in range(1, 81):
        c_id = random.randint(1, 50)
        p_id = random.randint(1, 25)
        rating = random.randint(1, 5)
        r_date = (datetime(2024, 4, 1) + timedelta(days=random.randint(0, 100))).strftime("%Y-%m-%d")
        rev_list.append((c_id, p_id, rating, r_date))
    cursor.executemany("INSERT INTO reviews (customer_id, product_id, rating, review_date) VALUES (?, ?, ?, ?)", rev_list)

    # Seed Inventory Logs (50 records)
    log_list = []
    for i in range(1, 51):
        p_id = random.randint(1, 25)
        chg = random.choice([-10, -5, 20, 50, -15, 100])
        l_date = (datetime(2024, 2, 1) + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        log_list.append((p_id, chg, l_date))
    cursor.executemany("INSERT INTO inventory_logs (product_id, change_quantity, log_date) VALUES (?, ?, ?)", log_list)

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Database '{db_path}' created with 10 tables and 500+ records!")

if __name__ == "__main__":
    create_and_populate_db()
