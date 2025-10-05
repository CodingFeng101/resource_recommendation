#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
import json
import os
import asyncio
import pandas as pd

from fastapi import HTTPException

from backend.app.recommendation.crud.crud_knowledge_graph import knowledge_graph_dao
from backend.app.recommendation.model import KnowledgeGraph
from backend.app.recommendation.schema import GetIndexDetail
from backend.app.recommendation.schema.knowledge_graph import KnowledgeGraphBase, UpdateKnowledgeGraphParam
from backend.common.core.unigraph.interface.query_service import query_kg
from backend.common.core.unigraph.implementation.module.sapperrag.model.model_load import load_entities, load_community, \
    load_relationships
from backend.common.core.unigraph.implementation.module.sapperrag.utils import parse_json
from backend.common.exception.exception import errors
from backend.core.logging import logger
from backend.database.db_mysql import async_db_session

PERMANENT_TEMP_DIR = "temp_files"
os.makedirs(PERMANENT_TEMP_DIR, exist_ok=True)


class KnowledgeGraphService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: KnowledgeGraphBase) -> str:
        async with async_db_session.begin() as db:
            # 检查图谱库名称是否已存在
            knowledge_graph = await knowledge_graph_dao.get_by_name(db, name=obj.name, course_id=obj.course_id)
            if knowledge_graph:
                raise errors.ForbiddenError(msg='图谱库名称已存在')
            # 创建图谱库
            return await knowledge_graph_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateKnowledgeGraphParam) -> int:
        async with async_db_session.begin() as db:
            knowledge_graph = await knowledge_graph_dao.get_by_uuid(db, uuid)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')

            # 检查更新的名称是否已存在
            if obj.name and obj.name != knowledge_graph.name:
                existing_knowledge_graph = await knowledge_graph_dao.get_by_name(db, name=obj.name, kg_base_uuid=obj.kg_base_uuid)
                if existing_knowledge_graph:
                    raise errors.ForbiddenError(msg='图谱库名称已存在')

            # 更新图谱库信息
            count = await knowledge_graph_dao.update_knowledge_graph(db, knowledge_graph.id, obj)
            # await redis_client.delete(f'{settings.KG_BASE_REDIS_PREFIX}:{knowledge_graph.id}')
            return count

    @staticmethod
    async def get_knowledge_graph(*, uuid: str = None, name: str = None) -> KnowledgeGraph:
        async with async_db_session() as db:
            knowledge_graph = await knowledge_graph_dao.get_with_relation(db, uuid=uuid, name=name)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')
            return knowledge_graph


    @staticmethod
    async def get_depth(*, uuid: str = None) -> int:
        async with async_db_session() as db:
            depth = await knowledge_graph_dao.get_depth(db, uuid=uuid)
            if not depth:
                raise errors.NotFoundError(msg='图谱库不存在')
            return depth


    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            knowledge_graph = await knowledge_graph_dao.get_by_uuid(db, uuid=uuid)
            if not knowledge_graph:
                raise errors.NotFoundError(msg='图谱库不存在')
            count = await knowledge_graph_dao.delete(db, knowledge_graph.id)
            return count

    @staticmethod
    async def get_all(*, kg_base_uuid: str, name: str = None) -> list[KnowledgeGraph]:
        async with async_db_session() as db:
            knowledge_graphs = await knowledge_graph_dao.get_list(db, kg_base_uuid=kg_base_uuid, name=name)
            if not knowledge_graphs:
                return []
            return knowledge_graphs

    @staticmethod
    async def query(
            *,
            knowledge_graph: GetIndexDetail,
            query: str,
            infer: bool,
            depth: int):
        entities = [entity.to_dict() for entity in knowledge_graph.entities]
        relationships = [relationship.to_dict() for relationship in knowledge_graph.relationships]
        communities = [relationship.to_dict() for relationship in knowledge_graph.communities]
        try:
            # 从数据库导出的数据进行解析
            entity_mapping = {
                'uuid': 'id', 'name': 'name', 'type': 'type', 'attributes': 'attributes',
                'embeddings': 'attributes_embedding', 'sources': 'source_ids', 'communities': 'community_ids'
            }
            relationship_mapping = {
                'uuid': 'id', 'source_entity_uuid': 'source', 'target_entity_uuid': 'target',
                'type': 'type', 'name': 'name', 'attributes': 'attributes', "source": "triple_source"
            }
            community_report_mapping = {
                'uuid': 'id', 'title': 'title', 'level': 'level', 'content': 'full_content',
                'rating': 'rating', 'attributes': 'attributes'
            }

            entities = parse_json(json.dumps(entities), entity_mapping)
            relationships = parse_json(json.dumps(relationships), relationship_mapping)
            community_reports = parse_json(json.dumps(communities), community_report_mapping)
            logger.info("数据解析完毕😀")

            context_text, context_data = await query_kg(
                query=query,
                entities=load_entities(df=pd.DataFrame(entities)),
                relationships=load_relationships(df=pd.DataFrame(relationships)),
                community_reports=load_community(df=pd.DataFrame(community_reports)),
                level=int(depth) - 1,
                infer=infer,
            )
            return {"context_text": context_text, "context_data": context_data}

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


knowledge_graph_service = KnowledgeGraphService()
