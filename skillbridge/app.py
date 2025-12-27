"""
Main Flask Application for SkillBridge

This is the entry point of the application.
Demonstrates OOP Concept: APPLICATION FACTORY PATTERN

Author: SkillBridge Team
Purpose: Initialize and configure Flask application
"""

from flask import Flask, render_template
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import get_config
from models import db, User
import os

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")


def create_app(config_name='default'):
    """
    Application Factory Function
    
    OOP Concept: FACTORY PATTERN
    - Creates and configures Flask application instance
    - Allows multiple app instances with different configurations
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application
    """
    
    # Create Flask application instance
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user by ID for Flask-Login
        
        Args:
            user_id (str): User ID
            
        Returns:
            User: User object or None
        """
        return User.query.get(int(user_id))
    
    # Register blueprints (routes)
    from routes import main_bp, auth_bp, service_bp, user_bp, admin_bp, api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(service_bp, url_prefix='/service')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()  # Rollback any failed database transactions
        return render_template('errors/500.html'), 500
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from init_db import create_default_admin, seed_categories
        create_default_admin(app)
        seed_categories()
    
    # Register Socket.IO events
    from events import register_socketio_events
    register_socketio_events(socketio)
    
    return app


if __name__ == '__main__':
    """
    Run the application
    
    This block only executes when running this file directly
    (not when importing as a module)
    """
    
    # Get configuration from environment variable or use default
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create application instance
    app = create_app(config_name)
    
    # Run development server with SocketIO
    # In production, use a WSGI server like Gunicorn or uWSGI
    socketio.run(
        app,
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,        # Port number
        debug=app.config.get('DEBUG', False)
    )
