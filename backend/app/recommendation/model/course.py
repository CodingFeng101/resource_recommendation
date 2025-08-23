from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Course(Base):
    __tablename__ = 'courses'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(100), unique=True, nullable=False, index=True)
    resource_name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    grade = Column(String(50), nullable=False, index=True)
    subject = Column(String(50), nullable=False, index=True)
    video_link = Column(Text, nullable=True)
    learning_objectives = Column(Text, nullable=True, default=None)
    learning_style_preference = Column(String(100), nullable=True, default=None)
    knowledge_level_self_assessment = Column(String(100), nullable=True, default=None)
    dialogue = Column(JSON, nullable=True, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    video_summaries = relationship("VideoSummary", back_populates="course")
    reports = relationship("Report", back_populates="course")
    
    def __repr__(self):
        return f"<Course(course_id='{self.course_id}', resource_name='{self.resource_name}')>"