from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from ..model.course import Course
from ..schema.course import CourseCreate, CourseUpdate

class CRUDCourse:
    def create(self, db: Session, *, obj_in: CourseCreate) -> Course:
        db_obj = Course(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, uuid: UUID) -> Optional[Course]:
        stmt = select(Course).where(Course.uuid == uuid)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_course_id(self, db: Session, *, course_id: str) -> Optional[Course]:
        stmt = select(Course).where(Course.course_id == course_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        stmt = select(Course).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def get_by_grade_subject(
        self, db: Session, *, grade: str, subject: str, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        stmt = select(Course).where(
            Course.grade == grade, Course.subject == subject
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def update(
        self, db: Session, *, db_obj: Course, obj_in: CourseUpdate
    ) -> Course:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, uuid: UUID) -> Course:
        stmt = select(Course).where(Course.uuid == uuid)
        result = db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # 异步方法
    async def create_async(self, db: AsyncSession, *, obj_in: CourseCreate) -> Course:
        db_obj = Course(**obj_in.dict())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_async(self, db: AsyncSession, *, uuid: UUID) -> Optional[Course]:
        stmt = select(Course).where(Course.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_course_id_async(self, db: AsyncSession, *, course_uuid: str) -> Optional[Course]:
        stmt = select(Course).where(Course.uuid == course_uuid)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_async(
        self, db: AsyncSession, *, db_obj: Course, obj_in: CourseUpdate
    ) -> Course:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

course_dao = CRUDCourse()