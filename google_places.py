import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class GooglePlacesAPI:
    def __init__(self):
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not api_key:
            raise ValueError("Google Places API key not found in environment variables")
        self.client = googlemaps.Client(key=api_key)
    
    def search_nearby_restaurants(self, latitude, longitude, radius=5000):
        """Search for nearby restaurants using Google Places API."""
        try:
            places_result = self.client.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                type='restaurant'
            )
            return places_result.get('results', [])
        except Exception as e:
            logger.error(f"Error searching nearby restaurants: {str(e)}")
            return []
    
    def get_restaurant_details(self, place_id):
        """Get detailed information about a restaurant."""
        try:
            place_details = self.client.place(place_id, fields=[
                'name', 'formatted_address', 'formatted_phone_number',
                'website', 'opening_hours', 'price_level', 'rating',
                'photos', 'reviews', 'menu', 'serves_menu'
            ])
            return place_details.get('result', {})
        except Exception as e:
            logger.error(f"Error getting restaurant details: {str(e)}")
            return {}
    
    def get_menu_url(self, place_id):
        """Get the menu URL for a restaurant if available."""
        try:
            place_details = self.client.place(place_id, fields=['website', 'menu'])
            result = place_details.get('result', {})
            
            # First check if there's a direct menu URL from Google
            if 'menu' in result:
                menu_url = result['menu'].get('url')
                if menu_url:
                    return menu_url
            
            # If no direct menu URL, try common patterns on the website
            website = result.get('website', '')
            if not website:
                return None
                
            # Common menu URL patterns
            menu_urls = [
                f"{website}/menu",
                f"{website}/menus",
                f"{website}/food-menu",
                f"{website}/drinks-menu",
                f"{website}/dinner-menu",
                f"{website}/lunch-menu",
                f"{website}/breakfast-menu"
            ]
            
            # Check if any of these URLs exist
            for url in menu_urls:
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        return url
                except:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"Error getting menu URL: {str(e)}")
            return None

    def get_menu_photos(self, place_id, max_photos=5):
        """Get menu photos from Google Places API."""
        try:
            place_details = self.client.place(place_id, fields=['photos'])
            photos = place_details.get('result', {}).get('photos', [])
            
            menu_photos = []
            for photo in photos[:max_photos]:
                try:
                    # Get the photo reference
                    photo_reference = photo.get('photo_reference')
                    if not photo_reference:
                        continue
                    
                    # Get the photo URL
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={os.getenv('GOOGLE_PLACES_API_KEY')}"
                    
                    # Download the photo
                    response = requests.get(photo_url)
                    if response.status_code == 200:
                        # Convert to PIL Image
                        image = Image.open(io.BytesIO(response.content))
                        menu_photos.append(image)
                except Exception as e:
                    logger.error(f"Error processing photo: {str(e)}")
                    continue
            
            return menu_photos
        except Exception as e:
            logger.error(f"Error getting menu photos: {str(e)}")
            return []

    def get_menu_items(self, place_id):
        """Get menu items from Google Places API if available."""
        try:
            place_details = self.client.place(place_id, fields=['menu'])
            menu = place_details.get('result', {}).get('menu', {})
            
            if not menu:
                return []
            
            menu_items = []
            # Process menu sections
            for section in menu.get('sections', []):
                section_name = section.get('name', '')
                for item in section.get('items', []):
                    menu_items.append({
                        'name': item.get('name', ''),
                        'description': item.get('description', ''),
                        'price': item.get('price', ''),
                        'section': section_name
                    })
            
            return menu_items
        except Exception as e:
            logger.error(f"Error getting menu items: {str(e)}")
            return [] 