from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from datetime import datetime

from database import get_db, engine
from model import Base
from schemas import Todo, TodoCreate, TodoUpdate
from crud import get_todo, get_todos, create_todo, update_todo, delete_todo

# Configure Cloudinary
cloudinary.config(
    cloud_name="dyo4kbiuq",
    api_key="932226137629113",
    api_secret="LyEC0SVKiDjy8Zj7-ncUd7eCHNk",
    secure=True
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API with Cloudinary",
    description="A Todo API with FastAPI, PostgreSQL and Cloudinary Image Upload",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def upload_to_cloudinary(file: UploadFile, todo_id: int) -> str:
    """Upload file to Cloudinary and return URL"""
    try:
        # Generate unique public ID
        timestamp = int(datetime.now().timestamp())
        public_id = f"todo_{todo_id}_{timestamp}"
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder="todo_app",
            public_id=public_id,
            overwrite=True,
            resource_type="auto"
        )
        
        print(f"✅ Image uploaded to Cloudinary: {upload_result['secure_url']}")
        return upload_result["secure_url"]
        
    except Exception as e:
        print(f"❌ Cloudinary upload error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upload image: {str(e)}"
        )

@app.get("/")
def read_root():
    return {"message": "Welcome to Todo API with Cloudinary"}

# POST endpoint with Cloudinary
@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_new_todo(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    completed: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create new todo with Cloudinary image upload"""
    print(f"📝 Creating todo: {title}")
    
    # Create todo data
    todo_data = TodoCreate(
        title=title,
        description=description,
        completed=completed
    )
    
    # Create todo in database
    db_todo = create_todo(db=db, todo=todo_data)
    
    # Handle image upload to Cloudinary
    if image and image.filename:
        try:
            # Validate image file
            if not image.content_type or not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Upload to Cloudinary
            image_url = upload_to_cloudinary(image, db_todo.id)
            
            # Update todo with image URL
            db_todo.image_url = image_url
            db.commit()
            db.refresh(db_todo)
            
            print(f"✅ Todo created with image: {db_todo.id}")
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"⚠️ Image upload failed but todo created: {e}")
            # Continue without image
    
    return db_todo

# PUT endpoint with Cloudinary
@app.put("/todos/{todo_id}", response_model=Todo)
async def update_existing_todo(
    todo_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    completed: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update todo with Cloudinary image upload"""
    print(f"📝 Updating todo {todo_id}")
    print(f"📝 Data received - title: {title}, completed: {completed}")
    
    # Build update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if completed is not None:
        # Handle string "true"/"false" conversion
        if isinstance(completed, str):
            completed = completed.lower() == "true"
        update_data["completed"] = completed
        print(f"✅ Will update completed to: {completed}")
    
    print(f"📝 Final update data: {update_data}")
    
    # Update todo in database
    todo_update = TodoUpdate(**update_data)
    db_todo = update_todo(db, todo_id=todo_id, todo=todo_update)
    
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    print(f"✅ Database update successful. Todo completed: {db_todo.completed}")
    
    # Handle image upload to Cloudinary
    if image and image.filename:
        try:
            # Validate image file
            if not image.content_type or not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Upload to Cloudinary
            image_url = upload_to_cloudinary(image, db_todo.id)
            
            # Update todo with image URL
            db_todo.image_url = image_url
            db.commit()
            db.refresh(db_todo)
            
            print(f"✅ Todo updated with new image: {db_todo.id}")
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"⚠️ Image update failed: {e}")
    
    return db_todo

# Keep other endpoints
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
    return {"message": "Todo deleted successfully"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Todo API with Cloudinary is running"}

@app.get("/cloudinary/test")
def test_cloudinary():
    """Test Cloudinary connection"""
    try:
        result = cloudinary.api.ping()
        return {
            "status": "connected",
            "cloudinary": result,
            "cloud_name": cloudinary.config().cloud_name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }