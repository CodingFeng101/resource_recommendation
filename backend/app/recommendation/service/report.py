#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from typing import List
from backend.app.recommendation.crud.report import report
from backend.app.recommendation.model.report import Report
from backend.app.recommendation.schema.report import (
    ReportCreate, ReportUpdate, ReportBase,
)
from backend.common.exception.exception import errors
from backend.database.db_mysql import async_db_session


class ReportService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: ReportCreate) -> Report:
        """创建report"""
        async with ReportService._lock:
            async with async_db_session.begin() as db:
                return await report.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: ReportUpdate) -> Report:
        """更新report"""
        async with async_db_session.begin() as db:
            db_report = await report.get(db, uuid)
            if not db_report:
                raise errors.NotFoundError(msg='报告数据不存在')

            updated_report = await report.update(db, db_report, obj)
            return updated_report

    @staticmethod
    async def get_report(*, uuid: str) -> Report:
        """根据UUID获取report"""
        async with async_db_session() as db:
            db_report = await report.get(db, uuid)
            if not db_report:
                raise errors.NotFoundError(msg='报告数据不存在')
            return db_report

    @staticmethod
    async def delete(*, uuid: str) -> bool:
        """删除report"""
        async with async_db_session.begin() as db:
            db_report = await report.get(db, uuid)
            if not db_report:
                raise errors.NotFoundError(msg='报告数据不存在')

            deleted_report = await report.delete(db, uuid)
            return deleted_report is not None

    @staticmethod
    async def get_all() -> List[Report]:
        """获取所有report"""
        async with async_db_session() as db:
            reports = await report.get_all(db)
            return reports

    @staticmethod
    async def get_report_with_embedding(*, uuid: str) -> Report:
        """获取report及其关联的embedding"""
        async with async_db_session() as db:
            db_report = await report.get(db, uuid)
            if not db_report:
                raise errors.NotFoundError(msg='报告数据不存在')

            # 如果需要加载embedding关系，可以在这里添加相关逻辑
            # 例如: await db.refresh(db_report, ['embedding'])
            return db_report


report_service = ReportService()
