from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# ឥឡូវនេះប្រើ direct imports
from database import get_db, engine
from model import Base
from schemas import Todo, TodoCreate, TodoUpdate
from crud import get_todo, get_todos, create_todo, update_todo, delete_todo

# បង្កើត database tables
Base.metadata.create_all(bind=engine)

# បង្កើត FastAPI application instance
app = FastAPI(
    title="Todo API",
    description="A simple Todo API with FastAPI and PostgreSQL",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """Root endpoint សម្រាប់ test"""
    return {"message": "Welcome to Todo API"}

@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_new_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """POST endpoint សម្រាប់បង្កើត todo ថ្មី"""
    return create_todo(db=db, todo=todo)

@app.get("/todos/", response_model=List[Todo])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """GET endpoint សម្រាប់យក todos ទាំងអស់"""
    todos = get_todos(db, skip=skip, limit=limit)
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    """GET endpoint សម្រាប់យក todo តាម ID"""
    db_todo = get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_existing_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    """PUT endpoint សម្រាប់ធ្វើបច្ចុប្បន្នភាព todo"""
    db_todo = update_todo(db, todo_id=todo_id, todo=todo)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_existing_todo(todo_id: int, db: Session = Depends(get_db)):
    """DELETE endpoint សម្រាប់លុប todo"""
    db_todo = delete_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}