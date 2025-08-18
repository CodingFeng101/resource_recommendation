import mysql.connector
from mysql.connector import Error
from uuid import uuid4
import json
from datetime import datetime


def create_database_connection(host_name, user_name, user_password, db_name):
    """创建数据库连接"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL数据库连接成功")
    except Error as e:
        print(f"连接错误: '{e}'")

    return connection


def get_max_id(connection, table_name):
    """获取指定表中当前最大的id值"""
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Error as e:
        print(f"获取最大ID错误: '{e}'")
        return 0


def store_knowledge_graph(connection, data, graph_uuid):
    """存储知识图谱数据到数据库"""
    cursor = connection.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间并格式化

    # 收集所有实体（去重）
    entities = set()
    for item in data:
        triple = item['triple']
        entities.add(triple['头实体'])
        entities.add(triple['尾实体'])

    # 获取实体表当前最大id，新实体从该值+1开始
    entity_start_id = get_max_id(connection, "knowledge_entity") + 1

    # 为每个实体生成唯一UUID并存储到knowledge_entity表
    entity_uuid_map = {}  # 用于映射实体与UUID
    for i, entity in enumerate(entities):
        entity_id = str(uuid4())  # 实体唯一UUID
        entity_uuid_map[entity] = entity_id
        current_id = entity_start_id + i  # 自增ID

        # 插入实体数据
        insert_entity = """
        INSERT INTO knowledge_entity (id, uuid, name, type, knowledge_graph_uuid, created_time, attributes, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        entity_data = (current_id, entity_id, entity, entity, graph_uuid, current_time, "{}", 1)
        cursor.execute(insert_entity, entity_data)

    # 获取关系表当前最大id，新关系从该值+1开始
    relation_start_id = get_max_id(connection, "knowledge_relationship") + 1

    # 存储关系到knowledge_relationship表
    for i, item in enumerate(data):
        triple = item['triple']
        source = item['source']
        relationship_id = str(uuid4())  # 关系唯一UUID
        relationship_name = triple['关系']
        current_id = relation_start_id + i  # 自增ID

        # 获取头实体和尾实体的UUID
        source_uuid = entity_uuid_map[triple['头实体']]
        target_uuid = entity_uuid_map[triple['尾实体']]

        # 插入关系数据
        insert_relationship = """
        INSERT INTO knowledge_relationship (id, uuid, name, type, source_entity_uuid, target_entity_uuid, knowledge_graph_uuid, created_time, attributes, status, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        relationship_data = (
            current_id,
            relationship_id,
            relationship_name,
            relationship_name,
            source_uuid,
            target_uuid,
            graph_uuid,
            current_time,
            "{}",  # 空字典转字符串存储，避免SQL语法错误
            1,
            source
        )
        cursor.execute(insert_relationship, relationship_data)

    connection.commit()
    print(f"本次新增实体数量: {len(entities)}, 新增关系数量: {len(data)}")
    print(f"实体ID范围: {entity_start_id} - {entity_start_id + len(entities) - 1}")
    print(f"关系ID范围: {relation_start_id} - {relation_start_id + len(data) - 1}")


# 新增的外部调用函数
def save_knowledge_data(host, user, password, database, data, graph_uuid):
    """
    外部调用接口：保存知识图谱数据到数据库

    参数:
        host: 数据库主机地址
        user: 数据库用户名
        password: 数据库密码
        database: 数据库名称
        data.txt: 要存储的知识图谱数据
        graph_name: 知识图谱名称，可选，默认为"default_graph"

    返回:
        成功返回graph_uuid，失败返回None
    """
    # 创建数据库连接
    connection = create_database_connection(host, user, password, database)
    if not connection:
        print("数据库连接失败，无法存储数据")
        return None

    try:
        # 存储数据
        store_knowledge_graph(connection, data, graph_uuid)
    except Error as e:
        print(f"存储数据时发生错误: {e}")
        connection.rollback()  # 发生错误时回滚
    finally:
        # 确保连接关闭
        if connection.is_connected():
            connection.close()
            print("数据库连接已关闭")


def main():
    # 示例用法
    host = "localhost"
    user = "root"
    password = "xfy64867"  # 替换为你的数据库密码
    database = "onlineunigraph"  # 替换为你的数据库名

    # 加载示例数据
    try:
        with open("output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"成功加载数据，共{len(data)}条三元组")

        graph_uuid = save_knowledge_data(host, user, password, database, data)
        if graph_uuid:
            print(f"数据已成功存储，图谱UUID: {graph_uuid}")

    except FileNotFoundError:
        print("未找到output.json文件，请检查文件路径")
    except json.JSONDecodeError:
        print("JSON文件解析错误，请检查文件格式")

if __name__ == "__main__":
    main()
