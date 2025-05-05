from app.routes.book_routes import books_bp
from app.routes.member_routes import members_bp
from app.routes.circulation_routes import circulation_bp
from app.routes.report_routes import reports_bp

__all__ = ['books_bp', 'members_bp', 'circulation_bp', 'reports_bp']