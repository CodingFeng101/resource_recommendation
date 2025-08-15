#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from typing import List, Optional
from backend.app.recommendation.crud.embedding import embedding
from backend.app.recommendation.model.embedding import Embedding
from backend.app.recommendation.schema.embedding import (
    EmbeddingCreate, EmbeddingUpdate
)
from backend.common.exception.exception import errors
from backend.database.db_mysql import async_db_session


class EmbeddingService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: EmbeddingCreate) -> Embedding:
        """创建embedding"""
        async with EmbeddingService._lock:
            async with async_db_session.begin() as db:
                # 检查是否已存在相同segment_topic_uuid的embedding
                existing_embedding = await embedding.get_by_report_uuid(
                    db=db, report_uuid=obj.segment_topic_uuid)
                if existing_embedding:
                    # 如果存在，先删除旧的
                    await embedding.delete(db, existing_embedding.uuid)

                return await embedding.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: EmbeddingUpdate) -> Embedding:
        """更新embedding"""
        async with async_db_session.begin() as db:
            db_embedding = await embedding.get(db, uuid)
            if not db_embedding:
                raise errors.NotFoundError(msg='向量数据不存在')

            updated_embedding = await embedding.update(db, db_embedding, obj)
            return updated_embedding

    @staticmethod
    async def get_embedding(*, uuid: str) -> Embedding:
        """根据UUID获取embedding"""
        async with async_db_session() as db:
            db_embedding = await embedding.get(db, uuid)
            if not db_embedding:
                raise errors.NotFoundError(msg='向量数据不存在')
            return db_embedding

    @staticmethod
    async def get_by_report_uuid(*, report_uuid: str) -> Optional[Embedding]:
        """根据report UUID获取embedding"""
        async with async_db_session() as db:
            db_embedding = await embedding.get_by_report_uuid(db, report_uuid)
            return db_embedding

    @staticmethod
    async def delete(*, uuid: str) -> bool:
        """删除embedding"""
        async with async_db_session.begin() as db:
            db_embedding = await embedding.get(db, uuid)
            if not db_embedding:
                raise errors.NotFoundError(msg='向量数据不存在')

            deleted_embedding = await embedding.delete(db, uuid)
            return deleted_embedding is not None

    @staticmethod
    async def get_all() -> List[Embedding]:
        """获取所有embedding"""
        async with async_db_session() as db:
            embeddings = await embedding.get_all(db)
            return embeddings


embedding_service = EmbeddingService()
