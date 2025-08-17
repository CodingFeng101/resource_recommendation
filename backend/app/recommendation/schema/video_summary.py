from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class VideoSummaryBase(BaseModel):
    course_uuid: UUID = Field(..., description="关联的课程UUID")
    video_summary: str = Field(..., description="视频摘要内容")

class VideoSummaryCreate(VideoSummaryBase):
    pass

class VideoSummaryUpdate(BaseModel):
    video_summary: Optional[str] = None

class VideoSummaryResponse(VideoSummaryBase):
    uuid: UUID
    created_at: str

    class Config:
        from_attributes = True