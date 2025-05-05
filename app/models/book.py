from datetime import datetime
from app import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    publisher = db.Column(db.String(255))
    publication_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    language = db.Column(db.String(50))
    pages = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=1)
    available_quantity = db.Column(db.Integer, default=1)
    location_shelf = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    cover_image = db.Column(db.String(255))
    
    # Relationship with Circulation
    circulations = db.relationship('Circulation', back_populates='book', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
        
    def is_available(self):
        """Check if the book is available for borrowing"""
        return self.available_quantity > 0
        
    def update_availability(self, change):
        """Update book availability
        
        Args:
            change (int): +1 for return, -1 for borrow
        """
        self.available_quantity += change