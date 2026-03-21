# backend/app/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 动态获取当前项目的根目录 (当前文件在 backend/app/core/，所以需要向上跳三级回到 backend/)
# 第一级: app/core/
# 第二级: app/
# 第三级: backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 确保 data 目录存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# 关键修复：SQLite 路径处理
DB_PATH = os.path.join(DATA_DIR, "deepblue.db")
# 统一使用绝对路径，避免 Windows 下的路径斜杠问题
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

# 创建引擎，check_same_thread=False 是 SQLite 在 FastAPI(多线程) 中必须的
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