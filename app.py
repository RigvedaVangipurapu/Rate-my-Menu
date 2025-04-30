from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, FloatField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
import os
from werkzeug.utils import secure_filename
import json
from menu_processor import MenuProcessor
from google_places import GooglePlacesAPI
from dotenv import load_dotenv
import logging
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menu_ratings.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Google Places API if key is available
try:
    google_places = GooglePlacesAPI()
except ValueError:
    print("Warning: Google Places API key not found or invalid. Some features may be limited.")
    google_places = None

menu_processor = MenuProcessor()  # Initialize the menu processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    google_place_id = db.Column(db.String(100), unique=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    rating = db.Column(db.Float)
    menus = db.relationship('Menu', backref='restaurant', lazy=True)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=True)
    source = db.Column(db.String(20))  # 'google', 'upload', or 'manual'
    items = db.relationship('MenuItem', backref='menu', lazy=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    ratings = db.relationship('Rating', backref='menu_item', lazy=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)

# Forms
class RestaurantForm(FlaskForm):
    name = StringField('Restaurant Name', validators=[DataRequired()])
    menu_file = FileField('Menu File', validators=[DataRequired()])
    submit = SubmitField('Upload Menu')

class RatingForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Rating')

class ManualItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description (Optional)')
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Add Item')

# Initialize database
def init_db():
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Create all tables with the current schema
        print("Database initialized successfully!")

@app.route('/')
def index():
    # Get user's location from request (you might want to use a more reliable method)
    # For now, we'll use a default location
    latitude = request.args.get('lat', 37.7749)  # Default to San Francisco
    longitude = request.args.get('lng', -122.4194)
    
    # Search for nearby restaurants
    nearby_restaurants = google_places.search_nearby_restaurants(latitude, longitude)
    
    # Get or create restaurant entries in our database
    restaurants = []
    for place in nearby_restaurants:
        restaurant = Restaurant.query.filter_by(google_place_id=place['place_id']).first()
        if not restaurant:
            # Get detailed information
            details = google_places.get_restaurant_details(place['place_id'])
            restaurant = Restaurant(
                name=place['name'],
                google_place_id=place['place_id'],
                address=details.get('formatted_address', ''),
                phone=details.get('formatted_phone_number', ''),
                website=details.get('website', ''),
                rating=details.get('rating', 0)
            )
            db.session.add(restaurant)
            db.session.commit()
        restaurants.append(restaurant)
    
    return render_template('index.html', 
                         restaurants=restaurants,
                         latitude=latitude,
                         longitude=longitude)

@app.route('/restaurant/<int:restaurant_id>')
def restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = []
    top_items = []
    
    # Try to get menu items from Google Places first
    if restaurant.google_place_id and google_places:
        menu_items = google_places.get_menu_items(restaurant.google_place_id)
        if not menu_items:
            # If no menu items from Google, try to get menu photos
            menu_photos = google_places.get_menu_photos(restaurant.google_place_id)
            if menu_photos:
                # Process menu photos using MenuProcessor
                processor = MenuProcessor()
                for photo in menu_photos:
                    # Save photo temporarily
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{restaurant_id}.jpg')
                    photo.save(temp_path)
                    try:
                        # Process the photo
                        text_content = processor.process_menu(temp_path)
                        items = processor.extract_menu_items(text_content)
                        menu_items.extend(items)
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
    
    # If still no menu items, check database
    if not menu_items:
        menu = Menu.query.filter_by(restaurant_id=restaurant_id).first()
        if menu:
            menu_items = MenuItem.query.filter_by(menu_id=menu.id).all()
    
    # Get top rated items
    if menu_items:
        top_items = sorted(menu_items, 
                         key=lambda x: sum(r.rating for r in x.ratings)/len(x.ratings) if x.ratings else 0,
                         reverse=True)[:5]
    
    return render_template('restaurant.html', 
                         restaurant=restaurant,
                         menu_items=menu_items,
                         top_items=top_items)

@app.route('/upload/<int:restaurant_id>', methods=['GET', 'POST'])
def upload(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = RestaurantForm()
    
    if form.validate_on_submit():
        menu_file = form.menu_file.data
        
        try:
            # Save menu file
            filename = secure_filename(menu_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            logger.info(f"Saving uploaded file to: {file_path}")
            menu_file.save(file_path)
            
            # Verify file was saved
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Failed to save uploaded file: {file_path}")
            
            # Create menu entry
            menu = Menu(
                restaurant_id=restaurant.id,
                file_path=file_path,
                source='upload'
            )
            db.session.add(menu)
            db.session.commit()
            
            try:
                # Process menu using the new MenuProcessor
                logger.info(f"Processing menu file: {file_path}")
                text_content = menu_processor.process_menu(file_path)
                menu_items = menu_processor.extract_menu_items(text_content)
                
                logger.info(f"Extracted {len(menu_items)} menu items")
                for item_data in menu_items:
                    menu_item = MenuItem(
                        menu_id=menu.id,
                        name=item_data['name'],
                        description=item_data.get('description', ''),
                        price=float(item_data['price']) if item_data.get('price') else None
                    )
                    db.session.add(menu_item)
                
                db.session.commit()
                flash('Menu uploaded and processed successfully!', 'success')
                
            except Exception as e:
                logger.error(f"Error processing menu: {str(e)}")
                db.session.delete(menu)
                db.session.commit()
                flash(f'Error processing menu: {str(e)}', 'error')
            
        except Exception as e:
            logger.error(f"Error handling upload: {str(e)}")
            flash(f'Error handling upload: {str(e)}', 'error')
            
        return redirect(url_for('restaurant', restaurant_id=restaurant.id))
    
    return render_template('upload.html', form=form, restaurant=restaurant)

@app.route('/rate/<int:item_id>', methods=['GET', 'POST'])
def rate_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    form = RatingForm()
    
    if form.validate_on_submit():
        rating = Rating(
            menu_item_id=item_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(rating)
        db.session.commit()
        flash('Rating submitted successfully!')
        return redirect(url_for('restaurant', restaurant_id=item.menu.restaurant_id))
    
    return render_template('rate.html', item=item, form=form)

@app.route('/restaurant/<int:restaurant_id>/add_item', methods=['GET', 'POST'])
def add_menu_item(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = ManualItemForm()
    
    if form.validate_on_submit():
        # Create a new menu if one doesn't exist
        menu = Menu.query.filter_by(restaurant_id=restaurant_id).first()
        if not menu:
            menu = Menu(
                restaurant_id=restaurant_id,
                source='manual',
                file_path=None  # Explicitly set to None for manual items
            )
            db.session.add(menu)
            db.session.commit()
        
        # Create the menu item
        item = MenuItem(
            menu_id=menu.id,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('restaurant', restaurant_id=restaurant_id))
    
    return render_template('add_item.html', form=form, restaurant=restaurant)

if __name__ == '__main__':
    init_db()  # Initialize the database before running the app
    app.run(debug=True) 