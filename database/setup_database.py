import os
import logging
from database.models import db
from sqlalchemy import text, inspect

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

def migrate_add_user_id_column(app) -> bool:
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)

            if "items" not in inspector.get_table_names():
                logger.info("Items table doesn't exist yet, will be created by create_all()")
                return True
                
            columns = [col['name'] for col in inspector.get_columns('items')]
            if "user_id" in columns:
                logger.info("user_id column already exists in table.")
                return True
                        
            logger.info("Adding user_id column to items table...")

            if "user_id" not in columns:
                with db.engine.connect() as conn:
                    
                    result = conn.execute(text("SELECT COUNT(*) FROM items"))
                    item_count = result.scalar()

                    if item_count > 0:
                        logger.warning(f"Warning: Found {item_count} existing items without user_id.")
                        logger.info("Deleting existing items (they don't have user_id and can't be assigned).")

                    conn.execute(text("ALTER TABLE items ADD COLUMN user_id VARCHAR(36)"))

                    try:
                        conn.execute(text("""
                            ALTER TABLE items 
                            ADD CONSTRAINT items_user_id_fkey
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            ON DELETE CASCADE
                            """))
                        logger.info("Foreign key constraing added successfully.")
                    except Exception as fk_error:
                        logger.warning(f"Could not add foreign key constraint: {fk_error}")

                    logger.info("user_id column added successfully!")
                    return True

        except Exception as e:
            logger.error(f"Error in migration: {str(e)}")
            return False

def init_db(app) -> None:

    # Configure Flask app to use the database
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)
    
    # Create all tables defined in models
    with app.app_context():
        db.create_all()
        logger.info("Database tables created.")
        
        # Run migration to add user_id column if needed
        if migrate_add_user_id_column(app):    
            logger.info("Database initialized successfully with SQLAlchemy!")
        else:
            logger.error("Database migration failed!")

def get_db_session():

    return db.session
    
def check_database_connection() -> bool:

    try:
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False