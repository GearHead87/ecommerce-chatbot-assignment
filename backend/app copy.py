from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
from queue import Queue
from threading import Lock

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configure CORS - Fixed to handle credentials properly
CORS(app, 
     supports_credentials=True,
     resources={
         r"/*": {
             "origins": ["http://localhost:3000"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Set-Cookie"],
         }
     })

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_PATH='/'
)

# Logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
DATABASE_PATH = 'ecommerce.db'
POOL_SIZE = 5
connection_pool = Queue(maxsize=POOL_SIZE)
pool_lock = Lock()

# Connection Pool Management
def init_connection_pool():
    """Initialize the connection pool"""
    for _ in range(POOL_SIZE):
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        connection_pool.put(conn)

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
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
    """Execute database operations with connection handling"""
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

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# CORS headers middleware
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', 'http://localhost:3000')
    response.headers.update({
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    })
    return response

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        # Check existing user
        existing_user = execute_db_operation(
            "SELECT 1 FROM users WHERE username = ?",
            (data['username'],),
            fetchone=True
        )
        
        if existing_user:
            return jsonify({"success": False, "message": "Username already exists"}), 400
        
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        execute_db_operation(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (data['username'], hashed_password)
        )
        
        return jsonify({"success": True, "message": "User registered successfully"}), 201
        
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return jsonify({"success": False, "message": "Registration failed"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        user = execute_db_operation(
            "SELECT * FROM users WHERE username = ?",
            (data['username'],),
            fetchone=True
        )
        
        if user and check_password_hash(user['password'], data['password']):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            
            return jsonify({
                "success": True,
                "message": "Logged in successfully",
                "user": user['username']
            }), 200
        
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "message": "Login failed"}), 500

@app.route('/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            "success": True,
            "authenticated": True,
            "username": session.get('username')
        })
    return jsonify({
        "success": True,
        "authenticated": False
    })

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/search', methods=['GET'])
@login_required
def search_products():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', float('inf')))
    
    try:
        sql = """
        SELECT * FROM products 
        WHERE (name LIKE ? OR description LIKE ?) 
        AND (? = '' OR category = ?)
        AND price >= ? AND price <= ?
        """
        products = execute_db_operation(
            sql,
            (f'%{query}%', f'%{query}%', category, category, min_price, max_price),
            fetchall=True
        )
        
        return jsonify([dict(row) for row in products])
        
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({"success": False, "message": "Search failed"}), 500

@app.route('/purchase', methods=['POST'])
@login_required
def purchase():
    data = request.get_json()
    if not data or 'product_id' not in data:
        return jsonify({"success": False, "message": "Missing product ID"}), 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            
            # Check product availability
            cursor.execute(
                "SELECT * FROM products WHERE id = ? AND stock > 0",
                (data['product_id'],)
            )
            product = cursor.fetchone()
            
            if not product:
                cursor.execute("ROLLBACK")
                return jsonify({"success": False, "message": "Product not available"}), 400
            
            # Update stock
            cursor.execute(
                "UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0",
                (data['product_id'],)
            )
            
            if cursor.rowcount == 0:
                cursor.execute("ROLLBACK")
                return jsonify({"success": False, "message": "Product out of stock"}), 400
            
            # Record purchase
            cursor.execute(
                "INSERT INTO purchases (user_id, product_id, purchase_time) VALUES (?, ?, ?)",
                (session['user_id'], data['product_id'], datetime.now().isoformat())
            )
            
            cursor.execute("COMMIT")
            return jsonify({"success": True, "message": "Purchase successful"}), 200
            
    except Exception as e:
        logging.error(f"Purchase error: {str(e)}")
        return jsonify({"success": False, "message": "Purchase failed"}), 500

@app.route('/chat_history', methods=['GET'])
@login_required
def get_chat_history():
    try:
        history = execute_db_operation(
            "SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp",
            (session['user_id'],),
            fetchall=True
        )
        return jsonify([dict(msg) for msg in history])
    except Exception as e:
        logging.error(f"Chat history error: {str(e)}")
        return jsonify({"success": False, "message": "Failed to retrieve chat history"}), 500

@app.route('/save_chat', methods=['POST'])
@login_required
def save_chat():
    data = request.get_json()
    if not data or 'message' not in data or 'sender' not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        execute_db_operation(
            "INSERT INTO chat_history (user_id, message, sender, timestamp) VALUES (?, ?, ?, ?)",
            (session['user_id'], data['message'], data['sender'], datetime.now().isoformat())
        )
        return jsonify({"success": True, "message": "Chat message saved successfully"})
    except Exception as e:
        logging.error(f"Save chat error: {str(e)}")
        return jsonify({"success": False, "message": "Failed to save chat message"}), 500

@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Unhandled error: {str(error)}")
    return jsonify({"success": False, "message": "An unexpected error occurred"}), 500

# Initialize application
init_connection_pool()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)