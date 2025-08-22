#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from backend.app.recommendation.model.model import Base
from backend.core.config import settings

# 异步数据库引擎（MySQL）
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"ssl": False},  # 禁用SSL连接
)

# 异步会话工厂
async_db_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# 同步数据库引擎（用于创建表等操作）
sync_engine = create_engine(
    settings.database_url.replace("mysql+asyncmy://", "mysql+pymysql://"),
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
)

# 同步会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# 创建所有表
async def create_tables():
    """创建数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 依赖注入函数
async def get_async_db():
    """获取异步数据库会话"""
    async with async_db_session() as session:
        try:
            yield session
        finally:
            await session.close()

def get_db():
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()