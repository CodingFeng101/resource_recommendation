from __future__ import annotations
from typing import Annotated
from fastapi import Path, APIRouter, HTTPException

from backend.app.recommendation.services.knowledge_graph_service import knowledge_graph_service
from backend.common.core.graphrag.retrieval.sapperrag.schema import GetIndexDetail
from backend.common.core.graphrag.retrieval.sapperrag.schema.knowledge_graph import AskKnowledgeGraphParam
from backend.common.core.graphrag.retrieval.sapperrag.utils.serializers import select_as_dict
from backend.core.logging import logger

router = APIRouter()

@router.post('/ask-graph/{uuid}', summary='基于KG进行问答')
async def ask_knowledge_graph(uuid: Annotated[str, Path(...)], obj: AskKnowledgeGraphParam):
    try:
        # 获取用户信息和知识图谱
        knowledge_graph = await knowledge_graph_service.get_knowledge_graph(uuid=uuid)
        data = GetIndexDetail(**select_as_dict(knowledge_graph))

        # 执行查询
        response = await knowledge_graph_service.query(
            knowledge_graph=data,
            query=obj.message,
            infer=obj.infer,
            depth=obj.depth,
        )

        return {
                "code": 200,
                "msg": "查询成功",
                "data": {
                    "response": response,
                    "knowledge_graph_uuid": uuid,
                    "query": obj.message,
                    "infer": obj.infer,
                    "depth": obj.depth
                }
            }

    except Exception as e:
        # 处理其他未预期的错误
        logger.error(f"知识图谱查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")





