# routes.py
from flask import Blueprint, request, jsonify
from database import db_session, Product, User
from sqlalchemy import text # Import text for raw SQL sorting if needed
import math

# Create blueprints for product and authentication routes
products_bp = Blueprint('products', __name__)
auth_bp = Blueprint('auth', __name__)

# --- Product Routes ---
@products_bp.route('/products', methods=['GET'])
def get_products():
    """
    API endpoint to retrieve product listings.
    Supports filtering by category, sorting, and pagination.
    """
    # Get query parameters for filtering, sorting, and pagination
    category_filter = request.args.get('category', 'all').lower()
    sort_by = request.args.get('sort', 'popular').lower()
    limit = int(request.args.get('limit', 8)) # Number of products per page
    offset = int(request.args.get('offset', 0)) # Starting index for pagination

    # Start with all products
    query = Product.query

    # Apply category filter if not 'all'
    if category_filter != 'all':
        query = query.filter(Product.category == category_filter)

    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(Product.id.desc()) # Assuming higher ID means newer for mock data
    elif sort_by == 'price-low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price-high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'popular':
        query = query.order_by(Product.reviews.desc(), Product.rating.desc()) # Sort by reviews then rating for 'popular'
    # Default sorting is by 'popular' if no match or 'popular' is explicitly chosen

    # Get total count before applying limit and offset for pagination metadata
    total_products = query.count()

    # Apply pagination
    products = query.offset(offset).limit(limit).all()

    # Serialize products for JSON response
    serialized_products = [product.serialize() for product in products]

    return jsonify({
        'products': serialized_products,
        'total': total_products,
        'limit': limit,
        'offset': offset
    })

# --- Authentication Routes ---
@auth_bp.route('/auth', methods=['POST'])
def auth():
    """
    API endpoint for user login and registration.
    Uses 'action' query parameter to determine the operation.
    """
    action = request.args.get('action')
    data = request.get_json()

    if not data:
        return jsonify({'message': 'Invalid JSON data.'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400

    if action == 'login':
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # In a real application, you would generate and return a JWT token here
            # For this demo, we'll just send a success message.
            return jsonify({'message': 'Login successful!', 'user': {'email': user.email, 'name': user.name}}), 200
        else:
            return jsonify({'message': 'Invalid email or password.'}), 401

    elif action == 'register':
        name = data.get('name')
        if not name:
            return jsonify({'message': 'Name is required for registration.'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'User with this email already exists.'}), 409 # Conflict status code
        else:
            new_user = User(name=name, email=email, password=password)
            db_session.add(new_user)
            db_session.commit()
            return jsonify({'message': 'Registration successful! Please login.'}), 201 # Created status code

    else:
        return jsonify({'message': 'Invalid authentication action.'}), 400

