import os
from database.models import db, User, Item
from sqlalchemy import text, inspect

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

def migrate_add_user_id_column(app):
    """
    Migration: Add user_id column to items table if it doesn't exist.
    This handles the case where the items table was created before user_id was added.
    """
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            # Check if items table exists
            if 'items' not in inspector.get_table_names():
                print("Items table doesn't exist yet, will be created by create_all()")
                return
                
            columns = [col['name'] for col in inspector.get_columns('items')]
            
            if 'user_id' not in columns:
                print("Adding user_id column to items table...")
                with db.engine.connect() as conn:
                    # Check if there are any existing items
                    result = conn.execute(text("SELECT COUNT(*) FROM items"))
                    item_count = result.scalar()
                    
                    if item_count > 0:
                        print(f"Warning: Found {item_count} existing items without user_id.")
                        print("Deleting existing items (they don't have user_id and can't be assigned).")
                        # Delete existing items since they can't have a user_id
                        conn.execute(text("DELETE FROM items"))
                    
                    # Add the column (nullable first)
                    conn.execute(text("ALTER TABLE items ADD COLUMN user_id TEXT"))
                    conn.commit()
                    
                    # Now add the foreign key constraint
                    try:
                        conn.execute(text(
                            "ALTER TABLE items ADD CONSTRAINT items_user_id_fkey "
                            "FOREIGN KEY (user_id) REFERENCES users(id)"
                        ))
                        conn.commit()
                    except Exception as fk_error:
                        print(f"Note: Could not add foreign key constraint: {fk_error}")
                        # Continue anyway
                    
                    # Make it NOT NULL (since we deleted old items)
                    conn.execute(text("ALTER TABLE items ALTER COLUMN user_id SET NOT NULL"))
                    conn.commit()
                    print("user_id column added successfully!")
            else:
                print("user_id column already exists in items table.")
        except Exception as e:
            print(f"Error in migration: {str(e)}")
            # If there's an error, try to continue - the column might already exist
            import traceback
            traceback.print_exc()

def init_db(app):
    """
    Initialize the database with SQLAlchemy.
    This replaces raw SQL with ORM (Object-Relational Mapping).
    
    How SQLAlchemy works:
    1. Models (User, Item) define the database structure as Python classes
    2. SQLAlchemy automatically generates SQL queries from Python code
    3. You work with Python objects instead of writing SQL directly
    4. Relationships (like user.items) are handled automatically
    """
    # Configure Flask app to use the database
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)
    
    # Create all tables defined in models
    with app.app_context():
        db.create_all()
        
        # Run migration to add user_id column if needed
        migrate_add_user_id_column(app)
        
        print("Database initialized successfully with SQLAlchemy!")

def get_db_session():
    """
    Get a database session for performing operations.
    Sessions manage transactions and object states.
    """
    return db.session
