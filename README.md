# FastTodo
FastTodo is a full-stack Todo application built with FastAPI (Python) that allows users to create, update, complete, and delete tasks through a clean web interface. The backend exposes 6 RESTful endpoints with Pydantic data validation and UUID-based IDs, while tasks are permanently stored in an SQLite database that survives server restarts. Auto-generated Swagger API documentation is available at /docs for testing all endpoints interactively.

## Features
FastTodo offers a complete set of features for managing tasks efficiently. Users can add new tasks with a title and an optional description, mark them as completed, and delete them individually or all at once. Every task is saved permanently in an SQLite database file, so no data is lost even after the server restarts. The homepage displays a live counter showing the total, pending, and completed task counts at a glance.

## Technology used
Backend — FastAPI, Uvicorn, Pydantic
Database — SQLite, sqlite3
Frontend — HTML, CSS, Vanilla JavaScript
Tools — Swagger UI, DB Browser for SQLite

## Future Scope
FastTodo has significant potential for growth and can be extended in multiple directions. The most immediate improvement would be replacing the current SQLite database with a production-grade database like PostgreSQL or MySQL using SQLAlchemy as an ORM, making it capable of handling large amounts of data and multiple simultaneous users efficiently.
