from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Report(Base):
    __tablename__ = 'reports'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_uuid = Column(String(36), ForeignKey('courses.uuid'), nullable=False)
    start_time = Column(String(50), nullable=False)
    end_time = Column(String(50), nullable=False)
    duration = Column(String(50), nullable=False)
    segment_topic = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=False)
    
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    course = relationship("Course", back_populates="reports")
    report_embeddings = relationship("ReportEmbedding", back_populates="report")
    
    def __repr__(self):
        return f"<Report(uuid='{self.uuid}', course_uuid='{self.course_uuid}', segment_topic='{self.segment_topic[:50]}...')>"