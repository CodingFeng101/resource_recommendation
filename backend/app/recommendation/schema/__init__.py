from .course import CourseBase, CourseCreate, CourseUpdate, CourseResponse
from .video_summary import VideoSummaryBase, VideoSummaryCreate, VideoSummaryUpdate, VideoSummaryResponse
from .summary_embedding import SummaryEmbeddingBase, SummaryEmbeddingCreate, SummaryEmbeddingResponse
from .report import ReportBase, ReportCreate, ReportUpdate, ReportResponse
from .report_embedding import ReportEmbeddingBase, ReportEmbeddingCreate, ReportEmbeddingResponse

__all__ = [
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse",
    "VideoSummaryBase", "VideoSummaryCreate", "VideoSummaryUpdate", "VideoSummaryResponse",
    "SummaryEmbeddingBase", "SummaryEmbeddingCreate", "SummaryEmbeddingResponse",
    "ReportBase", "ReportCreate", "ReportUpdate", "ReportResponse",
    "ReportEmbeddingBase", "ReportEmbeddingCreate", "ReportEmbeddingResponse"
]


import json

from pydantic import model_validator

from .embedding import EmbeddingResponse
from .community import CommunityResponse
from .knowledge_entity import KnowledgeEntityResponse
from .knowledge_graph import KnowledgeGraphResponse
from .knowledge_relationship import KnowledgeRelationshipResponse
from .schema_entity import SchemaEntityResponse
from .schema_graph import SchemaGraphResponse
from .schema_relationship import SchemaRelationshipResponse


class GetSchemaGraphDetail(SchemaGraphResponse):
    knowledge_graphs: list[KnowledgeGraphResponse]
    entities: list[SchemaEntityResponse]
    relationships: list[SchemaRelationshipResponse]


class GetKnowledgeEntityDetail(KnowledgeEntityResponse):
    embeddings: list[EmbeddingResponse] | list
    communities: list[CommunityResponse] | list[str]

    @model_validator(mode='after')
    def handel(self):
        """处理 embeddings 和 communities 数据"""
        embeddings = self.embeddings
        if embeddings and len(embeddings) >= 1:
            # embeddings[0].vector 已经在 EmbeddingResponse.handel() 中被解析为 JSON 对象
            # 直接使用解析后的数据，不需要再次 json.loads
            if isinstance(embeddings[0], dict):
                # 如果已经是字典，直接使用
                self.embeddings = embeddings[0].get('vector', [])
            else:
                # 如果是 EmbeddingResponse 对象，直接使用其 vector 属性
                self.embeddings = embeddings[0].vector

        communities = self.communities
        if communities and len(communities) >= 1:
            if isinstance(communities[0], str):
                # 如果已经是字符串列表，直接使用
                self.communities = communities
            else:
                # 如果是 CommunityResponse 对象，提取 uuid
                self.communities = [entity_community.uuid for entity_community in communities]
        return self



class GetIndexDetail(KnowledgeGraphResponse):
    entities: list[GetKnowledgeEntityDetail]
    relationships: list[KnowledgeRelationshipResponse]
    communities: list[CommunityResponse]


class GetKnowledgeGraphDetail(GetIndexDetail):
    schema_graph: SchemaGraphResponse




