from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..crud import report_dao
from ..schema.report import ReportCreate, ReportUpdate, ReportResponse

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def create_report(self, report_data: ReportCreate) -> ReportResponse:
        report = report_dao.create(self.db, obj_in=report_data)
        return ReportResponse.from_orm(report)

    def get_report(self, uuid: UUID) -> Optional[ReportResponse]:
        report = report_dao.get(self.db, uuid=uuid)
        return ReportResponse.from_orm(report) if report else None

    def get_reports_by_course(
        self, course_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[ReportResponse]:
        reports = report_dao.get_by_course_uuid(
            self.db, course_uuid=course_uuid, skip=skip, limit=limit
        )
        return [ReportResponse.from_orm(report) for report in reports]

    def get_all_reports(self, skip: int = 0, limit: int = 100) -> List[ReportResponse]:
        reports = report_dao.get_multi(self.db, skip=skip, limit=limit)
        return [ReportResponse.from_orm(report) for report in reports]

    def update_report(self, uuid: UUID, report_update: ReportUpdate) -> Optional[ReportResponse]:
        report = report_dao.get(self.db, uuid=uuid)
        if not report:
            return None
        updated_report = report_dao.update(self.db, db_obj=report, obj_in=report_update)
        return ReportResponse.from_orm(updated_report)

    def delete_report(self, uuid: UUID) -> bool:
        report = report_dao.get(self.db, uuid=uuid)
        if not report:
            return False
        report_dao.remove(self.db, uuid=uuid)
        return True