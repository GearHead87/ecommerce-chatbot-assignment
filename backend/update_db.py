import sqlite3

def update_database():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    try:
        # First, create a backup of existing purchases table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases_backup AS 
        SELECT id, user_id, product_id, purchase_date 
        FROM purchases
        ''')

        # Drop the original purchases table
        cursor.execute('DROP TABLE IF EXISTS purchases')

        # Create new purchases table with purchase_time
        cursor.execute('''
        CREATE TABLE purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            purchase_time DATETIME NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')

        # Restore data from backup, using purchase_date as purchase_time
        cursor.execute('''
        INSERT INTO purchases (id, user_id, product_id, purchase_time, purchase_date)
        SELECT id, user_id, product_id, purchase_date, purchase_date
        FROM purchases_backup
        ''')

        # Drop the backup table
        cursor.execute('DROP TABLE IF EXISTS purchases_backup')

        # Create other tables if they don't exist
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
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            category TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            sender TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

        conn.commit()
        print("Database schema updated successfully.")

    except Exception as e:
        print(f"Error updating database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_database()