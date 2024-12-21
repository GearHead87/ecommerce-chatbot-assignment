import sqlite3
import random
from werkzeug.security import generate_password_hash

# Mock data
categories = ['Electronics', 'Books', 'Clothing', 'Home & Garden', 'Toys']
product_names = ['Smartphone', 'Laptop', 'Headphones', 'Novel', 'T-shirt', 'Jeans', 'Sofa', 'Lamp', 'Action Figure', 'Board Game']
descriptions = ['High-quality product', 'Best-seller', 'Great value for money', 'Customer favorite', 'New arrival']

def create_tables():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        purchase_time TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        sender TEXT,
        timestamp TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()

def populate_mock_data():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # Add a test user
    hashed_password = generate_password_hash('password123')
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', hashed_password))

    # Add 100 mock products
    for _ in range(100):
        name = random.choice(product_names)
        category = random.choice(categories)
        price = round(random.uniform(10, 1000), 2)
        description = random.choice(descriptions)
        stock = random.randint(0, 100)

        cursor.execute('''
        INSERT INTO products (name, category, price, description, stock)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, category, price, description, stock))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    populate_mock_data()
    print("Database setup complete with mock data.")

