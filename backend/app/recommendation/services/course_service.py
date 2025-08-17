from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..crud import course_dao
from ..schema.course import CourseCreate, CourseUpdate, CourseResponse

class CourseService:
    def __init__(self, db: Session):
        self.db = db

    def create_course(self, course_data: CourseCreate) -> CourseResponse:
        course = course_dao.create(self.db, obj_in=course_data)
        return CourseResponse.from_orm(course)

    def get_course(self, uuid: UUID) -> Optional[CourseResponse]:
        course = course_dao.get(self.db, uuid=uuid)
        return CourseResponse.from_orm(course) if course else None

    def get_course_by_course_id(self, course_id: str) -> Optional[CourseResponse]:
        course = course_dao.get_by_course_id(self.db, course_id=course_id)
        return CourseResponse.from_orm(course) if course else None

    def get_courses(self, skip: int = 0, limit: int = 100) -> List[CourseResponse]:
        courses = course_dao.get_multi(self.db, skip=skip, limit=limit)
        return [CourseResponse.from_orm(course) for course in courses]

    def get_courses_by_grade_subject(
        self, grade: str, subject: str, skip: int = 0, limit: int = 100
    ) -> List[CourseResponse]:
        courses = course_dao.get_by_grade_subject(
            self.db, grade=grade, subject=subject, skip=skip, limit=limit
        )
        return [CourseResponse.from_orm(course) for course in courses]

    def update_course(self, uuid: UUID, course_update: CourseUpdate) -> Optional[CourseResponse]:
        course = course_dao.get(self.db, uuid=uuid)
        if not course:
            return None
        updated_course = course_dao.update(self.db, db_obj=course, obj_in=course_update)
        return CourseResponse.from_orm(updated_course)

    def delete_course(self, uuid: UUID) -> bool:
        course = course_dao.get(self.db, uuid=uuid)
        if not course:
            return False
        course_dao.remove(self.db, uuid=uuid)
        return True