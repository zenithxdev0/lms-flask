from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.book import Book
from app.models.member import Member
from app.models.circulation import Circulation
from app import db

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    """Reports dashboard"""
    # Only admins can access reports
    if not current_user.is_admin:
        return render_template('errors/403.html'), 403
    
    return render_template('reports/index.html')

@reports_bp.route('/circulation-stats')
@login_required
def circulation_stats():
    """Circulation statistics report"""
    if not current_user.is_admin:
        return render_template('errors/403.html'), 403
    
    # Get time period from query params (defaults to last 30 days)
    days = request.args.get('days', default=30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total checkouts in period
    total_checkouts = Circulation.query.filter(Circulation.checkout_date >= start_date).count()
    
    # Total returns in period
    total_returns = Circulation.query.filter(
        Circulation.return_date.isnot(None),
        Circulation.return_date >= start_date
    ).count()
    
    # Current active loans
    active_loans = Circulation.query.filter(Circulation.return_date.is_(None)).count()
    
    # Overdue loans
    overdue_loans = Circulation.query.filter(
        Circulation.return_date.is_(None),
        Circulation.due_date < datetime.utcnow()
    ).count()
    
    # Total fines collected
    fines_collected = db.session.query(func.sum(Circulation.fine_amount)).filter(
        Circulation.fine_paid == True,
        Circulation.return_date >= start_date
    ).scalar() or 0
    
    # Books with highest circulation
    popular_books = db.session.query(
        Book,
        func.count(Circulation.id).label('loan_count')
    ).join(Book.circulations).filter(
        Circulation.checkout_date >= start_date
    ).group_by(Book.id).order_by(func.count(Circulation.id).desc()).limit(10).all()
    
    return render_template(
        'reports/circulation_stats.html',
        days=days,
        total_checkouts=total_checkouts,
        total_returns=total_returns,
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        fines_collected=fines_collected,
        popular_books=popular_books
    )

@reports_bp.route('/member-activity')
@login_required
def member_activity():
    """Member activity report"""
    if not current_user.is_admin:
        return render_template('errors/403.html'), 403
    
    # Get time period from query params (defaults to last 30 days)
    days = request.args.get('days', default=30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Most active members (by number of checkouts)
    active_members = db.session.query(
        Member,
        func.count(Circulation.id).label('checkout_count')
    ).join(Member.circulations).filter(
        Circulation.checkout_date >= start_date
    ).group_by(Member.id).order_by(func.count(Circulation.id).desc()).limit(10).all()
    
    # Members with overdue books
    members_with_overdue = db.session.query(
        Member,
        func.count(Circulation.id).label('overdue_count')
    ).join(Member.circulations).filter(
        Circulation.return_date.is_(None),
        Circulation.due_date < datetime.utcnow()
    ).group_by(Member.id).order_by(func.count(Circulation.id).desc()).all()
    
    # New member registrations
    new_members = Member.query.filter(Member.registration_date >= start_date).count()
    
    return render_template(
        'reports/member_activity.html',
        days=days,
        active_members=active_members,
        members_with_overdue=members_with_overdue,
        new_members=new_members
    )

@reports_bp.route('/inventory')
@login_required
def inventory():
    """Book inventory report"""
    if not current_user.is_admin:
        return render_template('errors/403.html'), 403
    
    # Total books in collection
    total_books = db.session.query(func.sum(Book.quantity)).scalar() or 0
    
    # Total unique titles
    unique_titles = Book.query.count()
    
    # Books by category
    books_by_category = db.session.query(
        Book.category, 
        func.count(Book.id).label('book_count'),
        func.sum(Book.quantity).label('total_copies')
    ).group_by(Book.category).order_by(func.count(Book.id).desc()).all()
    
    # Books with zero availability
    unavailable_books = Book.query.filter(Book.available_quantity == 0).all()
    
    # Books never checked out (may need optimization for large libraries)
    never_loaned = Book.query.filter(~Book.circulations.any()).all()
    
    return render_template(
        'reports/inventory.html',
        total_books=total_books,
        unique_titles=unique_titles,
        books_by_category=books_by_category,
        unavailable_books=unavailable_books,
        never_loaned=never_loaned
    )