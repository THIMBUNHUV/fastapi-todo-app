from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from database import Base  # ប្រើ relative import

class Todo(Base):
    __tablename__ = "todos"  # ឈ្មោះ table ក្នុង database
    
    # Columns នៅក្នុង table
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)  # ឈ្មោះ todo អតិបរមា 100 characters
    description = Column(Text)  # ការពិពណ៌នា todo
    completed = Column(Boolean, default=False)  # ស្ថានភាព (ធ្វើរួច/មិនទាន់ធ្វើរួច)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # ពេលវេលាបង្កើត
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # ពេលវេលាធ្វើបច្ចុប្បន្នភាព