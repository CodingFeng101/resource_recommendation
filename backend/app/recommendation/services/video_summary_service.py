from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..crud import video_summary_dao
from ..schema.video_summary import VideoSummaryCreate, VideoSummaryUpdate, VideoSummaryResponse

class VideoSummaryService:
    def __init__(self, db: Session):
        self.db = db

    def create_video_summary(self, summary_data: VideoSummaryCreate) -> VideoSummaryResponse:
        summary = video_summary_dao.create(self.db, obj_in=summary_data)
        return VideoSummaryResponse.from_orm(summary)

    def get_video_summary(self, uuid: UUID) -> Optional[VideoSummaryResponse]:
        summary = video_summary_dao.get(self.db, uuid=uuid)
        return VideoSummaryResponse.from_orm(summary) if summary else None

    def get_video_summaries_by_course(
        self, course_uuid: UUID, skip: int = 0, limit: int = 100
    ) -> List[VideoSummaryResponse]:
        summaries = video_summary_dao.get_by_course_uuid(
            self.db, course_uuid=course_uuid, skip=skip, limit=limit
        )
        return [VideoSummaryResponse.from_orm(summary) for summary in summaries]

    def get_all_video_summaries(self, skip: int = 0, limit: int = 100) -> List[VideoSummaryResponse]:
        summaries = video_summary_dao.get_multi(self.db, skip=skip, limit=limit)
        return [VideoSummaryResponse.from_orm(summary) for summary in summaries]

    def update_video_summary(
        self, uuid: UUID, summary_update: VideoSummaryUpdate
    ) -> Optional[VideoSummaryResponse]:
        summary = video_summary_dao.get(self.db, uuid=uuid)
        if not summary:
            return None
        updated_summary = video_summary_dao.update(
            self.db, db_obj=summary, obj_in=summary_update
        )
        return VideoSummaryResponse.from_orm(updated_summary)

    def delete_video_summary(self, uuid: UUID) -> bool:
        summary = video_summary_dao.get(self.db, uuid=uuid)
        if not summary:
            return False
        video_summary_dao.remove(self.db, uuid=uuid)
        return True