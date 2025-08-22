from __future__ import annotations
from pydantic import model_validator, Field


from datetime import datetime

from sapperrag.schema.schema import SchemaBase


class SourceBase(SchemaBase):
    """获取图谱详情"""
    content: str
    knowledge_graph_uuid: str | None = Field("")


class SourceResponse(SourceBase):
    id: int
    uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddSourceParam(SchemaBase):
    content: str
    knowledge_graph_uuid: str


class UpdateSourceParam(SchemaBase):
    content: str | None = None


class GetSourceDetail(SourceBase):
    knowledge_graph: list
