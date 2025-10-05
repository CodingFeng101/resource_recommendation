#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid

from backend.common.model import MappedBase as Base

class VideoSummary(Base):
    """视频摘要表"""
    __tablename__ = 'video_summaries'
    
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_uuid: Mapped[str] = mapped_column(String(36), ForeignKey('courses.uuid'), nullable=False)
    video_summary: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    course: Mapped['Course'] = relationship("Course", back_populates="video_summaries")
    summary_embeddings: Mapped[list['SummaryEmbedding']] = relationship(
        "SummaryEmbedding", 
        back_populates="video_summary", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<VideoSummary(uuid='{self.uuid}', course_uuid='{self.course_uuid}')>"