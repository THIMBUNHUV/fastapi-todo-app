from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path

from database import get_db, engine
from model import Base
from schemas import Todo, TodoCreate, TodoUpdate
from crud import get_todo, get_todos, create_todo, update_todo, delete_todo

# Create upload directory
UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API with File Upload",
    description="A Todo API with FastAPI, PostgreSQL and File Upload",
    version="2.0.0"
)

# Serve static files (uploaded images)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def save_upload_file(upload_file: UploadFile, todo_id: int) -> str:
    """Save uploaded file and return the file URL"""
    # Create file extension
    file_extension = upload_file.filename.split('.')[-1] if '.' in upload_file.filename else 'jpg'
    
    # Create filename: todo_{id}_{timestamp}.{extension}
    import time
    timestamp = int(time.time())
    filename = f"todo_{todo_id}_{timestamp}.{file_extension}"
    file_path = UPLOAD_DIRECTORY / filename
    
    # Save file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return f"/uploads/{filename}"

@app.get("/")
def read_root():
    return {"message": "Welcome to Todo API with File Upload"}

# Updated POST endpoint with file upload
@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_new_todo(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    completed: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create new todo with optional image upload"""
    todo_data = TodoCreate(
        title=title,
        description=description,
        completed=completed
    )
    
    db_todo = create_todo(db=db, todo=todo_data)
    
    # Handle image upload
    if image and image.filename:
        image_url = save_upload_file(image, db_todo.id)
        db_todo.image_url = image_url
        db.commit()
        db.refresh(db_todo)
    
    return db_todo

# Updated PUT endpoint with file upload
@app.put("/todos/{todo_id}", response_model=Todo)
async def update_existing_todo(
    todo_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    completed: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update todo with optional image upload"""
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if completed is not None:
        update_data["completed"] = completed
    
    todo_update = TodoUpdate(**update_data)
    db_todo = update_todo(db, todo_id=todo_id, todo=todo_update)
    
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Handle image upload
    if image and image.filename:
        image_url = save_upload_file(image, db_todo.id)
        db_todo.image_url = image_url
        db.commit()
        db.refresh(db_todo)
    
    return db_todo

# Keep existing endpoints
@app.get("/todos/", response_model=List[Todo])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = get_todos(db, skip=skip, limit=limit)
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_existing_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = delete_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Delete associated image file if exists
    if db_todo.image_url:
        image_path = UPLOAD_DIRECTORY / db_todo.image_url.split('/')[-1]
        if image_path.exists():
            image_path.unlink()
    
    return {"message": "Todo deleted successfully"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Todo API with File Upload is running"}