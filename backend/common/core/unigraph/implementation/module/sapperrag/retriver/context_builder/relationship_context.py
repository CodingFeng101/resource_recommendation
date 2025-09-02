import logging
from collections import defaultdict
from typing import cast, Any

from ...utils import num_tokens
from ...index.graph.graph_parse import KGProcessor

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_relationship_context(
        selected_entities,
        relationships,
        token_encoder,
        entities,
        human_read_id: int,
        context_name="Relationships",
        top_k_relationships: int = 15,
        column_delimiter: str = "|",
        max_tokens: int = 10000
):
    """
    构建关系上下文

    :param selected_entities: 匹配到的实体列表
    :param relationships: 关系列表
    :param token_encoder: token编码器
    :param entities: 实体列表
    :param human_read_id: 人类可读的ID
    :param context_name: 上下文名称
    :param top_k_relationships: 选取的排名靠前的关系数量
    :param column_delimiter: 列分隔符
    :param max_tokens: 最大token数
    :return: 上下文文本，上下文数据，人类可读的ID, 选中的关系
    """
    selected_relationships = _filter_relationships(
        selected_entities=selected_entities,
        relationships=relationships,
        top_k_relationships=top_k_relationships
    )
    logger.info(f"已过滤关系😊")

    # 添加上下文标题
    current_context_text = f"-----{context_name}-----" + "\n"
    current_token = 0

    # 添加表头
    header = ["id", "name", "source", "target", "text"]
    current_context_text += column_delimiter.join(header) + "\n"
    all_context_records = [header]

    # 添加关系数据
    for relationship in selected_relationships:
        source_entity_name = next((entity.name for entity in entities if str(entity.id) == relationship.source), None)
        target_entity_name = next((entity.name for entity in entities if str(entity.id) == relationship.target), None)
        source_entity = get_entity_information_by_id(entities, relationship.source)
        target_entity = get_entity_information_by_id(entities, relationship.target)
        attributes = f"({source_entity}, {relationship.name}, {target_entity})"
        new_context = [
            str(human_read_id),
            relationship.name,
            source_entity_name,
            target_entity_name,
            attributes
        ]

        new_context_text = column_delimiter.join(new_context) + "\n"

        current_context_text += new_context_text
        all_context_records.append(new_context)
        human_read_id += 1
        current_token += num_tokens(current_context_text, token_encoder)
        if current_token >= max_tokens:
            break

    if len(all_context_records) > 1:
        record_df = pd.DataFrame(
            all_context_records[1:], columns=cast(Any, all_context_records[0])
        )
    else:
        record_df = pd.DataFrame()

    return selected_relationships, current_context_text, record_df, human_read_id


def _filter_relationships(
        selected_entities,
        relationships,
        top_k_relationships: int = 10,
        relationship_ranking_attributes: str = "weight",
):
    """
    过滤关系

    :param selected_entities: 匹配到的实体列表
    :param relationships: 关系列表
    :param top_k_relationships: 选取的排名靠前的关系数量
    :param relationship_ranking_attributes: 用于排序的关系属性
    """
    # 第一优先级：网络内关系（即所选实体之间的关系）
    selected_entity_ids = [str(entity.id) for entity in selected_entities]
    for relationship in relationships:
        relationship.attributes = {}
    in_network_relationships = [
        relationship
        for relationship in relationships
        if relationship.source in selected_entity_ids
        and relationship.target in selected_entity_ids
    ]
    # 第二优先级 - 网络外关系（即所选实体与不在所选实体中的其他实体之间的关系）
    source_relationships = [
        relationship
        for relationship in relationships
        if relationship.source in selected_entity_ids
        and relationship.target not in selected_entity_ids
    ]
    target_relationships = [
        relationship
        for relationship in relationships
        if relationship.target in selected_entity_ids
        and relationship.source not in selected_entity_ids
    ]
    out_network_relationships = source_relationships + target_relationships

    # 在网络外关系中，优先考虑相互关系（即与多个选定实体共享的网络外实体的关系）
    out_network_source_ids = [
        relationship.source
        for relationship in out_network_relationships
        if relationship.source not in selected_entity_ids
    ]
    out_network_target_ids = [
        relationship.target
        for relationship in out_network_relationships
        if relationship.target not in selected_entity_ids
    ]
    out_network_entity_ids = list(
        set(out_network_source_ids + out_network_target_ids)
    )
    out_network_entity_links = defaultdict(int)
    for entity_name in out_network_entity_ids:
        targets = [
            relationship.target
            for relationship in out_network_relationships
            if relationship.source == entity_name
        ]
        sources = [
            relationship.source
            for relationship in out_network_relationships
            if relationship.target == entity_name
        ]
        out_network_entity_links[entity_name] = len(set(targets + sources))
    # 按链接数量和rank_attributes对网络外关系进行排序
    for rel in out_network_relationships:
        rel.attributes["links"] = (
            out_network_entity_links[rel.source]
            if rel.source in out_network_entity_links
            else out_network_entity_links[rel.target]
        )
    # 先按 attributes[links] 排序，然后按 ranking_attributes 排序
    out_network_relationships.sort(
        key=lambda x: (
            x.attributes["links"],
            # x.attributes[relationship_ranking_attributes],
        ),
        reverse=True,
    )
    for out_network_relationship in out_network_relationships:
        del out_network_relationship.attributes["links"]
    relationship_budget = top_k_relationships * len(selected_entities)
    return in_network_relationships + out_network_relationships[:relationship_budget]


def get_entity_information_by_id(entities, given_id):
    """
    根据实体ID获取实体信息

    :param entities: 实体列表
    :param given_id: 实体ID
    """
    for entity in entities:
        if str(entity.id) == given_id:

            if KGProcessor.remove_unrelated_attributes(entity.attributes) == {}:
                return f"{entity.name}"
            return f"{entity.name},{KGProcessor.remove_unrelated_attributes(entity.attributes)}"