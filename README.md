# Bibliotheca: Library Management System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-v3.12-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3.2-green.svg)

Bibliotheca is a comprehensive library management system built with Flask that helps librarians manage their collections, track circulation, and maintain member records efficiently.

![Library Management System](app/static/img/library-screenshot.jpg)

## Features

- **Book Management**
  - Add, edit, and remove books from the library collection
  - Track book details including title, author, ISBN, genre, and more
  - Manage book quantities and locations

- **Member Management**
  - Register new members and maintain their profiles
  - Track contact information and membership status
  - Monitor checkout history and current loans

- **Circulation**
  - Process book checkouts and returns
  - Track due dates and calculate late fees automatically
  - Send notifications for overdue items (optional)

- **Reporting**
  - Generate circulation statistics
  - Inventory reports and book status
  - Overdue book reports and fine collection tracking

- **User-friendly Interface**
  - Responsive design for desktop and mobile
  - Search functionality for books and members
  - Role-based access control (admin/staff/members)

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bibliotheca.git
   cd bibliotheca
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate the virtual environment
   # For Windows
   venv\Scripts\activate
   
   # For macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file with your configuration settings
   # Make sure to generate a strong SECRET_KEY
   ```

5. **Initialize the database**
   ```bash
   # The database will be created when you run the app for the first time
   # To seed the database with sample data:
   python seed_db.py
   ```

## Running the Application

1. **Start the development server**
   ```bash
   python run.py
   ```

2. **Access the application**
   Open your browser and navigate to http://localhost:5000

3. **Default login credentials** (if using seed_db.py)
   - Admin User: admin@example.com / admin123
   - Regular User: john@example.com / password123

## Project Structure

```
bibliotheca/
├── app/                     # Application package
│   ├── __init__.py          # App initialization
│   ├── config.py            # Configuration settings
│   ├── models/              # Database models
│   ├── routes/              # Route handlers
│   ├── static/              # Static files (CSS, JS, images)
│   ├── templates/           # Jinja2 templates
│   └── utils/               # Utility functions
├── migrations/              # Database migrations
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── seed_db.py               # Database seeding script
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in your .env file
2. Use a production WSGI server like Gunicorn
3. Set up a reverse proxy with Nginx or Apache
4. Use a PostgreSQL database instead of SQLite

Example deployment with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Flask and its extensions
- SQLAlchemy ORM
- Bootstrap for frontend styling
- Font Awesome for icons
