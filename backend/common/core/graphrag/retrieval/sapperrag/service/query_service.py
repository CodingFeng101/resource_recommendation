from backend.common.core.graphrag.retrieval.sapperrag.core.retriver.structured_search.local_search.mixed_context import \
    LocalSearchMixedContext
from backend.common.core.graphrag.retrieval.sapperrag.core.retriver.structured_search.local_search.search import \
    LocalSearch, logger
from backend.common.core.graphrag.retrieval.sapperrag.core.retriver.structured_search.local_search.system_prompt import \
    LOCAL_SEARCH_SYSTEM_PROMPT


async def query_kg(query: str,
                   entities: list,
                   relationships: list,
                   community_reports: list,
                   level: int,
                   infer: bool = False,
                   api_key: str = "",
                   base_url: str = "",
                   model: str="") -> tuple:
    """
    初始化搜索器

    :param query: 用户输入的问题
    :param entities: 实体列表
    :param relationships: 关系列表
    :param community_reports: 社区报告列表
    :param level: 查询深度
    :param infer: 是否进行推理
    :return: 查询结果
    """
    context_builder = LocalSearchMixedContext(entities, relationships, community_reports)
    search_engine = LocalSearch(context_builder, LOCAL_SEARCH_SYSTEM_PROMPT)
    logger.info("搜索器初始化成功😊")
    results = await search_engine.search(query, level, infer, api_key, base_url, model)
    logger.info(f"上下文:{results}😊")

    return results, search_engine.context_text, search_engine.context_data
