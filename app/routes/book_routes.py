from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.book import Book

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def index():
    """List all books in the catalog"""
    books = Book.query.all()
    return render_template('books/index.html', books=books)

@books_bp.route('/<int:book_id>')
def view(book_id):
    """View a specific book's details"""
    book = Book.query.get_or_404(book_id)
    return render_template('books/view.html', book=book)

@books_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new book to the catalog"""
    if request.method == 'POST':
        # Extract form data
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        publication_year = request.form.get('publication_year')
        description = request.form.get('description')
        category = request.form.get('category')
        language = request.form.get('language')
        pages = request.form.get('pages')
        quantity = int(request.form.get('quantity', 1))
        location_shelf = request.form.get('location_shelf')
        
        # Create new book
        new_book = Book(
            title=title,
            author=author,
            isbn=isbn,
            publisher=publisher,
            publication_year=publication_year,
            description=description,
            category=category,
            language=language,
            pages=pages,
            quantity=quantity,
            available_quantity=quantity,
            location_shelf=location_shelf
        )
        
        # Save to database
        db.session.add(new_book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('books.view', book_id=new_book.id))
    
    return render_template('books/add.html')

@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    """Edit an existing book"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        # Update book details
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.isbn = request.form.get('isbn')
        book.publisher = request.form.get('publisher')
        book.publication_year = request.form.get('publication_year')
        book.description = request.form.get('description')
        book.category = request.form.get('category')
        book.language = request.form.get('language')
        book.pages = request.form.get('pages')
        
        new_quantity = int(request.form.get('quantity', 1))
        quantity_diff = new_quantity - book.quantity
        book.quantity = new_quantity
        book.available_quantity += quantity_diff
        
        book.location_shelf = request.form.get('location_shelf')
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books.view', book_id=book.id))
    
    return render_template('books/edit.html', book=book)

@books_bp.route('/<int:book_id>/delete', methods=['POST'])
def delete(book_id):
    """Delete a book from the catalog"""
    book = Book.query.get_or_404(book_id)
    
    # Check if the book can be deleted (no active loans)
    active_loans = [c for c in book.circulations if c.return_date is None]
    if active_loans:
        flash('Cannot delete book. There are active loans for this book.', 'danger')
        return redirect(url_for('books.view', book_id=book.id))
    
    db.session.delete(book)
    db.session.commit()
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books.index'))

@books_bp.route('/search')
def search():
    """Search for books by various criteria"""
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    
    # Build the search query
    search_query = Book.query
    
    if query:
        search_query = search_query.filter(
            (Book.title.ilike(f'%{query}%')) | 
            (Book.author.ilike(f'%{query}%')) | 
            (Book.isbn.ilike(f'%{query}%'))
        )
    
    if category:
        search_query = search_query.filter(Book.category == category)
    
    books = search_query.all()
    return render_template('books/search.html', books=books, query=query, category=category)