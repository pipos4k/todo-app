# SQLAlchemy ORM Explanation

## What is SQLAlchemy?

SQLAlchemy is an **Object-Relational Mapping (ORM)** library for Python. It lets you work with databases using Python objects instead of writing raw SQL queries.

## How SQLAlchemy Works

### 1. **Models (Python Classes) = Database Tables**

Instead of writing SQL to create tables:
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
```

You define a Python class:
```python
class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
```

### 2. **Python Objects = Database Rows**

Instead of writing SQL to insert data:
```sql
INSERT INTO users (id, email, password_hash) 
VALUES ('user_1', 'test@example.com', 'hash123');
```

You create a Python object:
```python
user = User(id='user_1', email='test@example.com', password_hash='hash123')
db.session.add(user)
db.session.commit()
```

### 3. **Python Queries = SQL Queries**

Instead of writing SQL to query:
```sql
SELECT * FROM users WHERE email = 'test@example.com';
```

You write Python code:
```python
user = User.query.filter_by(email='test@example.com').first()
```

SQLAlchemy **automatically converts** this to SQL!

## Before vs After Comparison

### BEFORE (Raw SQL):
```python
def get_user_by_email(email):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    db_connection.close()
    return dict(row) if row else None
```

### AFTER (SQLAlchemy ORM):
```python
def get_user_by_email(email):
    session = get_db_session()
    user = session.query(User).filter_by(email=email).first()
    return user.to_dict() if user else None
```

**Benefits:**
- ✅ No SQL syntax errors
- ✅ Type safety
- ✅ Easier to read and maintain
- ✅ Automatic SQL generation
- ✅ Database-agnostic (works with PostgreSQL, MySQL, SQLite, etc.)

## Relationships

SQLAlchemy makes relationships easy:

```python
class User(db.Model):
    # One user can have many items
    items = db.relationship('Item', backref='user', lazy=True)

class Item(db.Model):
    # Each item belongs to one user
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
```

Now you can do:
```python
user = User.query.first()
print(user.items)  # Get all items for this user - automatically!

item = Item.query.first()
print(item.user)   # Get the user who owns this item - automatically!
```

## Key SQLAlchemy Concepts

### 1. **Session**
- Manages database transactions
- Tracks changes to objects
- Commits changes to database

### 2. **Query**
- Builds SQL queries from Python code
- Chainable: `User.query.filter_by(...).filter_by(...).all()`

### 3. **Model Methods**
- `to_dict()`: Convert object to dictionary
- `__repr__()`: String representation for debugging

## User-Specific Items

### Answer: YES, each user now has their own items!

**Before:** All items were shared - any user could see all items.

**After:** 
- Each item has a `user_id` foreign key
- Items are filtered by `user_id` in all queries
- Users can only see/modify their own items

**Example:**
```python
# Get all items for user_1
items = Item.query.filter_by(user_id='user_1').all()

# Create item for user_1
item = Item(title='My Task', user_id='user_1')
db.session.add(item)
db.session.commit()
```

## Files Changed

1. **`database/models.py`** - SQLAlchemy models (User, Item)
2. **`database/setup_database.py`** - SQLAlchemy initialization
3. **`repositories/user_repository.py`** - Converted to ORM
4. **`repositories/todo_repository.py`** - Converted to ORM with user filtering
5. **`services/todo_service.py`** - Added user_id parameter
6. **`todo_app.py`** - Added user authentication to routes
7. **`requirements.txt`** - Added Flask-SQLAlchemy and SQLAlchemy

## Installation

Run:
```bash
pip install -r requirements.txt
```

This will install:
- `Flask-SQLAlchemy==3.1.1` - Flask integration for SQLAlchemy
- `SQLAlchemy==2.0.23` - The ORM library itself
