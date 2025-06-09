# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

# Define the path to the SQLite database file
# This path needs to match the one set in app.py
database_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'snapvolt.db')
# Create a SQLAlchemy engine for SQLite
# The 'sqlite:///' prefix indicates a SQLite database.
# The `convert_unicode=True` argument helps with character encoding.
engine = create_engine(f'sqlite:///{database_path}', convert_unicode=True)
# Create a scoped session factory.
# Scoped sessions are thread-local, meaning each request gets its own session,
# which is good practice for web applications to avoid concurrency issues.
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
# Declare a base for declarative models.
# All SQLAlchemy models will inherit from this Base.
Base = declarative_base()
Base.query = db_session.query_property()

# Product Model
class Product(Base):
    """
    SQLAlchemy model for a product in the database.
    Represents the 'products' table.
    """
    __tablename__ = 'products'
    id = Column(String, primary_key=True) # Using String for 'id' to match frontend's 'p1', 'p2' format
    name = Column(String(120), unique=True, nullable=False)
    category = Column(String(80), nullable=False)
    price = Column(Float, nullable=False)
    old_price = Column(Float, nullable=True)
    image = Column(String(200), nullable=False)
    # Store thumbnails as a JSON string to keep it simple with SQLite
    thumbnails = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    # Store mock reviews as text to support LLM sentiment analysis
    mock_reviews_text = Column(Text, nullable=True)
    rating = Column(Float, nullable=False)
    reviews = Column(Integer, nullable=False)
    # Store colors as a JSON string
    colors = Column(Text, nullable=True)
    is_new = Column(Boolean, default=False)

    def __init__(self, id, name, category, price, image, description, rating, reviews,
                 old_price=None, thumbnails=None, mock_reviews_text=None, colors=None, is_new=False):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.old_price = old_price
        self.image = image
        # Convert list of thumbnails to JSON string for storage
        self.thumbnails = json.dumps(thumbnails) if thumbnails else "[]"
        self.description = description
        self.mock_reviews_text = mock_reviews_text
        self.rating = rating
        self.reviews = reviews
        # Convert list of colors to JSON string for storage
        self.colors = json.dumps(colors) if colors else "[]"
        self.is_new = is_new

    def serialize(self):
        """
        Serializes the Product object to a dictionary, converting JSON strings back to lists.
        This format is suitable for sending as JSON response to the frontend.
        """
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'oldPrice': self.old_price,
            'image': self.image,
            'thumbnails': json.loads(self.thumbnails) if self.thumbnails else [],
            'description': self.description,
            'mockReviewsText': self.mock_reviews_text,
            'rating': self.rating,
            'reviews': self.reviews,
            'colors': json.loads(self.colors) if self.colors else [],
            'isNew': self.is_new
        }

    def __repr__(self):
        return f'<Product {self.name}>'

# User Model
class User(Base):
    """
    SQLAlchemy model for a user in the database.
    Represents the 'users' table.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.set_password(password) # Hash the password during initialization

    def set_password(self, password):
        """Hashes the given password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the given password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

# Function to initialize the database
def init_db():
    """
    Creates all tables defined by the Base metadata in the database.
    Also populates the products table with initial mock data if it's empty.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Populate initial product data if the products table is empty
    if Product.query.count() == 0:
        print("Populating initial product data...")
        # Use the extended mock product data directly from the frontend's original JS
        # This ensures consistency with the LLM-related fields like mockReviewsText
        initial_products_data = [
            {
                "id": 'p1', "name": 'Ultra Protective Case', "category": 'cases', "price": 29.99, "oldPrice": 39.99,
                "image": 'https://placehold.co/400x300/A78BFA/FFFFFF?text=Case+1',
                "thumbnails": [
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Case+1a',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Case+1b',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Case+1c',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Case+1d'
                ],
                "description": 'Experience ultimate protection with our Ultra Protective Case. Designed with multi-layer defense, it safeguards your phone from drops, scratches, and daily wear. Its slim profile ensures it fits comfortably in your hand and pocket.',
                "mockReviewsText": "This case is amazing! My phone survived a really bad fall, not a scratch. A bit bulky, but worth it for the protection. Highly recommend!",
                "rating": 4.8, "reviews": 125, "colors": ['#000000', '#60A5FA', '#DC2626'], "isNew": True
            },
            {
                "id": 'p2', "name": 'Tempered Glass Screen Protector', "category": 'protectors', "price": 19.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/818CF8/FFFFFF?text=Protector+1',
                "thumbnails": [
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Prot+1a',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Prot+1b',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Prot+1c',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Prot+1d'
                ],
                "description": 'Our premium tempered glass screen protector offers edge-to-edge coverage and superior scratch resistance. Maintain crystal-clear display quality and touch sensitivity.',
                "mockReviewsText": "Easy to install, but a small bubble formed on the side. Otherwise, my screen feels well protected. Good value for money.",
                "rating": 4.5, "reviews": 98, "colors": [], "isNew": False
            },
            {
                "id": 'p3', "name": 'Fast Wireless Charger Pad', "category": 'chargers', "price": 34.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/C084FC/FFFFFF?text=Charger+1',
                "thumbnails": [
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Charger+1a',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Charger+1b',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Charger+1c',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Charger+1d'
                ],
                "description": 'Charge your phone quickly and efficiently with our Fast Wireless Charger Pad. Compatible with all Qi-enabled devices, it features overheat protection and a sleek, compact design.',
                "mockReviewsText": "Charges super fast! The design is sleek and doesn't take up much space. However, it sometimes makes a faint buzzing sound, which is a bit annoying at night.",
                "rating": 4.7, "reviews": 150, "colors": ['#000000', '#E5E7EB'], "isNew": True
            },
            {
                "id": 'p4', "name": 'Universal Car Mount', "category": 'mounts', "price": 24.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/A78BFA/FFFFFF?text=Mount+1',
                "thumbnails": [
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Mount+1a',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Mount+1b',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Mount+1c',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Mount+1d'
                ],
                "description": 'Secure your phone on the go with our Universal Car Mount. Its strong suction cup and adjustable grip ensure a stable hold on any dashboard or windshield. Perfect for navigation and hands-free calls.',
                "mockReviewsText": "The suction cup doesn't hold well in hot weather; it falls off frequently. When it does stay, it's very sturdy, but the adhesive needs improvement.",
                "rating": 4.2, "reviews": 70, "colors": [], "isNew": False
            },
            {
                "id": 'p5', "name": 'Clear Hybrid Case', "category": 'cases', "price": 22.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/818CF8/FFFFFF?text=Case+2',
                "thumbnails": [
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Case+2a',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Case+2b',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Case+2c',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Case+2d'
                ],
                "description": 'Showcase your phone\'s original design with our Clear Hybrid Case. Made from durable, transparent materials, it offers excellent protection without hiding your device\'s aesthetics.',
                "mockReviewsText": "Fits perfectly and really highlights my phone's color. It does yellow a bit over time, which is a common issue with clear cases, but it protects well.",
                "rating": 4.6, "reviews": 80, "colors": [], "isNew": False
            },
            {
                "id": 'p6', "name": 'Privacy Screen Protector', "category": 'protectors', "price": 25.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/C084FC/FFFFFF?text=Protector+2',
                "thumbnails": [
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Prot+2a',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Prot+2b',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Prot+2c',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Prot+2d'
                ],
                "description": 'Keep your screen content private from prying eyes with our Privacy Screen Protector. It offers a narrow viewing angle, ensuring only you can see what\'s on your display.',
                "mockReviewsText": "The privacy feature works great, but it darkens the screen a lot, even when looking straight on. It's a trade-off, I guess. Installation was tricky.",
                "rating": 4.3, "reviews": 60, "colors": [], "isNew": False
            },
            {
                "id": 'p7', "name": 'Multi-Port Wall Charger', "category": 'chargers', "price": 29.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/A78BFA/FFFFFF?text=Charger+2',
                "thumbnails": [
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Charger+2a',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Charger+2b',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Charger+2c',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Charger+2d'
                ],
                "description": 'Charge multiple devices simultaneously with our Multi-Port Wall Charger. Equipped with fast-charging technology and multiple USB ports, it\'s perfect for families and travelers.',
                "mockReviewsText": "This charger is a lifesaver for travel! All my devices charge at once. It gets a little warm, but nothing concerning. Very satisfied.",
                "rating": 4.7, "reviews": 110, "colors": ['#000000'], "isNew": False
            },
            {
                "id": 'p8', "name": 'Magnetic Air Vent Mount', "category": 'mounts', "price": 18.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/818CF8/FFFFFF?text=Mount+2',
                "thumbnails": [
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Mount+2a',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Mount+2b',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Mount+2c',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=Mount+2d'
                ],
                "description": 'Effortlessly attach and detach your phone with our Magnetic Air Vent Mount. Its powerful magnets provide a secure grip, and the compact design keeps your dashboard clutter-free.',
                "mockReviewsText": "Great magnet, phone stays put even on bumpy roads. The only downside is it blocks some airflow from my vent, which is annoying on a hot day.",
                "rating": 4.4, "reviews": 55, "colors": [], "isNew": True
            },
            {
                "id": 'p9', "name": 'Slim Fit Case', "category": 'cases', "price": 19.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/C084FC/FFFFFF?text=Case+3',
                "thumbnails": [
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Case+3a',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Case+3b',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Case+3c',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Case+3d'
                ],
                "description": 'Our Slim Fit Case offers minimalist protection without adding bulk. Enjoy a comfortable grip and easy access to all ports and buttons.',
                "mockReviewsText": "Perfectly thin, barely notice it's there. Protection seems basic for real drops, but great for scratch prevention. Love the feel.",
                "rating": 4.5, "reviews": 90, "colors": ['#000000', '#6B7280', '#D1D5DB'], "isNew": False
            },
            {
                "id": 'p10', "name": 'Matte Screen Protector', "category": 'protectors', "price": 15.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/A78BFA/FFFFFF?text=Protector+3',
                "thumbnails": [
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Prot+3a',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Prot+3b',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Prot+3c',
                    'https://placehold.co/100x100/A78BFA/FFFFFF?text=Prot+3d'
                ],
                "description": 'Reduce glare and fingerprints with our Matte Screen Protector. Perfect for outdoor use, it provides a smooth, anti-glare surface while protecting your screen.',
                "mockReviewsText": "Anti-glare works wonders outdoors! Fingerprints are almost non-existent. My only complaint is it makes the screen slightly grainy, but it's a minor trade-off.",
                "rating": 4.1, "reviews": 45, "colors": [], "isNew": False
            },
            {
                "id": 'p11', "name": 'Portable Power Bank', "category": 'chargers', "price": 45.99, "oldPrice": 55.00,
                "image": 'https://placehold.co/400x300/818CF8/FFFFFF?text=Power+Bank+1',
                "thumbnails": [
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=PB+1a',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=PB+1b',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=PB+1c',
                    'https://placehold.co/100x100/818CF8/FFFFFF?text=PB+1d'
                ],
                "description": 'Never run out of battery with our high-capacity Portable Power Bank. It features fast charging for multiple devices and a compact design for easy portability.',
                "mockReviewsText": "This power bank is a lifesaver! I can charge my phone multiple times. It's a bit heavy, but given the capacity, that's expected. Absolutely essential for long trips.",
                "rating": 4.8, "reviews": 180, "colors": ['#000000', '#FFFFFF'], "isNew": True
            },
            {
                "id": 'p12', "name": 'Bike Phone Mount', "category": 'mounts', "price": 28.99, "oldPrice": None,
                "image": 'https://placehold.co/400x300/C084FC/FFFFFF?text=Bike+Mount+1',
                "thumbnails": [
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Bike+M+1a',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Bike+M+1b',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Bike+M+1c',
                    'https://placehold.co/100x100/C084FC/FFFFFF?text=Bike+M+1d'
                ],
                "description": 'Securely attach your phone to your bike handlebars with our sturdy Bike Phone Mount. Enjoy easy access to navigation and fitness apps during your rides.',
                "mockReviewsText": "Holds my phone securely on my mountain bike, even over rough terrain. Installation was a breeze. A bit pricey but feels very durable.",
                "rating": 4.0, "reviews": 30, "colors": [], "isNew": False
            }
        ]

        for p_data in initial_products_data:
            product = Product(
                id=p_data['id'],
                name=p_data['name'],
                category=p_data['category'],
                price=p_data['price'],
                old_price=p_data['oldPrice'],
                image=p_data['image'],
                thumbnails=p_data['thumbnails'],
                description=p_data['description'],
                mock_reviews_text=p_data['mockReviewsText'],
                rating=p_data['rating'],
                reviews=p_data['reviews'],
                colors=p_data['colors'],
                is_new=p_data['isNew']
            )
            db_session.add(product)
        db_session.commit()
        print("Initial product data populated successfully.")
    else:
        print("Database already contains product data, skipping initial population.")

