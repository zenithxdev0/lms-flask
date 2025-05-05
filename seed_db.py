"""
Database Seed Script for Bibliotheca Library Management System

This script populates the database with test data including:
- Sample books
- Library members (regular and admin)
- Circulation records (active loans and returned books)

Run this script after setting up the database:
$ python seed_db.py
"""

import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import Flask
from app import create_app, db
from app.models.book import Book
from app.models.member import Member
from app.models.circulation import Circulation

# Create Flask app context for database operations
app = create_app()

# Constants for circulation
MAX_LOAN_DAYS = 14  # Set this to match what should be in Config
FINE_PER_DAY = 0.25  # 25 cents per day overdue

# Sample books data - Title, Author, ISBN, Publisher, Year, Category
BOOKS = [
    ('To Kill a Mockingbird', 'Harper Lee', '9780060935467', 'HarperCollins', 1960, 'Fiction'),
    ('1984', 'George Orwell', '9780451524935', 'Signet Classic', 1949, 'Science Fiction'),
    ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'Scribner', 1925, 'Fiction'),
    ('Pride and Prejudice', 'Jane Austen', '9780141439518', 'Penguin Classics', 1813, 'Romance'),
    ('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 'Houghton Mifflin', 1937, 'Fantasy'),
    ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', '9780590353427', 'Scholastic', 1997, 'Fantasy'),
    ('The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 'Little, Brown', 1951, 'Fiction'),
    ('Lord of the Flies', 'William Golding', '9780399501487', 'Perigee', 1954, 'Fiction'),
    ('Animal Farm', 'George Orwell', '9780451526342', 'Signet Classics', 1945, 'Political Fiction'),
    ('The Da Vinci Code', 'Dan Brown', '9780307474278', 'Anchor', 2003, 'Mystery'),
    ('The Alchemist', 'Paulo Coelho', '9780061122415', 'HarperOne', 1988, 'Fiction'),
    ('Brave New World', 'Aldous Huxley', '9780060850524', 'Harper Perennial', 1932, 'Science Fiction'),
    ('The Hunger Games', 'Suzanne Collins', '9780439023528', 'Scholastic Press', 2008, 'Young Adult'),
    ('The Shining', 'Stephen King', '9780307743657', 'Anchor', 1977, 'Horror'),
    ('The Lord of the Rings', 'J.R.R. Tolkien', '9780618640157', 'Mariner Books', 1954, 'Fantasy'),
    # Additional books
    ('Dune', 'Frank Herbert', '9780441172719', 'Ace Books', 1965, 'Science Fiction'),
    ('The Road', 'Cormac McCarthy', '9780307387899', 'Vintage', 2006, 'Post-Apocalyptic'),
    ('The Kite Runner', 'Khaled Hosseini', '9781594631931', 'Riverhead Books', 2003, 'Historical Fiction'),
    ('The Girl with the Dragon Tattoo', 'Stieg Larsson', '9780307454546', 'Vintage Crime', 2005, 'Mystery'),
    ('The Fault in Our Stars', 'John Green', '9780142424179', 'Penguin Books', 2012, 'Young Adult'),
    ('A Game of Thrones', 'George R.R. Martin', '9780553593716', 'Bantam', 1996, 'Fantasy'),
    ('The Hitchhiker\'s Guide to the Galaxy', 'Douglas Adams', '9780345391803', 'Del Rey', 1979, 'Science Fiction'),
    ('The Handmaid\'s Tale', 'Margaret Atwood', '9780385490818', 'Anchor', 1985, 'Dystopian'),
    ('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', '9780062316097', 'Harper', 2014, 'Non-Fiction'),
    ('The Giver', 'Lois Lowry', '9780544336261', 'HMH Books', 1993, 'Dystopian'),
    ('The Martian', 'Andy Weir', '9780553418026', 'Broadway Books', 2014, 'Science Fiction'),
    ('Ready Player One', 'Ernest Cline', '9780307887443', 'Broadway Books', 2011, 'Science Fiction'),
    ('The Silent Patient', 'Alex Michaelides', '9781250301697', 'Celadon Books', 2019, 'Psychological Thriller'),
    ('Where the Crawdads Sing', 'Delia Owens', '9780735219090', 'G.P. Putnam\'s Sons', 2018, 'Mystery'),
    ('Educated', 'Tara Westover', '9780399590504', 'Random House', 2018, 'Memoir'),
    ('Atomic Habits', 'James Clear', '9780735211292', 'Avery', 2018, 'Self-Help'),
    ('The Power of Now', 'Eckhart Tolle', '9781577314806', 'New World Library', 1997, 'Spirituality'),
    ('The Night Circus', 'Erin Morgenstern', '9780307744432', 'Anchor', 2011, 'Fantasy'),
    ('Norse Mythology', 'Neil Gaiman', '9780393356182', 'W. W. Norton & Company', 2017, 'Mythology'),
    ('Becoming', 'Michelle Obama', '9781524763138', 'Crown', 2018, 'Autobiography')
]

# Sample member data - First Name, Last Name, Email, Password, Is Admin
MEMBERS = [
    ('Admin', 'User', 'admin@example.com', 'admin123', True),
    ('John', 'Doe', 'john@example.com', 'password123', False),
    ('Jane', 'Smith', 'jane@example.com', 'password123', False),
    ('Bob', 'Johnson', 'bob@example.com', 'password123', False),
    ('Alice', 'Williams', 'alice@example.com', 'password123', False),
    ('Michael', 'Brown', 'michael@example.com', 'password123', False)
]

def seed_database():
    """Seed the database with sample data"""
    with app.app_context():
        print("Starting database seeding...")
        
        # Clear existing data
        print("Clearing existing data...")
        Circulation.query.delete()
        Book.query.delete()
        Member.query.delete()
        db.session.commit()
        
        # Add books
        print("Adding sample books...")
        books = []
        for title, author, isbn, publisher, year, category in BOOKS:
            book = Book(
                title=title,
                author=author,
                isbn=isbn,
                publisher=publisher,
                publication_year=year,
                category=category,
                description=f"Sample description for {title} by {author}.",
                language="English",
                pages=random.randint(200, 600),
                quantity=random.randint(1, 5),
                available_quantity=random.randint(0, 3),  # Will be updated based on circulation
                location_shelf=f"{category[0]}-{random.randint(1, 9)}"
            )
            db.session.add(book)
            books.append(book)
        
        # Add members
        print("Adding sample members...")
        members = []
        for idx, (first, last, email, password, is_admin) in enumerate(MEMBERS):
            member = Member(
                member_id=f"LIB-{str(idx+1001).zfill(4)}",
                first_name=first,
                last_name=last,
                email=email,
                password_hash=generate_password_hash(password),
                phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                address=f"{random.randint(100, 999)} Sample St, Sample City",
                is_admin=is_admin
            )
            db.session.add(member)
            members.append(member)
        
        # Commit to get IDs
        db.session.commit()
        
        # Reset available quantities to match actual quantity before creating circulation records
        for book in books:
            book.available_quantity = book.quantity
        
        # Add circulation records (both active and returned)
        print("Adding sample circulation records...")
        now = datetime.now()  # Using now() instead of utcnow() to avoid deprecation warning
        
        # Active loans (not returned yet)
        for _ in range(8):
            book = random.choice(books)
            if book.available_quantity > 0:
                member = random.choice(members)
                checkout_date = now - timedelta(days=random.randint(1, 20))
                # Create circulation record without relying on __init__ method
                circulation = Circulation(
                    book_id=book.id,
                    member_id=member.id,
                    checkout_date=checkout_date
                )
                # Manually set the due date instead of relying on Config
                circulation.due_date = checkout_date + timedelta(days=MAX_LOAN_DAYS)
                
                db.session.add(circulation)
                book.available_quantity -= 1  # Update book availability
        
        # Returned books with history
        for _ in range(15):
            book = random.choice(books)
            member = random.choice(members)
            days_ago = random.randint(30, 120)
            checkout_date = now - timedelta(days=days_ago)
            due_date = checkout_date + timedelta(days=14)  # Standard loan period
            return_date = due_date + timedelta(days=random.randint(-7, 10))  # Some returned early, some late
            
            # Create circulation record without relying on __init__ method
            circulation = Circulation(
                book_id=book.id,
                member_id=member.id,
                checkout_date=checkout_date
            )
            circulation.due_date = due_date
            circulation.return_date = return_date
            
            # Calculate fine for overdue returns
            if return_date > due_date:
                days_overdue = (return_date - due_date).days
                fine_amount = days_overdue * FINE_PER_DAY
                circulation.fine_amount = fine_amount
                circulation.fine_paid = random.choice([True, False])
            
            db.session.add(circulation)
        
        # Commit all circulation records
        db.session.commit()
        
        print("Database seeding completed successfully!")
        print(f"Added {len(books)} books, {len(members)} members, and multiple circulation records.")
        print("\nSample login credentials:")
        print("Admin User: admin@example.com / admin123")
        print("Regular User: john@example.com / password123")

if __name__ == "__main__":
    seed_database()