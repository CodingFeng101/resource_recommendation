#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from sqlalchemy import String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid

from backend.common.model import MappedBase as Base

class Report(Base):
    """学习报告表"""
    __tablename__ = 'reports'
    
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_uuid: Mapped[str] = mapped_column(String(36), ForeignKey('courses.uuid'), nullable=False)
    start_time: Mapped[str] = mapped_column(String(50), nullable=False)
    end_time: Mapped[str] = mapped_column(String(50), nullable=False)
    duration: Mapped[str] = mapped_column(String(50), nullable=False)
    segment_topic: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[list] = mapped_column(JSON, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    course: Mapped['Course'] = relationship("Course", back_populates="reports")
    report_embeddings: Mapped[list['ReportEmbedding']] = relationship(
        "ReportEmbedding", 
        back_populates="report", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Report(uuid='{self.uuid}', course_uuid='{self.course_uuid}', segment_topic='{self.segment_topic[:50]}...')>"