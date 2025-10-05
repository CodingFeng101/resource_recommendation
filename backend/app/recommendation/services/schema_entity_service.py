#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

from backend.app.recommendation.crud.crud_schema_entity import schema_entity_dao
from backend.app.recommendation.model import SchemaEntity
from backend.app.recommendation.schema.schema_entity import AddSchemaEntityParam, UpdateSchemaEntityParam
from backend.common.exception.exception import errors
from backend.database.db_mysql import async_db_session


class SchemaEntityService:

    @staticmethod
    async def add(*, obj: AddSchemaEntityParam) -> str:
        async with async_db_session.begin() as db:

            entity = await schema_entity_dao.get_by_name_and_schema_graph_uuid(db, obj.name, obj.schema_graph_uuid)
            if entity:

                raise errors.ForbiddenError(msg='实体类型名称已存在')
            return await schema_entity_dao.create(db, obj)


    @staticmethod
    async def update(*, uuid: str, obj: UpdateSchemaEntityParam) -> int:
        async with async_db_session.begin() as db:
            schema_entity = await schema_entity_dao.get_by_uuid(db, uuid)
            if not schema_entity:
                raise errors.NotFoundError(msg='该实体类型不存在')

            # 检查更新的名称是否已存在
            if obj.name and obj.name != schema_entity.name:
                existing_schema_entity = await schema_entity_dao.get_by_name_and_schema_graph_uuid(db, obj.name, obj.schema_graph_uuid)
                if existing_schema_entity:
                    raise errors.ForbiddenError(msg='实体类型名称已存在')

            # 更新图谱库信息
            count = await schema_entity_dao.update_schema_entity(db, schema_entity.id, obj.data)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{schema_entity.id}')
            return count

    @staticmethod
    async def get_schema_entity(*, uuid: str = None, name: str = None, schema_graph_uuid: str = None) -> SchemaEntity:
        async with async_db_session() as db:
            schema_entity = await schema_entity_dao.get_with_relation(
                db, uuid=uuid, name=name, schema_graph_uuid=schema_graph_uuid)
            if not schema_entity:
                raise errors.NotFoundError(msg='图谱库不存在')
            return schema_entity

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            schema_entity = await schema_entity_dao.get_by_uuid(db, uuid)
            if not schema_entity:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await schema_entity_dao.delete(db, schema_entity.id)
            return count

    @staticmethod
    async def get_all(*,kg_base_uuid: str, name: str = None) -> list[SchemaEntity]:
        async with async_db_session() as db:
            schema_entities = await schema_entity_dao.get_list(db, kg_base_uuid=kg_base_uuid, name=name)
            if not schema_entities:
                return []
            return schema_entities


schema_entity_service = SchemaEntityService()
