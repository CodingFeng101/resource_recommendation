from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from backend.app.recommendation.model import Report
from ..schema.report import ReportCreate, ReportUpdate

class CRUDReport:
    def create(self, db: Session, *, obj_in: ReportCreate) -> Report:
        db_obj = Report(
            course_uuid=obj_in.course_uuid,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            duration=obj_in.duration,
            segment_topic=obj_in.segment_topic,
            key_points=obj_in.key_points
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, uuid: UUID) -> Optional[Report]:
        return db.query(Report).filter(Report.uuid == uuid).first()

    def get_by_course_uuid(
        self, db: Session, *, course_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        stmt = select(Report).where(
            Report.course_uuid == course_uuid
        ).order_by(Report.start_time).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        return db.query(Report).offset(skip).limit(limit).all()

    def update(
        self, db: Session, *, db_obj: Report, obj_in: ReportUpdate
    ) -> Report:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, uuid: UUID) -> Report:
        obj = db.query(Report).filter(Report.uuid == uuid).first()
        db.delete(obj)
        db.commit()
        return obj

    # 异步方法
    async def create_async(self, db: AsyncSession, *, obj_in: ReportCreate) -> Report:
        db_obj = Report(**obj_in.dict())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_async(self, db: AsyncSession, *, uuid: UUID) -> Optional[Report]:
        stmt = select(Report).where(Report.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_course_uuid_async(
        self, db: AsyncSession, *, course_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        stmt = select(Report).where(
            Report.course_uuid == course_uuid
        ).order_by(Report.start_time).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

report_dao = CRUDReport()