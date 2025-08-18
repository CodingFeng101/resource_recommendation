#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json

from sapperrag.service.community_service import community_service
from sapperrag.service.embedding_service import embedding_service
from sapperrag.service.knowledge_entity_service import knowledge_entity_service
from sapperrag.service.knowledge_graph_service import knowledge_graph_service
from sapperrag.schema import GetIndexDetail
from sapperrag.schema.community import AddCommunityParam
from sapperrag.schema.embedding import EmbeddingBase
from sapperrag.utils.serializers import select_as_dict


async def ask_knowledge_graph(uuid: str, query: str, api_key: str, base_url: str, model: str):
    knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
    data = GetIndexDetail(**select_as_dict(knowledge_graph))

    # 执行查询
    response = await knowledge_graph_service.query(
        knowledge_graph=data,
        query=query,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )
    return response


async def build_index(uuid: str, api_key, base_url, model):
    knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
    data = GetIndexDetail(**select_as_dict(knowledge_graph))

    # 执行构建索引任务
    index_result = await knowledge_graph_service.build_index(
        knowledge_graph=data,
        level=1,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    # 处理索引结果
    entities = index_result.get("entities", [])
    # community_reports = index_result.get('community_reports', [])
    # triple_community_hash_table = {}

    # 删除旧的社区数据
    # await community_service.delete_all(knowledge_graph_uuid=uuid)

    # 添加社区数据
    # for item in community_reports:
    #     community_uuid = await community_service.add(
    #         obj=AddCommunityParam(
    #             title=item.get('title', ''),
    #             content=item.get('full_content', ''),
    #             level=str(item.get('level', '')),
    #             rating=str(item.get('rating', '')),
    #             attributes=item.get('attributes', ''),
    #             knowledge_graph_uuid=uuid,
    #         )
    #     )
    #     triple_community_hash_table[item["id"]] = community_uuid

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
        # entity_community = []
        # if entity.get('community_ids', '{}'):
        #     entity_community = json.loads(json.dumps(entity.get('community_ids', '[]')))
        # for community in entity_community:
        #     community_uuid = triple_community_hash_table.get(community, None)
        #     if community_uuid:
        #         await knowledge_entity_service.add_community_relation(
        #             knowledge_entity_uuid=entity_uuid,
        #             community_uuid=community_uuid
        #         )
    # 完成任务
    result = {
        "type": "final_result",
        "data.txt": {"results": "成功构建索引"},
        "code": 200,
        "msg": "success"
    }
    return result


async def main():
    from dotenv import load_dotenv
    import os
    load_dotenv(override=True)
    uuid = os.getenv("graph_uuid")
    api_key = os.getenv("api_key")
    base_url = os.getenv("base_url")
    model = os.getenv("model")
    build_result = await build_index(
        uuid=uuid,
        api_key=api_key,
        base_url=base_url,
        model=model
    )
    print(build_result)


if __name__ == "__main__":
    asyncio.run(main())
