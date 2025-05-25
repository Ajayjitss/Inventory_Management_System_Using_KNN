from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from flask_apscheduler import APScheduler  # Import APScheduler
from datetime import datetime

# Initialize the database, login manager, and migrate object
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# Initialize the APScheduler
scheduler = APScheduler()

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))

    # Secret key for session management and CSRF protection
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure the LoginManager
    login_manager.login_view = "users.login_view"  
    login_manager.login_message = "Please log in to access this page."  

    # Initialize the extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # Set the user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return users.User.query.get(int(user_id))
    
    # Register blueprints
    from .users import users_bp
    from .inventory import inventory_bp
    from .customer import customer_bp
    from .sales import sales_bp

    # Register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(customer_bp, url_prefix='/customer_bp')
    app.register_blueprint(sales_bp, url_prefix='/sales')

    # Initialize the scheduler
    from app.inventory.utils import update_inventory_predictions

    # Init APScheduler
    scheduler.init_app(app)

    def run_update_with_app_context(app):
        with app.app_context():
            update_inventory_predictions()

    # Register the job
    scheduler.add_job(
        func=run_update_with_app_context,
        args=[app],
        trigger='interval',
        minutes=1,
        id='update_inventory',
        replace_existing=True
    )
   

    print("Scheduler job has been added.")
    scheduler.start()



    return app
