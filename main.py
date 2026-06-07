# main.py - FastAPI Todo App with SQLite Database
# Run with: uvicorn main:app --reload

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import sqlite3

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="Todo API",
    description="A simple Todo REST API built with FastAPI + SQLite",
    version="2.0.0"
)

DATABASE = "todos.db"  # This file appears in your project folder


# ─────────────────────────────────────────────
# Database Setup
# ─────────────────────────────────────────────
def get_db():
    """Create a new database connection for each request"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name (row["title"])
    return conn


def init_db():
    """Create the todos table if it doesn't exist yet"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            description TEXT,
            completed   INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# Create table when app starts
init_db()


# ─────────────────────────────────────────────
# Pydantic Models (Data Validation)
# ─────────────────────────────────────────────
class TodoCreate(BaseModel):
    """Model used when CREATING a new todo"""
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    """Model used when UPDATING an existing todo"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    """Full todo model returned in responses"""
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False


# ─────────────────────────────────────────────
# Helper: convert sqlite3.Row → Todo
# ─────────────────────────────────────────────
def row_to_todo(row) -> Todo:
    return Todo(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"])  # SQLite stores 0/1, convert to True/False
    )


# ─────────────────────────────────────────────
# Routes / Endpoints
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the frontend UI"""
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/todos", response_model=list[Todo], tags=["Todos"])
async def get_all_todos():
    """Get ALL todos from the database"""
    conn = get_db()
    rows = conn.execute("SELECT * FROM todos").fetchall()
    conn.close()
    return [row_to_todo(r) for r in rows]


@app.get("/todos/{todo_id}", response_model=Todo, tags=["Todos"])
async def get_todo(todo_id: str):
    """Get a SINGLE todo by its ID"""
    conn = get_db()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return row_to_todo(row)


@app.post("/todos", response_model=Todo, status_code=201, tags=["Todos"])
async def create_todo(todo: TodoCreate):
    """CREATE a new todo and save it to SQLite"""
    new_id = str(uuid.uuid4())

    conn = get_db()
    conn.execute(
        "INSERT INTO todos (id, title, description, completed) VALUES (?, ?, ?, ?)",
        (new_id, todo.title, todo.description, 0)
    )
    conn.commit()
    conn.close()

    return Todo(id=new_id, title=todo.title, description=todo.description, completed=False)


@app.put("/todos/{todo_id}", response_model=Todo, tags=["Todos"])
async def update_todo(todo_id: str, updates: TodoUpdate):
    """UPDATE an existing todo (partial update — only send what you want to change)"""
    conn = get_db()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    # Keep existing values if not provided in update
    new_title       = updates.title       if updates.title       is not None else row["title"]
    new_description = updates.description if updates.description is not None else row["description"]
    new_completed   = updates.completed   if updates.completed   is not None else bool(row["completed"])

    conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (new_title, new_description, int(new_completed), todo_id)
    )
    conn.commit()
    conn.close()

    return Todo(id=todo_id, title=new_title, description=new_description, completed=new_completed)


@app.delete("/todos/{todo_id}", tags=["Todos"])
async def delete_todo(todo_id: str):
    """DELETE a single todo by ID"""
    conn = get_db()
    row = conn.execute("SELECT id FROM todos WHERE id = ?", (todo_id,)).fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": "Todo deleted successfully"}


@app.delete("/todos", tags=["Todos"])
async def delete_all_todos():
    """DELETE all todos"""
    conn = get_db()
    conn.execute("DELETE FROM todos")
    conn.commit()
    conn.close()
    return {"message": "All todos deleted"}
