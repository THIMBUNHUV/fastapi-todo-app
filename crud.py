from sqlalchemy.orm import Session
from model import Todo  # ប្រើ relative import
from schemas import TodoCreate, TodoUpdate  # ប្រើ relative import

def get_todo(db: Session, todo_id: int):
    """យក todo តាម ID"""
    return db.query(Todo).filter(Todo.id == todo_id).first()

def get_todos(db: Session, skip: int = 0, limit: int = 100):
    """យក todos ទាំងអស់ (with pagination)"""
    return db.query(Todo).offset(skip).limit(limit).all()

def create_todo(db: Session, todo: TodoCreate):
    """បង្កើត todo ថ្មី"""
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed
    )
    db.add(db_todo)  # បន្ថែម todo ថ្មីទៅក្នុង session
    db.commit()  # បញ្ជូន changes ទៅ database
    db.refresh(db_todo)  # ទាញយក data ថ្មីពី database
    return db_todo

def update_todo(db: Session, todo_id: int, todo: TodoUpdate):
    """ធ្វើបច្ចុប្បន្នភាព todo"""
    db_todo = get_todo(db, todo_id)
    if db_todo:
        update_data = todo.dict(exclude_unset=True)  # យកតែ fields ដែលត្រូវ update
        for field, value in update_data.items():
            setattr(db_todo, field, value)  # កំណត់តម្លៃថ្មី
        db.commit()
        db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int):
    """លុប todo"""
    db_todo = get_todo(db, todo_id)
    if db_todo:
        db.delete(db_todo)  # លុប todo ពី session
        db.commit()  # បញ្ជូន changes ទៅ database
    return db_todo