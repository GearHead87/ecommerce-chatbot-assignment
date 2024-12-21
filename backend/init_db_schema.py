import logging
import sqlite3

# from Backend import app
# from Backend.app import init_connection_pool


def init_db_schema():
    """Initialize database schema with all required tables"""
    schema_sql = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );

    -- Products table
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        category TEXT
    );

    -- Purchases table
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        purchase_time DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    -- Chat history table
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        sender TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    
    try:
        # Use a dedicated connection for schema initialization
        conn = sqlite3.connect('ecommerce.db')
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        logging.info("Database schema initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database schema: {str(e)}")
        raise e

