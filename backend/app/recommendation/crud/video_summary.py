from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from backend.app.recommendation.model import VideoSummary
from ..schema.video_summary import VideoSummaryCreate, VideoSummaryUpdate

class CRUDVideoSummary:
    def create(self, db: Session, *, obj_in: VideoSummaryCreate) -> VideoSummary:
        db_obj = VideoSummary(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, uuid: UUID) -> Optional[VideoSummary]:
        stmt = select(VideoSummary).where(VideoSummary.uuid == uuid)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_course_uuid(
        self, db: Session, *, course_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[VideoSummary]:
        stmt = select(VideoSummary).where(
            VideoSummary.course_uuid == course_uuid
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[VideoSummary]:
        stmt = select(VideoSummary).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def update(
        self, db: Session, *, db_obj: VideoSummary, obj_in: VideoSummaryUpdate
    ) -> VideoSummary:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, uuid: UUID) -> VideoSummary:
        stmt = select(VideoSummary).where(VideoSummary.uuid == uuid)
        result = db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # 异步方法
    async def create_async(self, db: AsyncSession, *, obj_in: VideoSummaryCreate) -> VideoSummary:
        db_obj = VideoSummary(**obj_in.dict())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_async(self, db: AsyncSession, *, uuid: UUID) -> Optional[VideoSummary]:
        stmt = select(VideoSummary).where(VideoSummary.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_course_uuid_async(
        self, db: AsyncSession, *, course_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[VideoSummary]:
        stmt = select(VideoSummary).where(
            VideoSummary.course_uuid == course_uuid
        ).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

video_summary_dao = CRUDVideoSummary()