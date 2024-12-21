import sqlite3

# Initialize the database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Create the products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    stock INTEGER NOT NULL
)
''')

# Sample product data
products = [
    ('Smartphone X', 'Electronics', 699.99, 'High-end smartphone with advanced features', 50),
    ('Laptop Pro', 'Electronics', 1299.99, 'Powerful laptop for professionals', 30),
    ('Wireless Earbuds', 'Electronics', 129.99, 'True wireless earbuds with noise cancellation', 100),
    ('Smart Watch', 'Electronics', 249.99, 'Fitness tracker and smartwatch', 75),
    ('4K TV', 'Electronics', 799.99, '55-inch 4K Smart TV', 25),
    # Add more products here to reach at least 100 entries
]

# Insert the products
cursor.executemany('INSERT INTO products (name, category, price, description, stock) VALUES (?, ?, ?, ?, ?)', products)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database initialized with sample products.")