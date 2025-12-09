# Simple CRUD App with Flask

This is a basic backend CRUD application built with Flask for the **DevReady Bootcamp**!

## What it does

- **Create** new items
- **Read** and view existing items  
- **Update** and **Delete** will come soon!

## API Endpoints

- `GET /items` - Get all items as JSON
- `GET /items/<id>` - Get specific item by ID 
- `GET /items?status=<status>` - Filter items by status - "status": 'ToDo', 'InProgress', 'Done'
- `POST /post_item` - Form data with `title`, `description`, `status`
 
Basically, it's a simple list manager where you can add and view items.

## What I used

- Python
- Flask
- HTML/CSS
- Docker
- SQLite
  
## How to run it
### With docker
1. Clone the repo on your machine. <br/>
`git clone https://github.com/pipos4k/todo-app.git`
2. Navigate to the project. <br/>
`cd todo-app`
3. Build and run with docker compose <br/>
`docker compose up --build`
4. Open http://localhost:5000 in your browser

## Note

This is my first bootcamp project so... Feedback is welcome!
