#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
from uuid import uuid4

import asyncio
from fastapi import Request

from backend.app.recommendation.crud.crud_schema_graph import schema_graph_dao
from backend.app.recommendation.model import SchemaGraph
from backend.app.recommendation.schema.schema_graph import SchemaGraphBase, UpdateSchemaGraphBase
from backend.common.core.unigraph.interface.kgschema_service import create_schema
from backend.common.exception.exception import errors
from backend.database.db_mysql import async_db_session

PERMANENT_TEMP_DIR = "temp_files"
os.makedirs(PERMANENT_TEMP_DIR, exist_ok=True)


class SchemaGraphService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: SchemaGraphBase) -> str:
        async with async_db_session.begin() as db:
            # 检查知识架构名称是否已存在
            schema_graph = await schema_graph_dao.get_by_name(db, name=obj.name, kg_base_uuid=obj.kg_base_uuid)
            if schema_graph:
                raise errors.ForbiddenError(msg='知识架构名称已存在')
            # 创建知识架构
            return await schema_graph_dao.create(db, obj)


    @staticmethod
    async def update(*, uuid: str, obj: UpdateSchemaGraphBase) -> int:
        async with async_db_session.begin() as db:
            schema_graph = await schema_graph_dao.get_by_uuid(db, uuid)

            if not schema_graph:
                raise errors.NotFoundError(msg='知识架构不存在')

            # 检查更新的名称是否已存在
            if obj.name and obj.name != schema_graph.name:
                existing_schema_graph = await schema_graph_dao.get_by_name(db, name=obj.name, kg_base_uuid=obj.kg_base_uuid)
                if existing_schema_graph:
                    raise errors.ForbiddenError(msg='知识图谱架构名称已存在')

            # 更新知识架构信息
            count = await schema_graph_dao.update(db, schema_graph.id, obj)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{schema_graph.id}')
            return count

    @staticmethod
    async def get_schema_graph(*, uuid: str = None, name: str = None) -> SchemaGraph:
        async with async_db_session() as db:
            schema_graph = await schema_graph_dao.get_with_relation(db, uuid=uuid, name=name)
            if not schema_graph:
                raise errors.NotFoundError(msg='该知识图谱架构不存在')
            return schema_graph

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            schema_graph = await schema_graph_dao.get_by_uuid(db, uuid)
            if not schema_graph:
                raise errors.NotFoundError(msg='知识架构不存在')
            if await schema_graph_dao.search_schema_related_knowledge_graph(db, uuid):
                raise errors.ForbiddenError(msg='知识架构已关联知识图谱，请先删除相关联的知识图谱')
            count = await schema_graph_dao.delete(db, schema_graph.id)
            return count


    @staticmethod
    async def get_all(*,kg_base_uuid: str, name: str = None) -> list[SchemaGraph]:
        async with async_db_session() as db:
            schema_graphs = await schema_graph_dao.get_list(db, kg_base_uuid=kg_base_uuid, name=name)
            if not schema_graphs:
                return []
            return schema_graphs


    @staticmethod
    async def create_schema(
            *,
            file_paths: list[str],
            aim: str = None,
            api_key:str,
            base_url:str,
            model: str,
    ):
        async with SchemaGraphService._lock:  # 使用异步锁确保同一时间只有一个请求被发送
            file_locations = []

            # 为每个请求生成一个唯一的UUID并创建子目录
            request_temp_dir = os.path.join(PERMANENT_TEMP_DIR, str(uuid4()))
            os.makedirs(request_temp_dir, exist_ok=True)

            try:
                # 模拟上传文件，复制一份到临时目录
                for file_path in file_paths:
                    filename = os.path.basename(file_path)
                    temp_path = os.path.join(request_temp_dir, filename)
                    # 确保路径格式正确，处理相对路径
                    if file_path.startswith('./'):
                        relative_file_path = os.path.normpath(file_path[2:])  # 移除 './' 前缀
                    else:
                        relative_file_path = os.path.normpath(file_path)
                    shutil.copy(relative_file_path, temp_path)
                    # 调用之前定义的上传函数，假设它返回一个SchemaResponse对象
                schema, definition = await create_schema(
                    file_path_list=file_locations,
                    aim=aim,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                )
            finally:
                # 删除临时文件
                shutil.rmtree(request_temp_dir)
            return schema, definition



schema_graph_service = SchemaGraphService()
