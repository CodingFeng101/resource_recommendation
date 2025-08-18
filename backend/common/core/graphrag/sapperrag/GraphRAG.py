#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import asyncio
import re

from sapperrag.service.knowledge_graph_service import knowledge_graph_service
from sapperrag.schema import GetIndexDetail
from sapperrag.utils.serializers import select_as_dict


async def ask_knowledge_graph(uuid: str, query: str, api_key: str, base_url: str, model: str):
    # combined_knowledge_graph = GetIndexDetail(
    #     entities=[],
    #     relationships=[],
    #     communities=[],
    #     **{}
    # )
    #
    # for uid in uuid:
    knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
    data = GetIndexDetail(**select_as_dict(knowledge_graph))

        # combined_knowledge_graph.entities.extend(data.txt.entities)
        # combined_knowledge_graph.relationships.extend(data.txt.relationships)
        # combined_knowledge_graph.communities.extend(data.txt.communities)

    # 执行查询
    response = await knowledge_graph_service.query(
        knowledge_graph=data,
        query=query,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )
    results = response.get("results")
    context_text = response.get("context_text")

    # 去除答案中的无效字符串
    pattern = r'\[Data: Sources \(\d+\)\]'
    results = re.sub(pattern, '', results)

    # 去除source中的无效字符串
    lines = context_text.split('\n')
    remaining_lines = lines[2:]
    context_text = '\n'.join(remaining_lines)
    return results, context_text


async def main():
    from dotenv import load_dotenv
    import os
    load_dotenv(override=True)
    uuid = os.getenv("ask_uuid")
    api_key = os.getenv("api_key")
    base_url = os.getenv("base_url")
    model = os.getenv("model")
    query = ("哈喽，亲亲～我想了解一下咱们众 灿的分成那些哈")
    answer, source = await ask_knowledge_graph(
        uuid=uuid,
        query=query,
        api_key=api_key,
        base_url=base_url,
        model=model
    )
    print("Answer:", answer)
    # print("Source:", source)


if __name__ == "__main__":
    asyncio.run(main())
