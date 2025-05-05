import os
from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

# Import models to ensure they're recognized by Alembic
from app.models.book import Book
from app.models.member import Member
from app.models.circulation import Circulation

# Create a CLI context for Flask commands like flask db migrate
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'Book': Book, 
        'Member': Member, 
        'Circulation': Circulation
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)