from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 在本地项目根目录生成 local_test.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./local_test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()