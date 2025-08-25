from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ReportBase(BaseModel):
    course_uuid: str = Field(..., description="关联的课程UUID")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    duration: str = Field(..., description="持续时间")
    segment_topic: str = Field(..., description="段落主题")
    key_points: List[str] = Field(..., description="关键点列表")

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    segment_topic: Optional[str] = None
    key_points: Optional[List[str]] = None

class ReportResponse(ReportBase):
    uuid: UUID
    created_at: str

    class Config:
        from_attributes = True