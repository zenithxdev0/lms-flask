from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.book import Book
from app.models.member import Member
from app.models.circulation import Circulation
from app.config import Config

circulation_bp = Blueprint('circulation', __name__, url_prefix='/circulation')

@circulation_bp.route('/')
@login_required
def index():
    """List all circulation records"""
    # Admins see all records, regular members see only their own
    if current_user.is_admin:
        circulations = Circulation.query.order_by(Circulation.checkout_date.desc()).all()
    else:
        circulations = Circulation.query.filter_by(member_id=current_user.id).order_by(Circulation.checkout_date.desc()).all()
    
    return render_template('circulation/index.html', circulations=circulations)

@circulation_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Check out a book to a member"""
    if request.method == 'POST':
        book_id = request.form.get('book_id', type=int)
        member_id = request.form.get('member_id', type=int)
        
        # Validate book and member
        book = Book.query.get_or_404(book_id)
        member = Member.query.get_or_404(member_id)
        
        # Check if book is available
        if not book.is_available():
            flash('Book is not available for checkout.', 'danger')
            return redirect(url_for('circulation.checkout'))
        
        # Check if member has reached max books limit
        active_loans_count = member.get_active_loans_count()
        if active_loans_count >= Config.MAX_BOOKS_PER_USER:
            flash(f'Member has reached the maximum loan limit of {Config.MAX_BOOKS_PER_USER} books.', 'danger')
            return redirect(url_for('circulation.checkout'))
        
        # Check if member has any overdue books
        if member.has_overdue_books():
            flash('Member has overdue books. Cannot check out more books until overdue items are returned.', 'danger')
            return redirect(url_for('circulation.checkout'))
        
        # Create new circulation record
        checkout = Circulation(book_id=book_id, member_id=member_id)
        
        # Update book availability
        book.update_availability(-1)  # Decrease available quantity by 1
        
        db.session.add(checkout)
        db.session.commit()
        
        flash(f'Book "{book.title}" checked out successfully to {member.full_name}.', 'success')
        return redirect(url_for('circulation.index'))
    
    # For GET request, show checkout form
    books = Book.query.filter(Book.available_quantity > 0).all()
    members = Member.query.filter_by(is_active=True).all()
    
    return render_template('circulation/checkout.html', books=books, members=members)

@circulation_bp.route('/return/<int:circulation_id>', methods=['GET', 'POST'])
@login_required
def return_book(circulation_id):
    """Return a checked out book"""
    circulation = Circulation.query.get_or_404(circulation_id)
    
    # Only allow return if book hasn't been returned yet
    if circulation.return_date:
        flash('This book has already been returned.', 'warning')
        return redirect(url_for('circulation.index'))
    
    if request.method == 'POST':
        # Process return
        circulation.return_book()
        
        # Update database
        db.session.commit()
        
        # Check if there was a fine
        if circulation.fine_amount > 0:
            flash(f'Book returned with fine: ${circulation.fine_amount:.2f}', 'warning')
        else:
            flash('Book returned successfully.', 'success')
        
        return redirect(url_for('circulation.index'))
    
    # For GET request, show confirmation form
    return render_template('circulation/return.html', circulation=circulation)

@circulation_bp.route('/overdue')
@login_required
def overdue():
    """List all overdue books"""
    today = datetime.utcnow()
    
    # Build query based on user role
    if current_user.is_admin:
        overdue_loans = Circulation.query.filter(
            Circulation.return_date == None,
            Circulation.due_date < today
        ).order_by(Circulation.due_date).all()
    else:
        overdue_loans = Circulation.query.filter(
            Circulation.member_id == current_user.id,
            Circulation.return_date == None,
            Circulation.due_date < today
        ).order_by(Circulation.due_date).all()
    
    return render_template('circulation/overdue.html', overdue_loans=overdue_loans)

@circulation_bp.route('/renew/<int:circulation_id>', methods=['POST'])
@login_required
def renew(circulation_id):
    """Renew a book loan"""
    circulation = Circulation.query.get_or_404(circulation_id)
    
    # Check if user has permission
    if not current_user.is_admin and current_user.id != circulation.member_id:
        flash('You do not have permission to renew this loan.', 'danger')
        return redirect(url_for('circulation.index'))
    
    # Only allow renewal if book hasn't been returned yet
    if circulation.return_date:
        flash('This book has already been returned and cannot be renewed.', 'warning')
        return redirect(url_for('circulation.index'))
    
    # Check if book is overdue
    if circulation.is_overdue():
        flash('Overdue books cannot be renewed. Please return the book and pay the fine.', 'danger')
        return redirect(url_for('circulation.index'))
    
    # Extend due date
    from datetime import timedelta
    circulation.due_date = circulation.due_date + timedelta(days=Config.MAX_LOAN_DAYS)
    db.session.commit()
    
    flash(f'Book renewed successfully. New due date: {circulation.due_date.strftime("%Y-%m-%d")}', 'success')
    return redirect(url_for('circulation.index'))