import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv

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
            print(f"Error searching nearby restaurants: {str(e)}")
            return []
    
    def get_restaurant_details(self, place_id):
        """Get detailed information about a restaurant."""
        try:
            place_details = self.client.place(place_id, fields=[
                'name', 'formatted_address', 'formatted_phone_number',
                'website', 'opening_hours', 'price_level', 'rating',
                'photos', 'reviews'
            ])
            return place_details.get('result', {})
        except Exception as e:
            print(f"Error getting restaurant details: {str(e)}")
            return {}
    
    def get_menu_url(self, place_id):
        """Get the menu URL for a restaurant if available."""
        try:
            place_details = self.client.place(place_id, fields=['website'])
            website = place_details.get('result', {}).get('website', '')
            
            # Common menu URL patterns
            menu_urls = [
                f"{website}/menu",
                f"{website}/menus",
                f"{website}/food-menu",
                f"{website}/drinks-menu"
            ]
            
            # Check if any of these URLs exist
            for url in menu_urls:
                try:
                    response = self.client._request(url, method='HEAD')
                    if response.status_code == 200:
                        return url
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Error getting menu URL: {str(e)}")
            return None 