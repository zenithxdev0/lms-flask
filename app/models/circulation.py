from datetime import datetime, timedelta
from app import db
from app.config import Config

class Circulation(db.Model):
    __tablename__ = 'circulations'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    # Relationships
    book = db.relationship('Book', back_populates='circulations')
    member = db.relationship('Member', back_populates='circulations')
    
    def __init__(self, book_id, member_id, checkout_date=None):
        self.book_id = book_id
        self.member_id = member_id
        self.checkout_date = checkout_date or datetime.utcnow()
        self.due_date = self.checkout_date + timedelta(days=Config.MAX_LOAN_DAYS)
    
    def __repr__(self):
        return f'<Circulation #{self.id}: Book {self.book_id} - Member {self.member_id}>'
    
    def is_overdue(self):
        """Check if the loan is overdue"""
        if self.return_date:
            return self.return_date > self.due_date
        return datetime.utcnow() > self.due_date
    
    def calculate_fine(self):
        """Calculate fine for overdue books"""
        if not self.is_overdue():
            return 0.0
        
        if self.return_date:
            days_overdue = (self.return_date - self.due_date).days
        else:
            days_overdue = (datetime.utcnow() - self.due_date).days
        
        return max(0, days_overdue) * Config.FINE_PER_DAY
    
    def return_book(self):
        """Process book return"""
        self.return_date = datetime.utcnow()
        self.fine_amount = self.calculate_fine()
        self.book.update_availability(1)  # Increase available quantity by 1