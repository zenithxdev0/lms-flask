from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import uuid
from app import db
from app.models.member import Member

members_bp = Blueprint('members', __name__, url_prefix='/members')

@members_bp.route('/')
@login_required
def index():
    """List all members with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page
    
    # Get paginated members
    pagination = Member.query.paginate(page=page, per_page=per_page, error_out=False)
    members = pagination.items
    total_pages = pagination.pages
    
    return render_template(
        'members/index.html', 
        members=members, 
        page=page, 
        total_pages=total_pages
    )

@members_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new member - admin only"""
    if not current_user.is_admin:
        flash('You do not have permission to add members.', 'danger')
        return redirect(url_for('members.index'))
        
    if request.method == 'POST':
        # Extract form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        is_active = 'is_active' in request.form
        is_admin = 'is_admin' in request.form
        
        # Check if email already exists
        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            flash('Email already registered.', 'danger')
            return redirect(url_for('members.add'))
        
        # Generate a unique member ID
        member_id = f"MEM{uuid.uuid4().hex[:8].upper()}"
        
        # Create new member
        new_member = Member(
            member_id=member_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            address=address,
            is_active=is_active,
            is_admin=is_admin
        )
        
        # Save to database
        db.session.add(new_member)
        db.session.commit()
        
        flash('Member added successfully!', 'success')
        return redirect(url_for('members.view', member_id=new_member.id))
    
    return render_template('members/add.html')

@members_bp.route('/search')
@login_required
def search():
    """Search for members"""
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page
    
    if query:
        search_term = f"%{query}%"
        pagination = Member.query.filter(
            (Member.first_name.ilike(search_term)) |
            (Member.last_name.ilike(search_term)) |
            (Member.email.ilike(search_term)) |
            (Member.member_id.ilike(search_term))
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        pagination = Member.query.paginate(page=page, per_page=per_page, error_out=False)
    
    members = pagination.items
    total_pages = pagination.pages
    
    return render_template(
        'members/index.html', 
        members=members, 
        page=page, 
        total_pages=total_pages,
        search_query=query
    )

@members_bp.route('/<int:member_id>')
@login_required
def view(member_id):
    """View a specific member's details"""
    member = Member.query.get_or_404(member_id)
    return render_template('members/view.html', member=member)

@members_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new member"""
    if request.method == 'POST':
        # Extract form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Check if email already exists
        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            flash('Email already registered. Please login instead.', 'danger')
            return redirect(url_for('members.login'))
        
        # Generate a unique member ID
        member_id = f"MEM{uuid.uuid4().hex[:8].upper()}"
        
        # Create new member
        new_member = Member(
            member_id=member_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            address=address
        )
        
        # Save to database
        db.session.add(new_member)
        db.session.commit()
        
        # Log in the new member
        login_user(new_member)
        
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('members/register.html')

@members_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Member login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        member = Member.query.filter_by(email=email).first()
        
        if member and check_password_hash(member.password_hash, password):
            if not member.is_active:
                flash('Your account is inactive. Please contact the library.', 'danger')
                return redirect(url_for('members.login'))
                
            login_user(member, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('members/login.html')

@members_bp.route('/logout')
@login_required
def logout():
    """Member logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@members_bp.route('/<int:member_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(member_id):
    """Edit an existing member"""
    # Only admins can edit other members
    if not current_user.is_admin and current_user.id != member_id:
        flash('You do not have permission to edit this profile.', 'danger')
        return redirect(url_for('index'))
    
    member = Member.query.get_or_404(member_id)
    
    if request.method == 'POST':
        member.first_name = request.form.get('first_name')
        member.last_name = request.form.get('last_name')
        member.email = request.form.get('email')
        member.phone = request.form.get('phone')
        member.address = request.form.get('address')
        
        # Only update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            member.password_hash = generate_password_hash(new_password)
        
        # Only admins can change admin status
        if current_user.is_admin:
            member.is_active = 'is_active' in request.form
            member.is_admin = 'is_admin' in request.form
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('members.view', member_id=member.id))
    
    return render_template('members/edit.html', member=member)

@members_bp.route('/<int:member_id>/delete', methods=['POST'])
@login_required
def delete(member_id):
    """Delete a member"""
    # Only admins can delete members
    if not current_user.is_admin:
        flash('You do not have permission to delete members.', 'danger')
        return redirect(url_for('index'))
    
    member = Member.query.get_or_404(member_id)
    
    # Check if the member has active loans
    active_loans = [c for c in member.circulations if c.return_date is None]
    if active_loans:
        flash('Cannot delete member. There are active loans for this member.', 'danger')
        return redirect(url_for('members.view', member_id=member.id))
    
    db.session.delete(member)
    db.session.commit()
    
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('members.index'))