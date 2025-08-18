import json

from typing import Dict
from typing import List
from typing import Any, TypeVar


from sqlalchemy import Row, RowMapping
from sqlalchemy.orm import ColumnProperty, SynonymProperty, class_mapper

RowData = Row | RowMapping | Any

R = TypeVar('R', bound=RowData)


def parse_json(data: str, mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    将 JSON 数据解析为 Python 字典，并根据映射将键名进行转换。

    :param data: JSON 数据
    :param mapping: 键名映射，例如 {'old_key': 'new_key'}
    :return: 转换后的字典列表
    """
    return [
        {new_key: item.get(old_key, mapping[old_key]) for old_key, new_key in mapping.items()}
        for item in json.loads(data)
    ]

def num_tokens(text: str, token_encoder) -> int:
    """返回给定文本中的标记数"""
    return len(token_encoder.encode(text=text))


def select_as_dict(row: R, use_alias: bool = False) -> dict:
    """
    Converting SQLAlchemy select to dict, which can contain relational data.txt,
    depends on the properties of the select object itself

    If set use_alias is True, the column name will be returned as alias,
    If alias doesn't exist in columns, we don't recommend setting it to True

    :param row:
    :param use_alias:
    :return:
    """
    if not use_alias:
        result = row.__dict__
        if '_sa_instance_state' in result:
            del result['_sa_instance_state']
            return result
    else:
        result = {}
        mapper = class_mapper(row.__class__)
        for prop in mapper.iterate_properties:
            if isinstance(prop, (ColumnProperty, SynonymProperty)):
                key = prop.key
                result[key] = getattr(row, key)
        return result