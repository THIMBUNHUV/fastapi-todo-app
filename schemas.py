# from pydantic import BaseModel, ConfigDict
# from datetime import datetime
# from typing import Optional

# # Base schema សម្រាប់ Todo ទាំងអស់
# class TodoBase(BaseModel):
#     title: str
#     description: Optional[str] = None
#     completed: bool = False

# # Schema សម្រាប់ការបង្កើត Todo ថ្មី
# class TodoCreate(TodoBase):
#     pass

# # Schema សម្រាប់ការធ្វើបច្ចុប្បន្នភាព Todo
# class TodoUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     completed: Optional[bool] = None

# # Schema សម្រាប់ response (រួមមាន id និង timestamps)
# class Todo(TodoBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime
    
#     # កែសម្រួលសម្រាប់ Pydantic V2
#     model_config = ConfigDict(from_attributes=True)



from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    image_url: Optional[str] = None  # New field

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    image_url: Optional[str] = None  # New field

class Todo(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)