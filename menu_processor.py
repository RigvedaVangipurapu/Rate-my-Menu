import os
import tempfile
from typing import List, Union
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import logging
import re
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MenuProcessor:
    def __init__(self):
        """Initialize the MenuProcessor with default settings."""
        # Configure pytesseract path if needed (usually not necessary if installed via brew)
        # pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.avif'}
        self.temp_dir = tempfile.gettempdir()
        
        # Common section headers in menus
        self.section_headers = {
            'appetizers', 'starters', 'main courses', 'entrees', 'desserts',
            'beverages', 'drinks', 'sides', 'salads', 'soups', 'breakfast',
            'lunch', 'dinner', 'specials'
        }

    def _convert_avif_to_jpeg(self, avif_path: str) -> str:
        """Convert AVIF image to JPEG format using ImageMagick."""
        try:
            jpeg_path = os.path.join(self.temp_dir, f"{os.path.basename(avif_path)}.jpg")
            cmd = ['convert', avif_path, jpeg_path]
            subprocess.run(cmd, check=True)
            return jpeg_path
        except Exception as e:
            logger.error(f"Error converting AVIF to JPEG: {str(e)}")
            raise

    def process_menu(self, file_path: str) -> List[str]:
        """
        Process a menu file (PDF or image) and extract text content.
        
        Args:
            file_path (str): Path to the menu file
            
        Returns:
            List[str]: List of extracted text from each page/image
        """
        try:
            # Verify file exists and is readable
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"File not readable: {file_path}")
            
            logger.info(f"Processing file: {file_path}")
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._process_pdf(file_path)
            elif file_ext in self.supported_image_formats:
                return self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error processing menu file: {str(e)}")
            raise

    def _process_pdf(self, pdf_path: str) -> List[str]:
        """
        Process a PDF file and extract text content from each page.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[str]: List of extracted text from each page
        """
        try:
            logger.info(f"Converting PDF to images: {pdf_path}")
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            text_content = []
            
            for i, image in enumerate(images):
                logger.info(f"Processing PDF page {i+1}")
                # Extract text from the image
                text = pytesseract.image_to_string(image)
                text_content.append(text.strip())
            
            return text_content
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

    def _process_image(self, image_path: str) -> List[str]:
        """
        Process an image file and extract text content.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            List[str]: List containing the extracted text
        """
        try:
            logger.info(f"Opening image file: {image_path}")
            
            # Check if file is AVIF
            file_type = subprocess.run(['file', image_path], capture_output=True, text=True).stdout
            if 'AVIF' in file_type:
                logger.info("Detected AVIF format, converting to JPEG")
                image_path = self._convert_avif_to_jpeg(image_path)
            
            # Open and process the image
            with Image.open(image_path) as img:
                logger.info(f"Image format: {img.format}, Mode: {img.mode}, Size: {img.size}")
                
                # Convert to RGB if necessary
                if img.mode not in ('L', 'RGB'):
                    logger.info(f"Converting image from {img.mode} to RGB")
                    img = img.convert('RGB')
                
                logger.info("Extracting text from image")
                # Extract text from the image
                text = pytesseract.image_to_string(img)
                return [text.strip()]
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise

    def extract_menu_items(self, text_content: List[str]) -> List[dict]:
        """
        Extract menu items from the processed text content.
        
        Args:
            text_content (List[str]): List of text content from processed pages
            
        Returns:
            List[dict]: List of dictionaries containing menu items with their details
        """
        menu_items = []
        current_section = None
        
        for page_text in text_content:
            # Split text into lines and clean them
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Check if this line is a section header
                if line.lower() in self.section_headers:
                    current_section = line
                    i += 1
                    continue
                
                # Try to identify price patterns
                price_match = re.search(r'\$\s*(\d+\.?\d*)', line)
                
                if price_match:
                    # Extract the price
                    price_str = price_match.group(1)
                    try:
                        price = float(price_str)
                        
                        # Extract the name (everything before the price)
                        name = line[:price_match.start()].strip()
                        
                        # Look ahead for description in the next line
                        description = ""
                        if i + 1 < len(lines):
                            next_line = lines[i + 1]
                            # Check if next line is not a menu item (no price) and not a section header
                            if ('$' not in next_line and 
                                not any(next_line.lower() in header for header in self.section_headers)):
                                description = next_line
                                i += 1  # Skip the description line in next iteration
                        
                        # Create menu item if we have a valid name and price
                        if name and price > 0:
                            menu_items.append({
                                'name': name,
                                'price': price,
                                'description': description,
                                'section': current_section
                            })
                    except ValueError:
                        logger.warning(f"Failed to parse price from line: {line}")
                
                i += 1
        
        return menu_items

# Example usage:
# processor = MenuProcessor()
# text_content = processor.process_menu('path/to/menu.pdf')
# menu_items = processor.extract_menu_items(text_content) 