import os

from dotenv import load_dotenv

from kg_construction.code.kg_constructor1 import extract_triples_from_xlsx
from kg_construction.code.save_data import save_knowledge_data

load_dotenv()
host = os.environ["host"]
user = os.environ["user"]
password = os.environ["password"]
database = os.environ["database"]
graph_uuid = os.environ["graph_uuid"]
model = os.environ["model"]

# 构建知识图谱
KG = extract_triples_from_xlsx("./input_data/签约运营话术库.xlsx", model)

# 将知识图谱存储到数据库中
save_knowledge_data(host, user, password, database, KG, graph_uuid)
