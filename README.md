# Rate My Menu 🍽️

A quirky and user-friendly web application that allows users to upload restaurant menus and rate individual dishes.

## Features

- 📤 Upload restaurant menus (PDF, JPG, PNG)
- 🍽️ View restaurant menus
- ⭐ Rate individual menu items
- 📊 See top-rated dishes for each restaurant
- 💬 Add comments to your ratings

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rate-my-menu
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
python app.py
```

6. Visit `http://localhost:5000` in your web browser

## Requirements

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-WTF
- Pillow
- pdf2image
- pytesseract

## Note

For menu parsing functionality, you'll need to install:
- Tesseract OCR (for text extraction from images)
- Poppler (for PDF processing)

On macOS:
```bash
brew install tesseract poppler
```

On Ubuntu:
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

## License

MIT License 