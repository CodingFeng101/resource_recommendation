#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Path, Query

from backend.app.recommendation.schema import GetIndexDetail
from backend.app.recommendation.services.knowledge_graph_service import knowledge_graph_service
from backend.common.response.response_schema import response_base
from backend.utils.serializers import select_as_dict

import logging
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/ask/{course_id}', summary='基于索引进行问答')
async def ask_knowledge_graph(course_id: Annotated[str, Path(...)],
                              message: str = Query(..., description="查询内容")):
     try:
        knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=course_id)
        data = GetIndexDetail(**select_as_dict(knowledge_graph))
        # 执行查询
        response = await knowledge_graph_service.query(
            knowledge_graph=data,
            query=message,
            infer=False,
            depth=1
        )
        return response_base.success(data=response)
     except Exception as e:
         logger.error(f"获取知识图谱列表失败: {str(e)}", exc_info=True)
