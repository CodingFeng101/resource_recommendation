#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json

from typing import Annotated

import anyio
from fastapi import APIRouter, Path
from starlette.responses import StreamingResponse

from backend.app.recommendation.schema import GetSchemaGraphDetail, GetIndexDetail
from backend.app.recommendation.schema.community import AddCommunityParam
from backend.app.recommendation.schema.embedding import EmbeddingBase
from backend.app.recommendation.schema.knowledge_entity import AddKnowledgeEntityParam
from backend.app.recommendation.schema.knowledge_graph import AddKnowledgeGraphParam, AskKnowledgeGraphParam
from backend.app.recommendation.schema.knowledge_relationship import AddKnowledgeRelationshipParam
from backend.app.recommendation.schema.schema_entity import AddSchemaEntityParam
from backend.app.recommendation.schema.schema_graph import AddSchemaGraphParam
from backend.app.recommendation.schema.schema_relationship import AddSchemaRelationshipParam
from backend.app.recommendation.services.community_service import community_service
from backend.app.recommendation.services.embedding_service import embedding_service
from backend.app.recommendation.services.knowledge_entity_service import knowledge_entity_service
from backend.app.recommendation.services.knowledge_graph_service import knowledge_graph_service
from backend.app.recommendation.services.knowledge_relationship_service import knowledge_relationship_service
from backend.app.recommendation.services.schema_entity_service import schema_entity_service
from backend.app.recommendation.services.schema_graph_service import schema_graph_service
from backend.app.recommendation.services.schema_relationship_service import schema_relationship_service
from backend.common.response.response_schema import response_base, ResponseModel
from backend.utils.serializers import select_as_dict

import logging
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('create-schema', summary='提取知识架构')
async def create_schema_graph(obj_data: dict):
    try:
        # 反序列化参数
        obj_dict = obj_data
        obj = AddSchemaGraphParam(**obj_dict)

        # 初始化建议信息，防止为空时读取出错
        obj.data.modify_info = json.dumps({"add_entity": [], "del_entity": []})
        obj.data.modify_suggestion = ' '

        # 调用 schema_service 创建图谱
        schema_uuid = await schema_graph_service.add(obj=obj.data)

        # 创建架构
        schema, schema_definition = await schema_graph_service.create_schema(
            file_paths=obj.file_paths,
            aim=obj.data.aim
        )

        # 从架构中获取实体类型的source
        entity_source = {}
        for item in schema:
            directional_entity = item['schema']['DirectionalEntityType']['Name']
            directed_entity = item['schema']['DirectedEntityType']['Name']
            source_key = next(iter(item['source'].keys()))  # 获取 source 字典的第一个键
            source_entities = source_key.strip('()').split(', ')  # 去掉括号并按逗号分割

            if directional_entity not in entity_source:
                entity_source[directional_entity] = []
            if directed_entity not in entity_source:
                entity_source[directed_entity] = []

            entity_source[directional_entity].append(source_entities[0])
            entity_source[directed_entity].append(source_entities[2])

        # 去重并保持顺序
        for key in entity_source:
            entity_source[key] = list(dict.fromkeys(entity_source[key]))

        # 从架构中得到关系类型的source
        relation_source = {}
        for item in schema:
            relation_type = item['schema']['RelationType']
            sources = item['source']

            if relation_type not in relation_source:
                relation_source[relation_type] = {}
            relation_source[relation_type].update(sources)

        # 遍历提取的架构数据，处理实体和关系
        for item in schema:
            item = item.get("schema")
            directional_entity = item.get("DirectionalEntityType")
            directed_entity = item.get("DirectedEntityType")
            target_entity_uuid, source_entity_uuid = None, None

            # 处理源实体 (DirectionalEntity)
            if directional_entity:
                try:
                    entity = await schema_entity_service.get_schema_entity(
                        name=directional_entity.get("Name"), schema_graph_uuid=schema_uuid
                    )
                    source_entity_uuid = entity.uuid
                except Exception:
                    source_entity = AddSchemaEntityParam(
                        schema_graph_uuid=schema_uuid,
                        name=directional_entity.get("Name"),
                        attributes=json.dumps(directional_entity.get("Attributes")),
                        definition=schema_definition.get(directional_entity.get("Name")),
                        source=json.dumps(entity_source.get(directional_entity.get("Name")))
                    )
                    source_entity_uuid = await schema_entity_service.add(obj=source_entity)

            # 处理目标实体 (DirectedEntity)
            if directed_entity:
                try:
                    entity = await schema_entity_service.get_schema_entity(
                        name=directed_entity.get("Name"), schema_graph_uuid=schema_uuid
                    )
                    target_entity_uuid = entity.uuid
                except Exception:
                    target_entity = AddSchemaEntityParam(
                        schema_graph_uuid=schema_uuid,
                        name=directed_entity.get("Name"),
                        attributes=json.dumps(directed_entity.get("Attributes")),
                        definition=schema_definition.get(directed_entity.get("Name")),
                        source=json.dumps(entity_source.get(directed_entity.get("Name")))
                    )
                    target_entity_uuid = await schema_entity_service.add(obj=target_entity)

            # 处理关系 (Relationship)
            relationship = item.get('RelationType')
            if source_entity_uuid and target_entity_uuid and relationship:
                schema_relationship = AddSchemaRelationshipParam(
                    target_entity_uuid=target_entity_uuid,
                    source_entity_uuid=source_entity_uuid,
                    schema_graph_uuid=schema_uuid,
                    type=relationship,
                    name=relationship,
                    definition=schema_definition.get(relationship),
                    source=json.dumps(relation_source.get(relationship))
                )
                await schema_relationship_service.add(obj=schema_relationship)

        # 完成任务
        result = {
            "type": "final_result",
            "data": None,  # 保持原接口无具体 data
            "code": 200,
            "msg": "success",
        }
        return result

    except Exception as e:
        return e


@router.post('/create-kg', summary="提取知识图谱")
async def create_knowledge_graph(user_token: str, obj_data: dict):
    try:
        # 反序列化参数
        obj_dict = obj_data
        obj = AddKnowledgeGraphParam(**obj_dict)

        # 获取用户信息
        api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=user_token)
        knowledge_uuid = await knowledge_graph_service.add(obj=obj.data)

        # 获取模式图谱数据
        schema_graph = await schema_graph_service.get_schema_graph(uuid=obj.data.schema_graph_uuid)
        schema_data = GetSchemaGraphDetail(**select_as_dict(schema_graph))

        # 执行提取任务
        knowledge_graph_data_all = await knowledge_graph_service.extract(
            file_paths=obj.file_paths,
            schema=schema_data,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        # 处理提取的图谱数据
        for knowledge_graph_data in knowledge_graph_data_all:
            knowledge_graph = knowledge_graph_data['semantic_kg']
            triple_source = knowledge_graph_data['triple_source']

            # 转换三元组源哈希表
            triple_source_hash_table_ = {}
            for item in triple_source:
                triple_source_hash_table_[item['ID']] = item["TripleSource"]

            # 同时处理每个三元组及其ID对应的TripleSource
            for triple in knowledge_graph:
                directional_entity = triple.get('DirectionalEntity')
                directed_entity = triple.get('DirectedEntity')
                relation = triple.get('Relation')
                source_id = triple.get('ID')
                source_entity_uuid, target_entity_uuid = None, None

                # 处理头实体
                if directional_entity:
                    source_entity = AddKnowledgeEntityParam(
                        knowledge_graph_uuid=knowledge_uuid,
                        name=directional_entity.get('Name'),
                        type=directional_entity.get('Type'),
                        attributes=json.dumps(directional_entity.get('Attributes'))
                    )
                    try:
                        # 如果数据库没有实体，则新建
                        source_entity_uuid = await knowledge_entity_service.add(obj=source_entity)
                    except Exception as e:
                        exist_source_entity = await knowledge_entity_service.get_knowledge_entity(
                            name=source_entity.name, knowledge_graph_uuid=source_entity.knowledge_graph_uuid)
                        source_entity_uuid = exist_source_entity.uuid

                # 处理尾实体
                if directed_entity:
                    target_entity = AddKnowledgeEntityParam(
                        knowledge_graph_uuid=knowledge_uuid,
                        name=directed_entity.get('Name'),
                        type=directed_entity.get('Type'),
                        attributes=json.dumps(directed_entity.get('Attributes'))
                    )
                    try:
                        # 如果数据库没有，则新建
                        target_entity_uuid = await knowledge_entity_service.add(obj=target_entity)
                    except Exception as e:
                        exist_target_entity = await knowledge_entity_service.get_knowledge_entity(
                            name=target_entity.name, knowledge_graph_uuid=target_entity.knowledge_graph_uuid)
                        target_entity_uuid = exist_target_entity.uuid

                # 处理关系
                if relation and source_entity_uuid and target_entity_uuid:
                    relationship = AddKnowledgeRelationshipParam(
                        knowledge_graph_uuid=knowledge_uuid,
                        source_entity_uuid=source_entity_uuid,
                        target_entity_uuid=target_entity_uuid,
                        name=relation.get('Name'),
                        attributes='{}',
                        type=relation.get('Type'),
                        source=triple_source_hash_table_[source_id]
                    )
                    # 创建关系
                    await knowledge_relationship_service.add(obj=relationship)

        # 完成任务
        result = {
            "type": "final_result",
            "data": None,  # 保持原接口无具体 data
            "code": 200,
            "msg": "success"
        }
        return result

    except Exception as e:
        return e


@router.post('/build-index', summary="构建索引")
async def build_index(uuid: str, user_token: str, depth: int):
    try:
        # 获取用户信息和知识图谱
        api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=user_token)
        knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
        data = GetIndexDetail(**select_as_dict(knowledge_graph))

        # 执行构建索引任务
        index_result = await knowledge_graph_service.build_index(
            knowledge_graph=data,
            level=depth,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        # 处理索引结果
        entities = index_result.get("entities", [])
        community_reports = index_result.get('community_reports', [])
        triple_community_hash_table = {}

        # 删除旧的社区数据
        await community_service.delete_all(knowledge_graph_uuid=uuid)

        # 添加社区数据
        for item in community_reports:
            community_uuid = await community_service.add(
                obj=AddCommunityParam(
                    title=item.get('title', ''),
                    content=item.get('full_content', ''),
                    level=str(item.get('level', '')),
                    rating=str(item.get('rating', '')),
                    attributes=item.get('attributes', ''),
                    knowledge_graph_uuid=uuid
                )
            )
            triple_community_hash_table[item["id"]] = community_uuid

        # 添加实体和嵌入数据
        for entity in entities:
            entity_uuid = entity.get('id')
            vector = entity.get('attributes_embedding')
            await embedding_service.add(
                obj=EmbeddingBase(
                    knowledge_entity_uuid=entity_uuid,
                    vector=json.dumps(vector)
                )
            )
            entity_community = []
            if entity.get('community_ids', '{}'):
                entity_community = json.loads(json.dumps(entity.get('community_ids', '[]')))
            for community in entity_community:
                community_uuid = triple_community_hash_table.get(community, None)
                if community_uuid:
                    await knowledge_entity_service.add_community_relation(
                        knowledge_entity_uuid=entity_uuid,
                        community_uuid=community_uuid
                    )

        # 更新索引状态和深度
        await knowledge_graph_service.update_index_status(uuid=uuid, index_status=1)
        await knowledge_graph_service.update_depth(uuid=uuid, depth=depth)

        return response_base.success(data={"results": "成功构建索引"}, message="索引构建完成")

    except Exception as e:
        logger.error(f"构建索引失败: {str(e)}")
        return response_base.fail(message=f"任务失败, 请检查API账户并稍后重试: {str(e)}")


@router.get('/by-video-summary/{video_summary_uuid}', summary='根据视频摘要UUID获取知识图谱列表')
async def get_knowledge_graphs_by_video_summary(
    video_summary_uuid: Annotated[str, Path(..., description="视频摘要UUID")]
) -> ResponseModel:
    """
    根据视频摘要UUID获取知识图谱列表
    
    :param video_summary_uuid: 视频摘要UUID
    :return: 知识图谱列表
    """
    try:
        knowledge_graphs = await knowledge_graph_service.get_by_video_summary_uuid(
            video_summary_uuid=video_summary_uuid
        )
        
        # 转换为响应格式
        knowledge_graph_responses = [
            {
                "id": kg.id,
                "uuid": kg.uuid,
                "name": kg.name,
                "video_summary_uuid": kg.video_summary_uuid,
                "schema_graph_uuid": kg.schema_graph_uuid,
                "index_status": kg.index_status,
                "depth": kg.depth,
                "created_time": kg.created_time,
                "updated_time": kg.updated_time
            }
            for kg in knowledge_graphs
        ]
        
        return response_base.success(data=knowledge_graph_responses)
    except Exception as e:
        logger.error(f"获取知识图谱列表失败: {str(e)}", exc_info=True)
        return response_base.fail(msg=f"获取知识图谱列表失败: {str(e)}")


@router.post('/ask/{uuid}', summary='基于索引进行问答')
async def ask_knowledge_graph(uuid: Annotated[str, Path(...)],
                              obj: AskKnowledgeGraphParam):
    async def generate_stream():
        # 创建事件标志来控制心跳任务
        stop_event = asyncio.Event()

        async def send_heartbeats():
            while not stop_event.is_set():
                try:
                    # 使用wait_for而不是sleep，这样可以被事件中断
                    await asyncio.wait_for(stop_event.wait(), timeout=HEARTBEAT_INTERVAL)
                except asyncio.TimeoutError:
                    # 50秒到了，发送心跳
                    yield json.dumps({
                        "type": "processing",
                        "message": "Still processing..."
                    }) + "\n"

        async def process_request():

            try:
                # 获取用户信息和知识图谱
                api_key, base_url, model = await knowledge_graph_service.get_user_llm_info(user_token=obj.user_token)
                knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
                data = GetIndexDetail(**select_as_dict(knowledge_graph))

                # 执行查询
                response = await knowledge_graph_service.query(
                    knowledge_graph=data,
                    query=obj.message,
                    infer=obj.infer,
                    depth=obj.depth,
                    api_key=api_key,
                    base_url=base_url,
                    model=model,
                )

                # 返回成功结果（保持原有 ResponseModel 格式）
                yield json.dumps({
                    "type": "final_result",
                    "data": response,
                    "code": 200,
                    "msg": "success"
                }) + "\n"

            except asyncio.TimeoutError as e:
                yield json.dumps({
                    "type": "error",
                    "code": 500,
                    "msg": e
                }) + "\n"
            except Exception as e:
                yield json.dumps({
                    "type": "error",
                    "code": 500,
                    "msg": e
                }) + "\n"
            finally:
                stop_event.set()  # 停止心跳

        try:
            async for item in merge_async_generators(send_heartbeats(), process_request()):
                yield item
        except asyncio.CancelledError:
            stop_event.set()
            raise

    # 返回 StreamingResponse，保持 NDJSON 格式
    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")
