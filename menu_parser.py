import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import json

def extract_menu_items(text):
    """Extract menu items, descriptions, and prices from OCR text."""
    items = []
    
    # Split text into lines
    lines = text.split('\n')
    
    current_item = None
    current_description = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Look for price patterns (e.g., $12.99, 12.99, $12)
        price_match = re.search(r'(\$?\d+\.?\d*)', line)
        
        if price_match:
            # If we have a current item, save it
            if current_item:
                items.append({
                    'name': current_item,
                    'description': ' '.join(current_description) if current_description else '',
                    'price': float(price_match.group(1).replace('$', ''))
                })
                current_item = None
                current_description = []
            
            # The line before the price is likely the item name
            item_name = line[:price_match.start()].strip()
            if item_name:
                current_item = item_name
        else:
            # If we have a current item, this line might be part of the description
            if current_item:
                current_description.append(line.strip())
    
    # Add the last item if exists
    if current_item:
        items.append({
            'name': current_item,
            'description': ' '.join(current_description) if current_description else '',
            'price': None  # No price found for the last item
        })
    
    return items

def parse_menu_with_ocr(image_path):
    """Parse menu using Tesseract OCR."""
    try:
        # Convert PDF to images if needed
        if image_path.lower().endswith('.pdf'):
            images = convert_from_path(image_path)
            # For now, we'll just use the first page
            if images:
                image = images[0]
                # Save as temporary image
                temp_path = "temp_menu.jpg"
                image.save(temp_path, "JPEG")
                image_path = temp_path
        
        # Perform OCR
        text = pytesseract.image_to_string(Image.open(image_path))
        
        # Clean up temporary file if it exists
        if 'temp_path' in locals():
            os.remove(temp_path)
        
        # Extract menu items
        items = extract_menu_items(text)
        
        # Convert to JSON string
        return json.dumps(items)
        
    except Exception as e:
        print(f"Error parsing menu: {str(e)}")
        return None 