import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///bibliotheca.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    
    # Application settings
    DEMO_MODE = os.environ.get('DEMO_MODE', 'False').lower() == 'true'
    
    # Library circulation settings
    MAX_LOAN_DAYS = 14
    FINE_PER_DAY = 0.25  # 25 cents per day overdue
    MAX_BOOKS_PER_MEMBER = 5
    
    # Email configuration for future use
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Pagination settings
    BOOKS_PER_PAGE = 12
    MEMBERS_PER_PAGE = 15

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Configuration dictionary to easily switch between environments
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}