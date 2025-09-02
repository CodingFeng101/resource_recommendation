#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class VideoSummary(Base):
    """视频摘要表"""
    __tablename__ = 'video_summaries'
    
    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_uuid = Column(String(36), ForeignKey('courses.uuid'), nullable=False)
    video_summary = Column(Text, nullable=False)
    
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    
    # 关系
    course = relationship("Course", back_populates="video_summaries")
    summary_embeddings = relationship("SummaryEmbedding", back_populates="video_summary")
    knowledge_graphs = relationship("KnowledgeGraph", back_populates="video_summary")
    
    def __repr__(self):
        return f"<VideoSummary(uuid='{self.uuid}', course_uuid='{self.course_uuid}')>"