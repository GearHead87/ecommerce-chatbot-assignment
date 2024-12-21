from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from functools import wraps
from contextlib import contextmanager
from queue import Queue
from jwt import (JWT,jwk_from_dict)
from jwt.utils import get_int_from_datetime


from dotenv import load_dotenv
load_dotenv()


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

instance = JWT()

# CORS configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
         }
     })

# Logging configuration
logging.basicConfig(
    filename='app.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database connection pool
DATABASE_PATH = 'ecommerce.db'
POOL_SIZE = 5
connection_pool = Queue(maxsize=POOL_SIZE)

def init_connection_pool():
    for _ in range(POOL_SIZE):
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        connection_pool.put(conn)

@contextmanager
def get_db_connection():
    """Provides a database connection from the pool."""
    conn = connection_pool.get()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        connection_pool.put(conn)

def execute_query(query, params=None, fetchall=False, fetchone=False):
    """Executes a database query with optional fetch."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        if fetchall:
            return cursor.fetchall()
        if fetchone:
            return cursor.fetchone()

# Token-based authentication
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        signing_key = jwk_from_dict({'kty': 'oct', 'k': app.config['SECRET_KEY']})
        if not token:
            return jsonify({"success": False, "message": "Token is missing"}), 401
        try:
            decoded = instance.decode(token, signing_key, algorithms=["HS256"])
            request.user_id = decoded['user_id']
        except instance.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except instance.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorator

# Generate JWT token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': get_int_from_datetime(datetime.now(timezone.utc) + timedelta(days=7))
    }
    # print(payload)
    signing_key = jwk_from_dict({'kty': 'oct', 'k': app.config['SECRET_KEY']})
    # print(signing_key)
    return instance.encode(payload, signing_key, alg="HS256")

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        if execute_query("SELECT 1 FROM users WHERE username = ?", (username,), fetchone=True):
            return jsonify({"success": False, "message": "Username already exists"}), 400
        
        hashed_password = generate_password_hash(password)
        execute_query("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        return jsonify({"success": True, "message": "User registered successfully"}), 201
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return jsonify({"success": False, "message": "Registration failed"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        user = execute_query("SELECT * FROM users WHERE username = ?", (username,), fetchone=True)
        if user and check_password_hash(user['password'], password):
            token = generate_token(user['id'])
            return jsonify({"success": True, "token": token, "user": user['username']}), 200
        
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "message": "Login failed"}), 500

@app.route('/search', methods=['GET'])
@token_required
def search_products():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', float('inf')))
    
    try:
        sql = """
        SELECT * FROM products WHERE 
        (name LIKE ? OR description LIKE ?) AND 
        (? = '' OR category = ?) AND 
        price BETWEEN ? AND ?
        """
        products = execute_query(sql, (f'%{query}%', f'%{query}%', category, category, min_price, max_price), fetchall=True)
        return jsonify([dict(row) for row in products])
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({"success": False, "message": "Search failed"}), 500

@app.route('/purchase', methods=['POST'])
@token_required
def purchase():
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"success": False, "message": "Missing product ID"}), 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            
            # Check stock
            product = cursor.execute("SELECT * FROM products WHERE id = ? AND stock > 0", (product_id,)).fetchone()
            if not product:
                cursor.execute("ROLLBACK")
                return jsonify({"success": False, "message": "Product not available"}), 400
            
            # Update stock and record purchase
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (product_id,))
            cursor.execute("INSERT INTO purchases (user_id, product_id, purchase_time) VALUES (?, ?, ?)",
                           (request.user_id, product_id, datetime.now()))
            
            cursor.execute("COMMIT")
            return jsonify({"success": True, "message": "Purchase successful"}), 200
    except Exception as e:
        logging.error(f"Purchase error: {str(e)}")
        return jsonify({"success": False, "message": "Purchase failed"}), 500

@app.route('/chat_history', methods=['GET'])
@token_required
def get_chat_history():
    try:
        history = execute_query("SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp", 
                                (request.user_id,), fetchall=True)
        return jsonify([dict(row) for row in history])
    except Exception as e:
        logging.error(f"Chat history error: {str(e)}")
        return jsonify({"success": False, "message": "Failed to retrieve chat history"}), 500

@app.route('/save_chat', methods=['POST'])
@token_required
def save_chat():
    data = request.get_json()
    message, sender = data.get('message'), data.get('sender')
    
    if not message or not sender:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        execute_query("INSERT INTO chat_history (user_id, message, sender, timestamp) VALUES (?, ?, ?, ?)",
                      (request.user_id, message, sender, datetime.now()))
        return jsonify({"success": True, "message": "Chat message saved successfully"})
    except Exception as e:
        logging.error(f"Save chat error: {str(e)}")
        return jsonify({"success": False, "message": "Failed to save chat message"}), 500

# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled error: {str(e)}")
    return jsonify({"success": False, "message": "An unexpected error occurred"}), 500

# Initialize app
init_connection_pool()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
