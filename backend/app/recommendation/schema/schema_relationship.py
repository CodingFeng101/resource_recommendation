from __future__ import annotations
from pydantic import model_validator, Field

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase
from datetime import datetime


class SchemaRelationshipBase(SchemaBase):
    """获取图谱详情"""
    name: str
    type: str | None = None
    attributes: str | None = Field("")
    definition: str | None = Field("")
    source: str | None = Field("")
    status: int | None = StatusType.enable.value


class SchemaRelationshipResponse(SchemaRelationshipBase):
    id: int
    uuid: str
    schema_graph_uuid: str
    source_entity_uuid: str
    target_entity_uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddSchemaRelationshipParam(SchemaRelationshipBase):
    schema_graph_uuid: str
    source_entity_uuid: str
    target_entity_uuid: str


class UpdateSchemaRelationshipParam(SchemaRelationshipBase):
    pass


class GetSchemaRelationshipDetail(SchemaRelationshipBase):
    schema_graph: list

