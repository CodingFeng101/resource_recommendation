from __future__ import annotations

import json
import logging

import pandas as pd

from sapperrag.core.model.community import Community
from sapperrag.core.model.entity import Entity
from typing import List

from sapperrag.utils.utils import num_tokens

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_community_context(
        community_reports: list,
        human_read_id: int,
        selected_entities: List[Entity],
        token_encoder,
        column_delimiter: str = "|",
        max_tokens: int = 6000,
        user_level: int = 0,
        infer: bool = False,
        min_community_rank: int = 1,
        context_name: str = "Reports",
):
    """
    构建社区上下文

    :param community_reports: 社区报告列表
    :param human_read_id: 用于替换复杂的ID,方便模型溯源
    :param selected_entities: 匹配到的实体列表
    :param token_encoder: 用于计算文本长度的编码器
    :param column_delimiter: 列分隔符
    :param max_tokens: 最大token数
    :param user_level: 用户等级
    :param infer: 是否进行推理
    :param min_community_rank: 社区报告最低评分(用于筛选)
    :param context_name: 上下文名称
    :return: 上下文文本, 上下文数据, human_read_id
    """
    sorted_community_reports = sort_community(community_reports, selected_entities, user_level, infer)
    logger.info(f"已排序社区报告😊")
    def _is_included(report: community_reports) -> bool:
        return report.rating is not None and float(report.rating) >= min_community_rank

    # 根据社区报告最低评分进行筛选
    selected_reports = [report for report in sorted_community_reports if _is_included(report)]
    if not selected_reports:
        return "", pd.DataFrame(), human_read_id

    # 添加上下文标题
    current_context_text = f"-----{context_name}-----\n"
    current_token = 0

    # 添加表头
    header = ["id", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    # 构建上下文文本和记录
    for report in selected_reports:
        new_context = [
            str(human_read_id),
            "\n".join([
                f"社区名称: {json.loads(report.full_content)['title']}",
                f"社区摘要: {json.loads(report.full_content)['summary']}",
                *[
                    f"  详细摘要({index + 1}): {finding['summary']}\n 摘要说明({index + 1}): {finding['explanation']}"
                    for index, finding in enumerate(json.loads(report.full_content)["findings"])
                ]
            ])
        ]

        new_context_text = column_delimiter.join(new_context) + "\n"
        current_context_text += new_context_text
        all_context_records.append(new_context)
        human_read_id += 1
        current_token += num_tokens(current_context_text, token_encoder)
        if current_token >= max_tokens:
            break

    # 构建 DataFrame
    if len(all_context_records) > 1:
        record_df = pd.DataFrame(all_context_records[1:], columns=all_context_records[0])
    else:
        record_df = pd.DataFrame()

    return current_context_text, record_df, human_read_id


def sort_community(community_reports, selected_entities: List[Entity], user_level: int, infer: bool) -> List[Community]:
    """
    对社区报告进行排序

    :param community_reports: 社区报告列表
    :param selected_entities: 匹配到的实体列表
    :param user_level: 推理深度
    :param infer: 是否进行推理
    :return: 排序后的社区报告列表
    """
    community_matches = {}
    for entity in selected_entities:
        # 计算社区所包含选中实体的数量
        if entity.community_ids:
            for community_id in entity.community_ids:
                community_matches[community_id] = (
                        community_matches.get(community_id, 0) + 1
                )

    community_reports_id_dict = {
        community.id: community for community in community_reports
    }

    # 防止部分社区没有报告
    select_communities = [
        community_reports_id_dict.get(community_id)
        for community_id in community_matches
        if community_id in community_reports_id_dict
    ]
    for community in select_communities:
        if community.attributes is None:
            community.attributes = {}
        community.attributes["matches"] = community_matches[community.id]
    for community in select_communities:
        community.level = int(community.level)
    select_communities = base_on_matches(select_communities)
    for community in select_communities:
        del community.attributes["matches"]  # type: ignore
    if infer:
        logger.info(f"开始进行深度{infer}的推理")
        select_communities = base_on_user_levels(select_communities, user_level)
    return select_communities


def base_on_user_levels(select_communities, user_level: int) -> List[Community]:
    """
    基于用户指定的推理深度选取该深度的社区

    :param select_communities: 社区报告列表
    :param user_level: 推理深度
    """
    selected_communities = []
    for community in select_communities:
        if community.level == user_level:
            selected_communities.append(community)
    return selected_communities


def base_on_matches(select_communities) -> List[Community]:
    """
    基于匹配的实体数量对社区进行排序

    :param select_communities: 社区报告列表
    :return: 排序后的社区报告列表
    """
    select_communities.sort(
        key=lambda x: (x.attributes["matches"], x.level),
        reverse=True,
    )
    return select_communities