from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

from app.config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Update login view to use members blueprint
    login_manager.login_view = 'members.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.routes.book_routes import books_bp
    from app.routes.member_routes import members_bp
    from app.routes.circulation_routes import circulation_bp
    from app.routes.report_routes import reports_bp

    app.register_blueprint(books_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(circulation_bp)
    app.register_blueprint(reports_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        # Initialize empty stats dictionary
        stats = {}
        
        # Add dashboard statistics if user is an admin
        if current_user.is_authenticated and current_user.is_admin:
            from app.models.book import Book
            from app.models.member import Member
            from app.models.circulation import Circulation
            from sqlalchemy import func
            from datetime import datetime
            
            # Collect stats for admin dashboard
            stats['total_books'] = db.session.query(func.sum(Book.quantity)).scalar() or 0
            stats['total_members'] = Member.query.count()
            stats['active_loans'] = Circulation.query.filter(Circulation.return_date.is_(None)).count()
            stats['overdue_loans'] = Circulation.query.filter(
                Circulation.return_date.is_(None),
                Circulation.due_date < datetime.utcnow()
            ).count()
        
        # Render the homepage with stats
        return render_template('index.html', **stats)

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app