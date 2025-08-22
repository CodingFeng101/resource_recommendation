#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from database.db_mysql import async_db_session
from sapperrag.crud.crud_embedding import embedding_dao
from sapperrag.schema.embedding import EmbeddingBase


class EmbeddingService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: EmbeddingBase) -> str:
        async with async_db_session.begin() as db:
            embedding = await embedding_dao.get_with_relation(
                db=db, knowledge_entity_uuid=obj.knowledge_entity_uuid)
            if embedding:
                await embedding_dao.delete(db, embedding.id)
            return await embedding_dao.create(db, obj)


embedding_service = EmbeddingService()
