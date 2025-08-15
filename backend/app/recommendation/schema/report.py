from pydantic import BaseModel, Field
from typing import Optional, List

class ReportBase(BaseModel):
    start_time: str = Field(..., description="开始时间，如'30.0 秒'")
    end_time: str = Field(..., description="结束时间，如'75.02 秒'")
    duration: str = Field(..., description="持续时间，如'45.02 秒'")
    segment_topic: str = Field(..., description="段落主题")
    key_points: List[str] = Field(..., description="关键点列表")

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    duration: Optional[str] = Field(None, description="持续时间")
    segment_topic: Optional[str] = Field(None, description="段落主题")
    key_points: Optional[List[str]] = Field(None, description="关键点列表")

class Report(ReportBase):
    uuid: str = Field(..., description="唯一标识符")

    class Config:
        from_attributes = True