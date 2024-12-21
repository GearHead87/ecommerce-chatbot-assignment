from init_db_schema import init_db_schema
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from queue import Queue
from threading import Lock
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# Set up logging
logging.basicConfig(filename='chatbot.log', level=logging.INFO)

# Connection pool configuration
POOL_SIZE = 5
connection_pool = Queue(maxsize=POOL_SIZE)
pool_lock = Lock()

def init_connection_pool():
    """Initialize the connection pool with multiple database connections"""
    for _ in range(POOL_SIZE):
        conn = sqlite3.connect('ecommerce.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        connection_pool.put(conn)

@contextmanager
def get_db_connection():
    """Context manager for handling database connections from the pool"""
    connection = None
    try:
        connection = connection_pool.get()
        yield connection
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection_pool.put(connection)

def execute_db_operation(operation, params=None, fetchall=False, fetchone=False):
    """Execute a database operation with proper connection handling"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(operation, params)
        else:
            cursor.execute(operation)
            
        if fetchall:
            return cursor.fetchall()
        elif fetchone:
            return cursor.fetchone()
        return cursor

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400
    
    try:
        # Check if username exists
        existing_user = execute_db_operation(
            "SELECT * FROM users WHERE username = ?", 
            (username,), 
            fetchone=True
        )
        
        if existing_user:
            return jsonify({"success": False, "message": "Username already exists"}), 400
        
        # Insert new user
        hashed_password = generate_password_hash(password)
        execute_db_operation(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        
        logging.info(f"New user registered: {username}")
        return jsonify({"success": True, "message": "User registered successfully"}), 201
        
    except Exception as e:
        logging.error(f"Error during registration: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during registration"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        user = execute_db_operation(
            "SELECT * FROM users WHERE username = ?",
            (username,),
            fetchone=True
        )
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            logging.info(f"User logged in: {username}")
            return jsonify({"success": True, "message": "Logged in successfully"})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
            
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during login"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    username = session.get('username')
    session.clear()
    logging.info(f"User logged out: {username}")
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/search', methods=['GET'])
def search_products():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', 0)
    max_price = request.args.get('max_price', float('inf'))
    
    try:
        sql = """
        SELECT * FROM products 
        WHERE (name LIKE ? OR description LIKE ?) 
        AND (? = '' OR category = ?)
        AND price >= ? AND price <= ?
        """
        products = execute_db_operation(
            sql,
            ('%' + query + '%', '%' + query + '%', 
             category, category, 
             min_price, max_price),
            fetchall=True
        )
        
        logging.info(f"Search performed: query='{query}', category='{category}', price range={min_price}-{max_price}")
        return jsonify([dict(product) for product in products])
        
    except Exception as e:
        logging.error(f"Error during product search: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during product search"}), 500

@app.route('/purchase', methods=['POST'])
def purchase():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    
    data = request.json
    product_id = data.get('product_id')
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Check if product exists and is in stock
            cursor.execute("SELECT * FROM products WHERE id = ? AND stock > 0", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                cursor.execute("ROLLBACK")
                return jsonify({"success": False, "message": "Product not available"}), 400
            
            # Update stock with proper locking
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0", (product_id,))
            
            if cursor.rowcount == 0:
                cursor.execute("ROLLBACK")
                return jsonify({"success": False, "message": "Product out of stock"}), 400
            
            # Record purchase
            purchase_time = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO purchases (user_id, product_id, purchase_time) VALUES (?, ?, ?)",
                (session['user_id'], product_id, purchase_time)
            )
            
            # Commit transaction
            cursor.execute("COMMIT")
            
            logging.info(f"Purchase made: user_id={session['user_id']}, product_id={product_id}")
            return jsonify({"success": True, "message": f"Purchase successful for product ID: {product_id}"})
            
    except Exception as e:
        logging.error(f"Error during purchase: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during purchase"}), 500

@app.route('/chat_history', methods=['GET'])
def get_chat_history():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    
    try:
        history = execute_db_operation(
            "SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp",
            (session['user_id'],),
            fetchall=True
        )
        
        return jsonify([dict(message) for message in history])
        
    except Exception as e:
        logging.error(f"Error retrieving chat history: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while retrieving chat history"}), 500

@app.route('/save_chat', methods=['POST'])
def save_chat():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    
    data = request.json
    message = data.get('message')
    sender = data.get('sender')
    
    try:
        execute_db_operation(
            "INSERT INTO chat_history (user_id, message, sender, timestamp) VALUES (?, ?, ?, ?)",
            (session['user_id'], message, sender, datetime.now().isoformat())
        )
        
        return jsonify({"success": True, "message": "Chat message saved successfully"})
        
    except Exception as e:
        logging.error(f"Error saving chat message: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while saving the chat message"}), 500

# Add this to your main application right before the init_connection_pool() call:
# if __name__ == '__main__':
#     init_db_schema()  # Initialize schema first
#     init_connection_pool()  # Then initialize connection pool
#     app.run(debug=True)


# Initialize the connection pool when the application starts
init_connection_pool()

if __name__ == '__main__':
    app.run(debug=True)