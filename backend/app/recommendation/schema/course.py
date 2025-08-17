from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class CourseBase(BaseModel):
    course_id: str = Field(..., description="课程唯一标识")
    resource_name: str = Field(..., description="资源名称")
    file_name: str = Field(..., description="文件名")
    grade: str = Field(..., description="年级")
    subject: str = Field(..., description="学科")
    video_link: Optional[str] = Field(None, description="视频链接")
    learning_objectives: Optional[str] = Field(None, description="学习目标")
    learning_style_preference: Optional[str] = Field(None, description="学习方式偏好")
    knowledge_level_self_assessment: Optional[str] = Field(None, description="知识掌握程度自评")
    dialogue: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="课程对话")

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    resource_name: Optional[str] = None
    video_link: Optional[str] = None
    learning_objectives: Optional[str] = None
    learning_style_preference: Optional[str] = None
    knowledge_level_self_assessment: Optional[str] = None
    dialogue: Optional[List[str]] = None

class CourseResponse(CourseBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True