# E-commerce Sales Chatbot

## Overview
An interactive sales chatbot for an e-commerce platform, designed to enhance the shopping experience by enabling efficient search, exploration, and purchase processes.

---

## Features
### Backend Features:
- **User Authentication**: 
  - Secure registration and login system using hashed passwords.
  - Token-based authentication for secure user session management.
- **Product Search**:
  - Advanced filtering capabilities (category, price range, keywords).
  - Supports partial and fuzzy search queries.
- **Purchases**:
  - Stock validation and transactional integrity for product purchases.
  - Purchase history tracking.
- **Chat Management**:
  - Save and retrieve user chat history.
  - Timestamped messages for better context.
- **Error Handling**: 
  - Centralized error management for smoother operations.

### Frontend Features:
- **User Interface**:
  - Interactive product catalog with advanced search and filtering options.
  - Intuitive chatbot interface for enhanced user experience.
- **Authentication**:
  - Seamless login and registration forms integrated with the backend.
- **Responsive Design**:
  - Fully responsive layout optimized for various devices.
- **Purchase Flow**:
  - Simplified and secure purchase process.

---

## Tech Stack
### Backend:
- **Flask**: For RESTful API development.
- **SQLite**: Lightweight RDBMS for storing user data, products, and chat history.
- **JWT**: For secure token-based authentication.
- **Flask-CORS**: To enable cross-origin resource sharing.

### Frontend:
- **Next.js**: For server-side rendering and dynamic frontend.
- **React.js**: For building interactive user interfaces.
- **Tailwind CSS**: For styling and responsive design.

---

## Database Schema
### Tables:
1. **users**:
   - `id` (INTEGER, PRIMARY KEY)
   - `username` (TEXT, UNIQUE)
   - `password` (TEXT, hashed)
2. **products**:
   - `id` (INTEGER, PRIMARY KEY)
   - `name` (TEXT)
   - `description` (TEXT)
   - `category` (TEXT)
   - `price` (REAL)
   - `stock` (INTEGER)
3. **purchases**:
   - `id` (INTEGER, PRIMARY KEY)
   - `user_id` (INTEGER, FOREIGN KEY)
   - `product_id` (INTEGER, FOREIGN KEY)
   - `purchase_time` (TIMESTAMP)
4. **chat_history**:
   - `id` (INTEGER, PRIMARY KEY)
   - `user_id` (INTEGER, FOREIGN KEY)
   - `message` (TEXT)
   - `sender` (TEXT)
   - `timestamp` (TIMESTAMP)

---

## Installation
### Prerequisites:
1. Node.js 16+
2. Python 3.8+
3. `pip` (Python package installer)
4. SQLite3

### Steps:
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Set up the backend:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python init_db.py
   ```
   Create a `.env` file in the `backend` directory:
   ```env
   SECRET_KEY=your_secret_key_here
   ```
   Start the backend server:
   ```bash
   python app.py
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```
      Create a `.env` file in the `fontend` directory:
   ```env
   NEXT_PUBLIC_BACKEND_API=your_backend_url
   ```
   Start the frontend server:
   ```bash
   npm run dev
   ```

---

## API Endpoints
### Authentication
- **POST /register**: Register a new user.
- **POST /login**: Login and obtain a JWT token.

### Product Management
- **GET /search**: Search for products with optional filters (requires authentication).
- **POST /purchase**: Purchase a product by providing its ID (requires authentication).

### Chat Management
- **POST /save_chat**: Save a chat message (requires authentication).
- **GET /chat_history**: Retrieve chat history (requires authentication).

### Error Handling
- Centralized error handler for all routes.

---

## Project Structure
```
|-- backend/
|   |-- app.py                # Main backend application file
|   |-- init_db.py            # Script to initialize the database schema
|   |-- requirements.txt      # Python dependencies
|   |-- .env                  # Environment variables
|   |-- ecommerce.db          # SQLite database file
|   |-- app.log               # Log file
|-- frontend/
|   |-- app/                  # Next.js pages
|   |-- components/           # React components
|   |-- styles/               # Tailwind CSS styles
|   |-- public/               # Static assets
|   |-- package.json          # Frontend dependencies
|-- README.md                 # Project documentation
```

---

## Challenges & Solutions
### Challenges:
1. Ensuring transactional integrity during purchases.
2. Handling large chat histories efficiently.
3. Implementing a secure authentication mechanism.

### Solutions:
1. Used SQL transactions with rollback mechanisms for safe stock updates.
2. Optimized database queries and indexing for chat history retrieval.
3. Utilized JWTs with secure key management.

---

## Future Enhancements
1. Implement real-time chat using WebSocket.
2. Add support for multiple payment gateways.
3. Enhance product search with AI-based recommendations.

---

## Contributors
- [Hosan Ul Islam]()

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.
