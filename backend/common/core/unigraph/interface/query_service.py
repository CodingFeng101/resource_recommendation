from typing import List, Dict, Any

from backend.common.core.unigraph.implementation.module.sapperrag.index.graph.graph_parse import transform_data, \
    KGProcessor
from backend.common.core.unigraph.implementation.module.sapperrag.retriver.structured_search.local_search.mixed_context import \
    LocalSearchMixedContext
from backend.common.core.unigraph.implementation.module.sapperrag.retriver.structured_search.local_search.search import \
    LocalSearch, logger
from backend.common.core.unigraph.implementation.module.sapperrag.retriver.structured_search.local_search.system_prompt import \
    LOCAL_SEARCH_SYSTEM_PROMPT


async def query_kg(query: str,
                   entities: list,
                   relationships: list,
                   community_reports: list,
                   level: int,
                   infer: bool) -> tuple:
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
    await search_engine.search(query, level, infer)
    return search_engine.context_text, search_engine.context_data
