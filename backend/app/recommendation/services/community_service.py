import asyncio

from database.db_mysql import async_db_session
from sapperrag.crud.crud_community import community_dao
from sapperrag.schema.community import CommunityBase


class CommunityService:
    _lock = asyncio.Lock()  # 创建一个类级别的异步锁

    @staticmethod
    async def add(*, obj: CommunityBase) -> str:
        async with async_db_session.begin() as db:
            # 创建图谱库
            return await community_dao.create(db, obj)

    @staticmethod
    async def delete_all(*, knowledge_graph_uuid: str) -> int:
        async with async_db_session.begin() as db:
            communities = await community_dao.get_list(db=db, knowledge_graph_uuid=knowledge_graph_uuid)
            if not communities:
                return 0
            for community in communities:
                count = await community_dao.delete(db, community.id)
            return count



community_service = CommunityService()
