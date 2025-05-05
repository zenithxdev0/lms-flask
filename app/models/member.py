from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

class Member(db.Model, UserMixin):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationship with Circulation
    circulations = db.relationship('Circulation', back_populates='member', cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Member {self.member_id}: {self.full_name}>'
    
    def has_overdue_books(self):
        """Check if member has any overdue books"""
        from app.models.circulation import Circulation
        return any(circulation.is_overdue() for circulation in self.circulations if not circulation.return_date)
    
    def get_active_loans_count(self):
        """Get the count of books currently borrowed by the member"""
        return sum(1 for circulation in self.circulations if not circulation.return_date)

@login_manager.user_loader
def load_user(id):
    return Member.query.get(int(id))