from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
import json

from ..model.model import ReportEmbedding
from ..schema.report_embedding import ReportEmbeddingCreate, ReportEmbeddingResponse

class CRUDReportEmbedding:
    def create(self, db: Session, *, obj_in: ReportEmbeddingCreate) -> ReportEmbedding:
        # 将向量转换为JSON字符串存储
        vector_str = json.dumps(obj_in.vector)
        db_obj = ReportEmbedding(
            vector=vector_str,
            report_uuid=obj_in.report_uuid
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, uuid: UUID) -> Optional[ReportEmbedding]:
        stmt = select(ReportEmbedding).where(ReportEmbedding.uuid == uuid)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_report_uuid(
        self, db: Session, *, report_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportEmbedding]:
        stmt = select(ReportEmbedding).where(
            ReportEmbedding.report_uuid == report_uuid
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ReportEmbedding]:
        stmt = select(ReportEmbedding).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def remove(self, db: Session, *, uuid: UUID) -> ReportEmbedding:
        stmt = select(ReportEmbedding).where(ReportEmbedding.uuid == uuid)
        result = db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # 异步方法
    async def create_async(self, db: AsyncSession, *, obj_in: ReportEmbeddingCreate) -> ReportEmbedding:
        # 将向量转换为JSON字符串存储
        vector_str = json.dumps(obj_in.vector)
        db_obj = ReportEmbedding(
            vector=vector_str,
            report_uuid=obj_in.report_uuid
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_async(self, db: AsyncSession, *, uuid: UUID) -> Optional[ReportEmbedding]:
        stmt = select(ReportEmbedding).where(ReportEmbedding.uuid == uuid)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_report_uuid_async(
        self, db: AsyncSession, *, report_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportEmbedding]:
        stmt = select(ReportEmbedding).where(
            ReportEmbedding.report_uuid == report_uuid
        ).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

report_embedding_dao = CRUDReportEmbedding()