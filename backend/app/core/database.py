# backend/app/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 动态获取当前项目的根目录: app/core/ -> app/ -> backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 确保 data 目录存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "deepblue.db")

# 💡 核心修复：将 Windows 下的反斜杠 \ 全部替换为正斜杠 /
# 否则 SQLAlchemy 会解析出错，导致数据库存入虚无的空间
abs_db_path = os.path.abspath(DB_PATH).replace('\\', '/')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{abs_db_path}"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()