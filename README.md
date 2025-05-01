# Plant Shop

A modern Django-based e-commerce platform for selling plants and gardening supplies.

## Features

- Responsive, mobile-first design
- Product catalog with categories
- Advanced stock status system (In Stock, On Order, Out of Stock)
- Shopping cart functionality
- Detailed product pages with plant characteristics
- Image gallery with thumbnails
- Modern UI with smooth animations and transitions

## Tech Stack

- Python 3.x
- Django 4.x
- HTML5/CSS3
- JavaScript (ES6+)
- SQLite (development)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd plant_shop
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to view the site.

## Project Structure

- `catalog/` - Product catalog app
- `cart/` - Shopping cart functionality
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `media/` - User-uploaded content

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 

# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Email settings
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
CONTACT_EMAIL=your-email@gmail.com

# Telegram settings
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_CHAT_ID=your-chat-id 