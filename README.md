# Simple CRUD App with Flask

This is a basic backend CRUD application built with Flask for the **DevReady Bootcamp**!

## What it does

- **Create** new items
- **Read** and view existing items
- **Update** items
- **Delete** items

Basically, it's a simple todo list manager where you can add, update, delete, and view items through a REST API.

## API Endpoints

- `GET /items` - Get all items
- `GET /items/<item_id>` - Get a specific item by ID
- `GET /items?status=<status>` - Filter items by status (ToDo, InProgress, Done)
- `POST /items` - Create a new item
- `PUT /items/<item_id>` - Update an item
- `DELETE /items/<item_id>` - Delete an item

### Example Requests

**Create an item:**
```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "From the store", "status": "ToDo"}'
```

**Get all items:**
```bash
curl http://localhost:5000/items
```

**Update an item:**
```bash
curl -X PUT http://localhost:5000/items/item_1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Done"}'
```

## What I used

- **Python** - Backend language
- **Flask** - Web framework
- **PostgreSQL** - Database (upgraded from SQLite!)
- **Docker** - For running everything in containers

## How to run it

### Setup

1. Clone the repo:
```bash
git clone https://github.com/pipos4k/todo-app.git
cd todo-app
```

2. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Edit `.env` if you want different database credentials (optional)

### Start the app

With Docker:
```bash
docker compose up --build
```

The API will be running at http://localhost:5000

### Stop the app
```bash
docker compose down
```

## Database

The app uses **PostgreSQL** running in a Docker container. No need to install something locally!

## Note

This is my first bootcamp project, so feedback is welcome! I'm still learning and trying to improve. 🚀

If you find any bugs or have suggestions, feel free to open an issue!📨
