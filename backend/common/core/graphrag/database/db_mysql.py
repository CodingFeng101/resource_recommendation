#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
import sys
from uuid import uuid4

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from sapperrag.core_setting.conf import settings
from sapperrag.log import log


def create_engine_and_session(url: str | URL):
    try:
        # 数据库引擎
        engine = create_async_engine(url, echo=settings.MYSQL_ECHO, future=True, pool_pre_ping=True)
        # log.success('数据库连接成功')
    except Exception as e:
        log.error('❌ 数据库链接失败 {}', e)
        sys.exit()
    else:
        db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        return engine, db_session


SQLALCHEMY_DATABASE_URL = (
    f'mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:'
    f'{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}?charset={settings.MYSQL_CHARSET}'
)

async_engine, async_db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


def uuid4_str() -> str:
    """数据库引擎 UUID 类型兼容性解决方案"""
    return str(uuid4())
