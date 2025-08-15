from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..model.report import Report
from ..schema.report import ReportCreate, ReportUpdate

class CRUDReport:
    async def create(self, db: AsyncSession, obj_in: ReportCreate) -> Report:
        """创建report"""
        db_obj = Report(
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            duration=obj_in.duration,
            segment_topic=obj_in.segment_topic,
            key_points=obj_in.key_points
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: str) -> Optional[Report]:
        """根据UUID获取report"""
        result = await db.execute(select(Report).where(Report.uuid == id))
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession) -> List[Report]:
        """获取所有report"""
        result = await db.execute(select(Report))
        return result.scalars().all()

    async def update(self, db: AsyncSession, db_obj: Report, obj_in: ReportUpdate) -> Report:
        """更新report"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> Optional[Report]:
        """删除report"""
        result = await db.execute(select(Report).where(Report.uuid == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

report = CRUDReport()