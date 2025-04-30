# 🍽️ Rate My Menu

Ever been to a restaurant with a 4.5-star rating, only to discover that their signature dish tastes like cardboard? Or found yourself scrolling through endless reviews trying to figure out which menu items are actually worth ordering? 

Welcome to **Rate My Menu** - where we believe that while restaurants can be great overall, not every dish is created equal! 🎯

## 🤔 Why Rate My Menu?

Picture this: You're at a new restaurant, staring at a menu longer than a CVS receipt. The restaurant has great reviews, but you're still playing Russian roulette with your taste buds. That's where we come in!

- 🎯 **Dish-by-Dish Ratings**: No more guessing games! See exactly which dishes are worth your hard-earned money
- 📱 **Smart Menu Parsing**: Our AI-powered system (Tesseract + LLaVA) automatically extracts dishes and prices from menus
- 📍 **Nearby Restaurants**: Find and rate menus from restaurants around you
- ⭐ **Community Driven**: Share your culinary wisdom with fellow foodies

## 🚀 Features

- **AI-Powered Menu Parsing**: Combines Tesseract OCR with LLaVA (Large Language and Vision Assistant) for accurate menu extraction
- **Smart Dish Recognition**: Automatically identifies dishes, prices, and categories
- **Google Places Integration**: Find restaurants near you and see their menus
- **Dish Ratings**: Rate individual menu items and leave helpful comments
- **Top Picks**: See which dishes are crowd favorites at each restaurant

## 🛠️ Tech Stack

- **Backend**: Flask
- **Database**: SQLite
- **OCR**: Tesseract + LLaVA
- **Location Services**: Google Places API
- **Frontend**: Bootstrap + Custom CSS

## 🍕 How It Works

1. **Find a Restaurant**: Use your location or search for a specific place
2. **Upload Menu**: Take a photo or upload a PDF of the menu
3. **AI Processing**: Our system automatically extracts dishes and prices
4. **Rate & Review**: Share your thoughts on specific menu items
5. **Help Others**: Your ratings help fellow foodies make better choices

## 🚀 Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR:
   ```bash
   # On macOS
   brew install tesseract
   
   # On Ubuntu
   sudo apt-get install tesseract-ocr
   ```
4. Set up your environment variables in `.env`
5. Run the application:
   ```bash
   python app.py
   ```

## 🤝 Contributing

Found a bug? Have a feature request? We'd love to hear from you! Feel free to open an issue or submit a pull request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 The Vision

We're on a mission to make restaurant menus more transparent and help foodies make better dining decisions. Because let's face it - life's too short for mediocre food! 🍜

---

Made with ❤️ by [Rigveda Vangipurapu](https://github.com/RigvedaVangipurapu)

*"Because every dish deserves its moment in the spotlight!"* ✨ 