#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.recommendation.crud.crud_schema_relationship import schema_relationship_dao
from backend.app.recommendation.model import SchemaRelationship
from backend.app.recommendation.schema.schema_relationship import AddSchemaRelationshipParam, \
    UpdateSchemaRelationshipParam
from backend.common.exception.exception import errors
from backend.database.db_mysql import async_db_session


class SchemaRelationshipService:

    @staticmethod
    async def add(*, obj: AddSchemaRelationshipParam) -> str:
        async with async_db_session.begin() as db:
            # 创建图谱库
            return await schema_relationship_dao.create(db, obj)


    @staticmethod
    async def update(*, uuid: str, obj: UpdateSchemaRelationshipParam) -> int:
        async with async_db_session.begin() as db:
            schema_relationship = await schema_relationship_dao.get_by_uuid(db, uuid)
            if not schema_relationship:
                raise errors.NotFoundError(msg='关系类型不存在')

            # 更新图谱库信息
            count = await schema_relationship_dao.update_schema_relationship(db, schema_relationship.id, obj)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{schema_relationship.id}')
            return count

    @staticmethod
    async def get_schema_relationship(*, uuid: str = None, name: str = None, status: int = None) -> SchemaRelationship:
        async with async_db_session() as db:
            schema_relationship = await schema_relationship_dao.get_with_relation(db, uuid=uuid, name=name, status=status)
            if not schema_relationship:
                raise errors.NotFoundError(msg='图谱库不存在')
            return schema_relationship

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            schema_relationship = await schema_relationship_dao.get_by_uuid(db, uuid)
            if not schema_relationship:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await schema_relationship_dao.delete(db, schema_relationship.id)
            return count

    @staticmethod
    async def get_all(*,schema_graph_uuid: str, name: str = None) -> list[SchemaRelationship]:
        async with async_db_session() as db:
            schema_relationships = await schema_relationship_dao.get_list(db, schema_graph_uuid=schema_graph_uuid, name=name)
            if not schema_relationships:
                return []
            return schema_relationships

    @staticmethod
    async def delete_all(*, request: Request) -> int:
        """删除所有关系（需要超级管理员权限）"""
        async with async_db_session.begin() as db:

            # 执行批量删除操作
            count = await schema_relationship_dao.delete_all(db)

            # 清除所有相关缓存（根据实际情况调整）
            # 示例：await redis_client.delete_prefix(f"{settings.KG_BASE_REDIS_PREFIX}:*")

            return count


schema_relationship_service = SchemaRelationshipService()
