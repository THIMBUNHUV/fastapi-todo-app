from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# បង្កើត load environment variables
load_dotenv()

# ទទួល database URL ពី .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# បង្កើត database engine
engine = create_engine(DATABASE_URL)

# បង្កើត SessionLocal class សម្រាប់ database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# បង្កើត Base class សម្រាប់ models
Base = declarative_base()

# Dependency function សម្រាប់ get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()