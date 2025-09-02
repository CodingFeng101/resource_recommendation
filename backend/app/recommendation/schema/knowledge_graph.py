from __future__ import annotations

from typing import Dict, List

from pydantic import Field

from backend.common.schema import SchemaBase
from datetime import datetime


class KnowledgeGraphBase(SchemaBase):
    """获取图谱详情"""
    name: str
    video_summary_uuid: str = Field(..., description="关联的视频摘要UUID")
    schema_graph_uuid: str | None = Field("")
    kg_base_uuid: str | None = Field("")


class KnowledgeGraphResponse(KnowledgeGraphBase):
    id: int
    uuid: str
    video_summary_uuid: str
    index_status: int
    created_time: datetime
    updated_time: datetime | None = None


class AddKnowledgeGraphParam(SchemaBase):
    file_paths: list[str]
    data: KnowledgeGraphBase


class AskKnowledgeGraphParam(SchemaBase):
    message: str
    infer: bool = False
    depth: int = 1
    user_token: str


class BuildKnowledgeGraphIndexParam(SchemaBase):
    knowledge_graph_uuid: str


class UpdateKnowledgeGraphBase(SchemaBase):
    name: str | None = None
    video_summary_uuid: str | None = Field(None, description="关联的视频摘要UUID")
    schema_graph_uuid: str | None = Field("")


class UpdateKnowledgeGraphParam(SchemaBase):
    file_paths: list[str]
    data: UpdateKnowledgeGraphBase


class IndexKnowledgeGraphBase(BuildKnowledgeGraphIndexParam):
    file_path: str | None = None

