# from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
# from fastapi.staticfiles import StaticFiles
# from sqlalchemy.orm import Session
# from typing import List, Optional
# import os
# import shutil
# from pathlib import Path

# from database import get_db, engine
# from model import Base
# from schemas import Todo, TodoCreate, TodoUpdate
# from crud import get_todo, get_todos, create_todo, update_todo, delete_todo

# # Create upload directory
# UPLOAD_DIRECTORY = Path("uploads")
# UPLOAD_DIRECTORY.mkdir(exist_ok=True)

# # Create database tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="Todo API with File Upload",
#     description="A Todo API with FastAPI, PostgreSQL and File Upload",
#     version="2.0.0"
# )

# # Serve static files (uploaded images)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# def save_upload_file(upload_file: UploadFile, todo_id: int) -> str:
#     """Save uploaded file and return the file URL"""
#     # Create file extension
#     file_extension = upload_file.filename.split('.')[-1] if '.' in upload_file.filename else 'jpg'
    
#     # Create filename: todo_{id}_{timestamp}.{extension}
#     import time
#     timestamp = int(time.time())
#     filename = f"todo_{todo_id}_{timestamp}.{file_extension}"
#     file_path = UPLOAD_DIRECTORY / filename
    
#     # Save file
#     with file_path.open("wb") as buffer:
#         shutil.copyfileobj(upload_file.file, buffer)
    
#     return f"/uploads/{filename}"

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to Todo API with File Upload"}

# # Updated POST endpoint with file upload
# @app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
# async def create_new_todo(
#     title: str = Form(...),
#     description: Optional[str] = Form(None),
#     completed: bool = Form(False),
#     image: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     """Create new todo with optional image upload"""
#     todo_data = TodoCreate(
#         title=title,
#         description=description,
#         completed=completed
#     )
    
#     db_todo = create_todo(db=db, todo=todo_data)
    
#     # Handle image upload
#     if image and image.filename:
#         image_url = save_upload_file(image, db_todo.id)
#         db_todo.image_url = image_url
#         db.commit()
#         db.refresh(db_todo)
    
#     return db_todo

# # Updated PUT endpoint with file upload
# @app.put("/todos/{todo_id}", response_model=Todo)
# async def update_existing_todo(
#     todo_id: int,
#     title: Optional[str] = Form(None),
#     description: Optional[str] = Form(None),
#     completed: Optional[bool] = Form(None),
#     image: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     """Update todo with optional image upload"""
#     update_data = {}
#     if title is not None:
#         update_data["title"] = title
#     if description is not None:
#         update_data["description"] = description
#     if completed is not None:
#         update_data["completed"] = completed
    
#     todo_update = TodoUpdate(**update_data)
#     db_todo = update_todo(db, todo_id=todo_id, todo=todo_update)
    
#     if db_todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
    
#     # Handle image upload
#     if image and image.filename:
#         image_url = save_upload_file(image, db_todo.id)
#         db_todo.image_url = image_url
#         db.commit()
#         db.refresh(db_todo)
    
#     return db_todo

# # Keep existing endpoints
# @app.get("/todos/", response_model=List[Todo])
# def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     todos = get_todos(db, skip=skip, limit=limit)
#     return todos

# @app.get("/todos/{todo_id}", response_model=Todo)
# def read_todo(todo_id: int, db: Session = Depends(get_db)):
#     db_todo = get_todo(db, todo_id=todo_id)
#     if db_todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     return db_todo

# @app.delete("/todos/{todo_id}")
# def delete_existing_todo(todo_id: int, db: Session = Depends(get_db)):
#     db_todo = delete_todo(db, todo_id=todo_id)
#     if db_todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
    
#     # Delete associated image file if exists
#     if db_todo.image_url:
#         image_path = UPLOAD_DIRECTORY / db_todo.image_url.split('/')[-1]
#         if image_path.exists():
#             image_path.unlink()
    
#     return {"message": "Todo deleted successfully"}

# # Health check endpoint
# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "message": "Todo API with File Upload is running"}



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

# Configure Cloudinary - REMOVE SECRETS BEFORE COMMITTING TO GITHUB!
cloudinary.config(
    cloud_name="dyo4kbiuq",
    api_key="932226137629113",
    api_secret="LyEC0SVKiDjy8Zj7-ncUd7eCHNk",  # ⚠️ KEEP THIS SECRET!
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
    allow_origins=["*"],  # For development, restrict in production
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
            resource_type="auto"  # Auto-detect image/video
        )
        
        print(f"✅ Image uploaded to Cloudinary: {upload_result['secure_url']}")
        return upload_result["secure_url"]
        
    except Exception as e:
        print(f"❌ Cloudinary upload error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upload image: {str(e)}"
        )

def delete_from_cloudinary(image_url: str):
    """Delete image from Cloudinary"""
    try:
        if image_url and "cloudinary.com" in image_url:
            # Extract public_id from Cloudinary URL
            # URL format: https://res.cloudinary.com/cloud_name/image/upload/v1234567/public_id.jpg
            parts = image_url.split('/')
            filename_with_ext = parts[-1]
            filename = filename_with_ext.split('.')[0]
            public_id = f"todo_app/{filename}"
            
            # Delete from Cloudinary
            result = cloudinary.uploader.destroy(public_id)
            print(f"🗑️ Deleted from Cloudinary: {public_id}, result: {result}")
            
    except Exception as e:
        print(f"⚠️ Failed to delete from Cloudinary: {e}")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Todo API with Cloudinary",
        "version": "3.0.0",
        "docs": "/docs"
    }

@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_new_todo(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    completed: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create new todo with optional Cloudinary image upload"""
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
            # Continue without image - todo is already created
    
    return db_todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_existing_todo(
    todo_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    completed: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update todo with optional Cloudinary image upload"""
    print(f"📝 Updating todo {todo_id}")
    
    # Get existing todo to check for old image
    existing_todo = get_todo(db, todo_id)
    if existing_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Build update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if completed is not None:
        update_data["completed"] = completed
    
    # Update todo in database
    todo_update = TodoUpdate(**update_data)
    db_todo = update_todo(db, todo_id=todo_id, todo=todo_update)
    
    # Handle image upload to Cloudinary
    if image and image.filename:
        try:
            # Validate image file
            if not image.content_type or not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Delete old image from Cloudinary if exists
            if db_todo.image_url:
                delete_from_cloudinary(db_todo.image_url)
            
            # Upload new image to Cloudinary
            image_url = upload_to_cloudinary(image, db_todo.id)
            
            # Update todo with new image URL
            db_todo.image_url = image_url
            db.commit()
            db.refresh(db_todo)
            
            print(f"✅ Todo updated with new image: {db_todo.id}")
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"⚠️ Image update failed: {e}")
            # Continue without updating image
    
    return db_todo

@app.patch("/todos/{todo_id}/toggle", response_model=Todo)
async def toggle_todo_completion(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Toggle todo completion status"""
    db_todo = get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Toggle completion status
    db_todo.completed = not db_todo.completed
    db.commit()
    db.refresh(db_todo)
    
    return db_todo

@app.get("/todos/", response_model=List[Todo])
def read_todos(
    skip: int = 0, 
    limit: int = 100, 
    completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get todos with optional filtering"""
    todos = get_todos(db, skip=skip, limit=limit)
    
    # Filter by completion status if provided
    if completed is not None:
        todos = [todo for todo in todos if todo.completed == completed]
    
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get single todo by ID"""
    db_todo = get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_existing_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete todo and its image from Cloudinary"""
    db_todo = delete_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Delete associated image from Cloudinary if exists
    if db_todo.image_url:
        delete_from_cloudinary(db_todo.image_url)
    
    return {"message": "Todo deleted successfully"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Todo API",
        "timestamp": datetime.now().isoformat(),
        "image_service": "Cloudinary"
    }

@app.get("/cloudinary/test")
def test_cloudinary():
    """Test Cloudinary connection"""
    try:
        # Simple test to check Cloudinary connection
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