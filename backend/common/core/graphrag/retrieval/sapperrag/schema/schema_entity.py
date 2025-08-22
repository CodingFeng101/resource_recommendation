from __future__ import annotations
from pydantic import model_validator, Field

from datetime import datetime

from sapperrag.schema.schema import SchemaBase
from sapperrag.utils.enums import StatusType


class SchemaEntityBase(SchemaBase):
    """获取图谱详情"""
    name: str
    type: str | None = None
    attributes: str | None = None
    definition: str | None = None
    source: str | None = None
    status: int | None = StatusType.enable.value


class SchemaEntityResponse(SchemaEntityBase):
    id: int
    uuid: str
    schema_graph_uuid: str
    created_time: datetime
    updated_time: datetime | None = None


class AddSchemaEntityParam(SchemaEntityBase):
    schema_graph_uuid: str
    def __str__(self):
        return self.attributes

class UpdateSchemaEntityParam(SchemaEntityBase):
    schema_graph_uuid: str
    data: SchemaEntityBase
    @model_validator(mode='before')
    def check_name(cls, values):
        if values.get('name') and len(values.get('name')) < 1:
            raise ValueError('实体类型名称不能为空')
        return values


class GetSchemaEntityDetail(SchemaEntityBase):
    schema_graph: list

