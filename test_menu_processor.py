import os
import unittest
from menu_processor import MenuProcessor
from PIL import Image, ImageDraw, ImageFont
import tempfile

class TestMenuProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = MenuProcessor()
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test menu image
        self.test_image_path = os.path.join(self.test_dir, 'test_menu.png')
        self.create_test_menu_image()

    def create_test_menu_image(self):
        """Create a test menu image with some sample items"""
        # Create a new image with white background
        img = Image.new('RGB', (800, 600), color='white')
        d = ImageDraw.Draw(img)
        
        # Sample menu items
        menu_text = """
        APPETIZERS
        
        Garlic Bread $5.99
        Fresh baked bread with garlic butter
        
        Caesar Salad $8.99
        Crisp romaine lettuce with parmesan
        
        MAIN COURSES
        
        Spaghetti Carbonara $16.99
        Classic pasta with eggs and pancetta
        
        Grilled Salmon $24.99
        Fresh Atlantic salmon with herbs
        """
        
        # Add text to image
        d.text((50, 50), menu_text, fill='black')
        img.save(self.test_image_path)

    def test_process_image(self):
        """Test processing an image menu"""
        text_content = self.processor.process_menu(self.test_image_path)
        self.assertIsInstance(text_content, list)
        self.assertTrue(len(text_content) > 0)
        
        # Extract menu items
        menu_items = self.processor.extract_menu_items(text_content)
        self.assertIsInstance(menu_items, list)
        
        # Print extracted items for manual verification
        print("\nExtracted menu items:")
        for item in menu_items:
            print(f"Name: {item['name']}")
            print(f"Price: ${item['price']}")
            print(f"Description: {item['description']}")
            print("-" * 50)

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        os.rmdir(self.test_dir)

if __name__ == '__main__':
    unittest.main() 