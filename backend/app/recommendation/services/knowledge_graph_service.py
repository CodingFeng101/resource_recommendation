import json
import pandas as pd
import asyncio

from backend.app.recommendation.model import KnowledgeGraph
from backend.common.core.graphrag.retrieval.sapperrag.core.model.model_load import load_entities, load_community, \
    load_relationships
from backend.common.core.graphrag.retrieval.sapperrag.crud.crud_knowledge_graph import knowledge_graph_dao
from backend.common.core.graphrag.retrieval.sapperrag.schema import GetIndexDetail
from backend.common.core.graphrag.retrieval.sapperrag.service.query_service import query_kg
from backend.common.core.graphrag.retrieval.sapperrag.utils.utils import parse_json
from backend.core.logging import logger
from backend.database.db_mysql import async_db_session


class KnowledgeGraphService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def query(
            *,
            knowledge_graph: GetIndexDetail,
            query: str,
            infer: bool = False,
            depth: int = 0,
            api_key: str,
            base_url: str,
            model: str):
        entities = [entity.to_dict() for entity in knowledge_graph.entities]
        relationships = [relationship.to_dict() for relationship in knowledge_graph.relationships]
        communities = [relationship.to_dict() for relationship in knowledge_graph.communities]
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

        results, context_text, context_data = await query_kg(
            query=query,
            entities=load_entities(df=pd.DataFrame(entities)),
            relationships=load_relationships(df=pd.DataFrame(relationships)),
            community_reports=load_community(df=pd.DataFrame(community_reports)),
            level=int(depth) - 1,
            infer=infer,
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        return {"results": results, "context_text": context_text}

    @staticmethod
    async def get_knowledge_graph(*, uuid: str = None, name: str = None) -> KnowledgeGraph:
        async with async_db_session() as db:
            knowledge_graph = await knowledge_graph_dao.get_with_relation(db, uuid=uuid, name=name)
            return knowledge_graph


knowledge_graph_service = KnowledgeGraphService()
