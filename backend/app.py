# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, db_session
from routes import products_bp, auth_bp
import os

# Initialize Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for your frontend
# This is crucial because your frontend (HTML file) will be served from a different origin
# (e.g., your local file system or a different web server) than your backend.
CORS(app)

# Define the path for the SQLite database file
# It will be created in the root directory of your backend project.
app.config['DATABASE'] = os.path.join(app.root_path, 'snapvolt.db')

# Initialize the database when the application starts
# This will create the tables and populate them with initial product data.
with app.app_context():
    init_db()

# Register blueprints for different API routes
# Blueprints help organize your routes into modular components.
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')

# Teardown the database session when the application context ends
# This ensures database connections are properly closed.
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Root endpoint for testing if the server is running
@app.route('/')
def index():
    return "SnapVolt Backend is running!"

if __name__ == '__main__':
    # Run the Flask application
    # debug=True allows for automatic code reloading and a debugger in the browser.
    # It should be False in production.
    app.run(debug=True, port=5000)
