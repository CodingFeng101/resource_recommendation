#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.recommendation.crud.crud_knowledge_entity import knowledge_entity_dao
from backend.app.recommendation.model import KnowledgeEntity
from backend.app.recommendation.schema.knowledge_entity import AddKnowledgeEntityParam, UpdateKnowledgeEntityParam
from backend.common.exception.exception import errors
from backend.database.db_mysql import async_db_session


class KnowledgeEntityService:

    @staticmethod
    async def add(*, obj: AddKnowledgeEntityParam) -> str:
        async with async_db_session.begin() as db:
            knowledge_entity = await knowledge_entity_dao.get_with_relation(db, name=obj.name, type=obj.type,
                                                                            knowledge_graph_uuid=
                                                                            obj.knowledge_graph_uuid)
            if knowledge_entity:
                raise errors.ForbiddenError(msg='实例实体已存在')

            return await knowledge_entity_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateKnowledgeEntityParam) -> int:
        async with async_db_session.begin() as db:
            knowledge_entity = await knowledge_entity_dao.get_by_uuid(db, uuid)
            if not knowledge_entity:
                raise errors.NotFoundError(msg='需更新实体不存在')

            # 检查更新的名称是否已存在
            if obj.name and obj.name != knowledge_entity.name:
                existing_knowledge_entity = await knowledge_entity_dao.get_by_name(db, obj.name)
                if existing_knowledge_entity:
                    raise errors.ForbiddenError(msg='更新实体已存在')

            # 更新图谱库信息
            count = await knowledge_entity_dao.update_knowledge_entity(db, knowledge_entity.id, obj)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{knowledge_entity.id}')
            return count

    @staticmethod
    async def add_source_relation(*, knowledge_entity_uuid: str, source_uuid: str) -> int:
        async with async_db_session.begin() as db:
            await knowledge_entity_dao.add_source(db, knowledge_entity_uuid=knowledge_entity_uuid,
                                                  source_uuid=source_uuid)
            return 1

    @staticmethod
    async def add_community_relation(*, knowledge_entity_uuid: str, community_uuid: str) -> int:
        async with async_db_session.begin() as db:
            await knowledge_entity_dao.add_community(db, knowledge_entity_uuid=knowledge_entity_uuid,
                                                     community_uuid=community_uuid)
            return 1

    @staticmethod
    async def get_knowledge_entity(*, uuid: str = None, name: str = None, status: int = None,
                                   knowledge_graph_uuid: str = None) -> KnowledgeEntity:
        async with async_db_session() as db:
            knowledge_entity = await knowledge_entity_dao.get_with_relation(db, uuid=uuid, name=name, status=status,
                                                                            knowledge_graph_uuid=knowledge_graph_uuid)
            if not knowledge_entity:
                raise errors.NotFoundError(msg='图谱库不存在')
            return knowledge_entity

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            knowledge_entity = await knowledge_entity_dao.get_by_uuid(db, uuid)
            if not knowledge_entity:
                raise errors.NotFoundError(msg='删除实体不存在')
            count = await knowledge_entity_dao.delete(db, knowledge_entity.id)
            return count


    @staticmethod
    async def get_all(*, knowledge_graph_uuid: str, name: str = None) -> list[KnowledgeEntity]:
        async with async_db_session() as db:
            knowledge_entity = await knowledge_entity_dao.get_list(db, knowledge_graph_uuid=knowledge_graph_uuid, name=name)
            if not knowledge_entity:
                pass
            return knowledge_entity


knowledge_entity_service = KnowledgeEntityService()
