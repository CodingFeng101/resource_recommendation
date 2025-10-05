from __future__ import annotations
from pydantic import model_validator, Field

from backend.common.schema import SchemaBase
from datetime import datetime


class CommunityBase(SchemaBase):
    """获取图谱详情"""
    content: str
    title: str
    level: str | None = None
    rating: str | None = None
    attributes: str | None = None
    knowledge_graph_uuid: str


class CommunityResponse(CommunityBase):
    id: int
    uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddCommunityParam(CommunityBase):
    pass


class UpdateCommunityParam(CommunityBase):
    pass


class GetCommunityDetail(CommunityBase):
    knowledge_graph: list
