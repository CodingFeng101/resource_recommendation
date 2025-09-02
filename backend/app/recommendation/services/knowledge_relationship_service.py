#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.recommendation.crud.crud_knowledge_relationship import knowledge_relationship_dao
from backend.app.recommendation.model import KnowledgeRelationship
from backend.app.recommendation.schema.knowledge_relationship import AddKnowledgeRelationshipParam, \
    UpdateKnowledgeRelationshipParam
from backend.common.exception.exception import errors
from backend.database.db_mysql import async_db_session


class KnowledgeRelationshipService:

    @staticmethod
    async def add(*, obj: AddKnowledgeRelationshipParam) -> str:
        async with async_db_session.begin() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_with_relation(
                db, name=obj.name, target_entity_uuid=obj.target_entity_uuid, source_entity_uuid=obj.source_entity_uuid)
            if knowledge_relationship:
                # 如果关系已存在，则直接返回
                return knowledge_relationship.uuid
            # 创建关系
            return await knowledge_relationship_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateKnowledgeRelationshipParam) -> int:
        async with async_db_session.begin() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_by_uuid(db, uuid)
            if not knowledge_relationship:
                raise errors.NotFoundError(msg='关系不存在')
            # 更新关系信息
            count = await knowledge_relationship_dao.update_knowledge_relationship(db, knowledge_relationship.id, obj)
            return count

    @staticmethod
    async def add_source_relation(*, knowledge_relationship_uuid: str, source_uuid: str) -> int:
        async with async_db_session.begin() as db:
            await knowledge_relationship_dao.add_source(db, knowledge_relationship_uuid=knowledge_relationship_uuid,
                                                        source_uuid=source_uuid)
            return 1

    @staticmethod
    async def get_knowledge_relationship(*, uuid: str = None, name: str = None,
                                         status: int = None) -> KnowledgeRelationship:
        async with async_db_session() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_with_relation(db, uuid=uuid, name=name,
                                                                                        status=status)
            if not knowledge_relationship:
                raise errors.NotFoundError(msg='关系不存在')
            return knowledge_relationship

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            knowledge_relationship = await knowledge_relationship_dao.get_by_uuid(db, uuid)
            if not knowledge_relationship:
                raise errors.NotFoundError(msg='关系不存在')
            count = await knowledge_relationship_dao.delete(db, knowledge_relationship.id)
            return count


    @staticmethod
    async def get_all(*, knowledge_graph_uuid: str, name: str = None) -> list[KnowledgeRelationship]:
        async with async_db_session() as db:
            knowledge_relationships = await knowledge_relationship_dao.get_list(db, knowledge_graph_uuid=knowledge_graph_uuid,
                                                                                name=name)
            if not knowledge_relationships:
                pass
            return knowledge_relationships


knowledge_relationship_service = KnowledgeRelationshipService()
