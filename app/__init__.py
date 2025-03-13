from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'auth.user_login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.auth_routes import auth
    from app.routes.admin_routes import admin
    from app.routes.user_routes import user
    from app.routes.main_routes import main
    
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        from app.models import Admin
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin')
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
    
    return app