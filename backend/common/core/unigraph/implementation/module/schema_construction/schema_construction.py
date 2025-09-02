from jinja2 import Template

from backend.common.core.llm.response_getter import GenericResponseGetter
from backend.common.core.unigraph.implementation.file.file_loader import FileLoader
from backend.common.core.unigraph.implementation.module.schema_construction.utils import is_chinese_more_than_english, \
    deduplicate_schema, extract_definition, extract_triples_and_strings, get_new_entity_types_from_response, \
    merge_type_dicts_with_semantic, get_new_relationship_types_from_response, get_entity_type_attributes_from_response, \
    transform_triplets_to_schema


class SchemaConstruction:
    def __init__(self, kg_schema, definition):
        self.kg_schema = kg_schema
        self.definition = definition
        self.suggestion = ""
        self.entity_type_dict = {}  # 用于存储实体类型及其实例的字典
        self.relation_type_dict = {}  # 用于存储关系类型及其实例的字典

    async def chatresponse(
            self,
            prompt,
            api_key,
            base_url,
            model
    ):
        response = await GenericResponseGetter.get_response(
            query=prompt,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        return response

    # 从各种文件中读取分割后的数据
    @classmethod
    def file_load(cls, file_path_list):
        """
        从各种类型的文件中读取文本
        """
        chunks = []
        tool = FileLoader()
        for file_path in file_path_list:
            content = tool.load(file_path)
            chunks.extend([chunk for chunk in content[0].values()])
        return chunks

    async def extract_from_path(
            self,
            file_path_list: list,
            aim: str,
            info: dict,
            directional_suggestion: str,
            api_key: str,
            base_url: str,
            model: str
    ) -> object:
        # 输入参数
        # 1. path:提取文件的文件路径
        # 2. aim:构建知识图谱的核心目标（应用）
        # 3. info:字典形式为{"add_entity": [], "del_entity": []}，每个列表中填相应的增删类别
        # 将新的增删信息添加到总的增删信息中
        chunks = SchemaConstruction.file_load(file_path_list)
        print(chunks)
        # 过滤掉空的文本块
        filter_chunks = [chunk for chunk in chunks if chunk]
        # 判断输入文本是中文还是英文
        language = "Chinese" if is_chinese_more_than_english(filter_chunks[0][0]) else "English"
        for chunk in filter_chunks:
            for text in chunk:
                await self.extract_kg_schema(
                    text,
                    aim,
                    directional_suggestion,
                    language,
                    api_key,
                    base_url,
                    model
                )
        # 对schema中的元素进行去重
        self.kg_schema = deduplicate_schema(self.kg_schema)
        # 过滤掉 source 为空字典的元素
        self.kg_schema = [i for i in self.kg_schema if i.get("source") != {}]
        await self.type_definition(language, api_key=api_key, base_url=base_url, model=model)
        return self.kg_schema, self.definition

    # 对实体类型和关系类型进行定义
    async def type_definition(
            self,
            language,
            api_key,
            base_url,
            model: str
    ):
        """
        Generate definitions for entity and relation types in batches of 10 (no progress bar)

        Args:
            api_key: API key for LLM service
            base_url: Base URL for API endpoint
            model: LLM model name
        """

        # ========= 实体类型定义（每10个键一批） =========
        entity_items = list(self.entity_type_dict.items())
        for i in range(0, len(entity_items), 10):
            batch = entity_items[i:i + 10]

            # 拼接当前批次的输入字符串
            batch_str = "\n".join(
                f"{key}: {', '.join(values)}" for key, values in batch
            )

            # 加载实体类型定义的提示词模板
            entity_type_define_prompt = Template(
                open("common/implementation/implementation/module/schema_construction/prompt/entity_type_define_agent.txt", "r", encoding="utf-8").read()
                # open("backend_temp/common/implementation/implementation/module/schema_construction/prompt/entity_type_define_agent.txt", "r", encoding="utf-8").read()
            )
            # 渲染提示词，填入实体类型字典字符串
            entity_type_define_prompt = entity_type_define_prompt.render(
                entity_type_dict_string=batch_str
            )

            # 调用大模型生成定义
            entity_type_define_response = await self.chatresponse(
                entity_type_define_prompt, api_key, base_url, model
            )

            # 解析响应并更新定义
            self.definition.update(extract_definition(entity_type_define_response))

        # ========= 关系类型定义（每10个键一批） =========
        relation_items = list(self.relation_type_dict.items())
        for i in range(0, len(relation_items), 10):
            batch = relation_items[i:i + 10]

            # 拼接当前批次的输入字符串
            batch_str = "\n".join(
                f"{key}: {', '.join(values)}" for key, values in batch
            )

            # 加载关系类型定义的提示词模板
            relation_type_define_prompt = Template(
                open("common/implementation/implementation/module/schema_construction/prompt/relation_type_define_agent.txt", "r", encoding="utf-8").read()
            # open("backend_temp/common/implementation/implementation/module/schema_construction/prompt/relation_type_define_agent.txt", "r",encoding="utf-8").read()
            )
            # 渲染提示词，填入关系类型字典字符串
            relation_type_define_prompt = relation_type_define_prompt.render(
                relation_type_dict_string=batch_str,
                language=language
            )

            # 调用大模型生成定义
            relation_type_define_response = await self.chatresponse(
                relation_type_define_prompt, api_key, base_url, model
            )

            # 解析响应并更新定义
            self.definition.update(extract_definition(relation_type_define_response))

    async def extract_kg_schema(
            self,
            text,
            aim,
            directional_suggestion,
            language,
            api_key,
            base_url,
            model: str
    ):
        extract_triples_from_text_prompt = Template(
            open(r"common/implementation/implementation/module/schema_construction/prompt/extract_triples_from_text_agent.txt", "r", encoding="utf-8").read()
            # open(r"backend_temp/common/implementation/implementation/module/schema_construction/prompt/extract_triples_from_text_agent.txt", "r",encoding="utf-8").read()
        )

        # 第一次调用大模型
        extract_triples_from_text_prompt = extract_triples_from_text_prompt.render(
            text=text,
            aim=aim,
            directional_suggestion=directional_suggestion,
            language=language
        )

        extract_triples_from_text_response = await self.chatresponse(
            extract_triples_from_text_prompt,
            api_key,
            base_url,
            model
        )

        # 从文本中提取三元组以及实体和关系
        Triple_source_dict, entity_string, relation_string = extract_triples_and_strings(extract_triples_from_text_response)

        entity_classify_prompt = Template(
            open("common/implementation/implementation/module/schema_construction/prompt/entity_classify_agent.txt", "r", encoding="utf-8").read()
            # open("backend_temp/common/implementation/implementation/module/schema_construction/prompt/entity_classify_agent.txt", "r", encoding="utf-8").read()
        )

        entity_classify_prompt = entity_classify_prompt.render(entity_string=entity_string, language=language)

        entity_classify_response = await self.chatresponse(entity_classify_prompt, api_key, base_url, model=model)

        # 更新实体类型字典
        if not self.kg_schema:
            self.entity_type_dict = get_new_entity_types_from_response(response=entity_classify_response)
        else:
            temp_entity_type_dict = get_new_entity_types_from_response(response=entity_classify_response)
            self.entity_type_dict = await merge_type_dicts_with_semantic(self.entity_type_dict,
                                                                         temp_entity_type_dict)

        relation_classify_prompt = Template(
            open("common/implementation/implementation/module/schema_construction/prompt/relation_classify_agent.txt").read()
            # open("backend_temp/common/implementation/implementation/module/schema_construction/prompt/relation_classify_agent.txt").read()
        )
        relation_classify_prompt = relation_classify_prompt.render(relation_string=relation_string, language=language)

        relation_classify_response = await self.chatresponse(relation_classify_prompt, api_key, base_url,
                                                             model=model)
        # 更新关系类型字典
        if not self.kg_schema:
            self.relation_type_dict = get_new_relationship_types_from_response(response=relation_classify_response)
        else:
            temp_relation_type_dict = get_new_relationship_types_from_response(response=relation_classify_response)
            self.relation_type_dict = await merge_type_dicts_with_semantic(self.relation_type_dict,
                                                                           temp_relation_type_dict)
        entity_type_string = "，".join(self.entity_type_dict.keys())
        attribute_reasoning_prompt = Template(
            open("common/implementation/implementation/module/schema_construction/prompt/attribute_reasoning.txt").read()
            # open("backend_temp/common/implementation/implementation/module/schema_construction/prompt/attribute_reasoning.txt").read()
        )
        attribute_reasoning_prompt = attribute_reasoning_prompt.render(entity_type_string = entity_type_string, language=language)
        attribute_reasoning_response = await self.chatresponse(attribute_reasoning_prompt, api_key, base_url,
                                                             model=model)
        entity_type_attribute_dict = get_entity_type_attributes_from_response(response=attribute_reasoning_response)

        kg_schema = transform_triplets_to_schema(Triple_source_dict, self.entity_type_dict,self.relation_type_dict, entity_type_attribute_dict)
        self.kg_schema.extend(kg_schema)


import asyncio
import json

if __name__ == "__main__":
    # 创建SchemaConstruction实例（需确保已正确导入该类）
    extractor = SchemaConstruction(
        kg_schema=[],
        definition={}
    )


    # 定义异步测试函数
    async def run_extraction():
        # 调用异步提取函数
        kg_schema, definition = await extractor.extract_from_path(
            api_key="sk-hd95YjFcrWVfOBah84B09a1c11284776A48294EbBe887c2e",
            base_url="https://api.rcouyi.com/v1",
            file_path_list=[r"test_input\text1.txt"],
            aim="提取实体",
            info={"add_entity": [], "del_entity": []},
            directional_suggestion="重点关注硬件相关实体",
            model="gpt-4.1"
        )

        # 打印结果
        print('-----------------------------------------')
        print(f"kgschema:{kg_schema}")
        print(f"definition:{definition}")

        # 保存结果到JSON文件
        with open(r"backend_temp\common\core_layer\unigraph\module\schema_construction\test_output\kg_schema.json", 'w', encoding='utf-8') as file:
            json.dump(kg_schema, file, ensure_ascii=False, indent=4)
        with open(r"backend_temp\common\core_layer\unigraph\module\schema_construction\test_output\definition.json", 'w', encoding='utf-8') as file:
            json.dump(definition, file, ensure_ascii=False, indent=4)


    # 运行异步测试函数
    asyncio.run(run_extraction())
