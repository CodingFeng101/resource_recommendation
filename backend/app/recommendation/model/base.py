from uuid import uuid4

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def uuid4_str() -> str:
    """数据库引擎 UUID 类型兼容性解决方案"""
    return str(uuid4())