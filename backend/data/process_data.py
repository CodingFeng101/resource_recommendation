"""
数据处理脚本
功能包括：
1. 从原始JSON数据中提取对话内容
2. 合并所有JSON文件
3. 整合Excel文件中的资源信息
"""

import json
import os
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any

class DataProcessor:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.handleJSON_dir = self.base_dir / "handleJSON"
        self.handleJSON_dir.mkdir(exist_ok=True)

    def extract_dialogues_from_json(self, input_file: str, output_dir: str = None) -> None:
        """
        从原始JSON文件中提取对话内容并保存为单独的文件
        """
        if output_dir is None:
            output_dir = self.handleJSON_dir
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)

        print(f"开始从 {input_file} 提取对话...")

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print("错误: JSON文件应该包含一个列表")
                return

            extracted_count = 0

            for item in data:
                # 提取ID
                item_id = None
                if 'id' in item:
                    item_id = str(item['id'])
                elif 'ID' in item:
                    item_id = str(item['ID'])
                elif '数据ID' in item:
                    item_id = str(item['数据ID'])

                if not item_id:
                    print(f"跳过没有ID的项目: {item}")
                    continue

                # 提取对话内容
                dialogue_content = self._extract_dialogue_content(item)

                if dialogue_content:
                    # 保存到单独的文件
                    output_file = output_dir / f"{item_id}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(dialogue_content, f, ensure_ascii=False, indent=2)

                    extracted_count += 1
                    print(f"已提取对话: {item_id}")

            print(f"对话提取完成！总共提取了 {extracted_count} 个对话文件")

        except Exception as e:
            print(f"提取对话时出错: {e}")

    def _extract_dialogue_content(self, item: Dict) -> Dict:
        """提取单个项目的对话内容"""
        dialogue_content = {}

        # 提取各种可能的对话字段
        dialogue_fields = [
            'dialogue', 'conversation', 'chat', 'messages',
            '对话', '会话', '聊天记录', '消息'
        ]

        for field in dialogue_fields:
            if field in item:
                dialogue_content[field] = item[field]

        # 如果没有找到标准对话字段，尝试提取所有非ID字段
        if not dialogue_content:
            exclude_fields = ['id', 'ID', '数据ID', '_id']
            for key, value in item.items():
                if key not in exclude_fields:
                    dialogue_content[key] = value

        return dialogue_content

    def merge_with_excel_data(self, excel_file: str, output_file: str = "merged_dialogues.json") -> None:
        """
        合并JSON文件并整合Excel数据
        """
        print("开始合并JSON文件并整合Excel数据...")

        # 存储结果的列表
        merged_data = []

        # 读取Excel文件
        excel_data = {}
        try:
            df = pd.read_excel(excel_file)
            print(f"成功读取Excel文件，包含 {len(df)} 条记录")

            # 创建ID到资源信息的映射
            for _, row in df.iterrows():
                excel_data[str(row['数据ID'])] = {
                    "resource_name": row['资源名称'],
                    "file_name": row['文件名'],
                    "grade": row['年级'],
                    "subject": row['学科'],
                    "video_link": row['视频链接']
                }
        except Exception as e:
            print(f"读取Excel文件时出错: {e}")

        # 获取所有json文件
        if not self.handleJSON_dir.exists():
            print(f"错误: {self.handleJSON_dir} 目录不存在")
            return

        json_files = [f for f in os.listdir(self.handleJSON_dir) if f.endswith('.json')]
        print(f"找到 {len(json_files)} 个JSON文件")

        # 处理每个JSON文件
        for filename in sorted(json_files):
            file_id = filename.replace('.json', '')

            try:
                # 读取文件内容
                with open(self.handleJSON_dir / filename, 'r', encoding='utf-8') as f:
                    dialogue_content = json.load(f)

                # 创建新的数据结构，先添加id
                merged_item = {
                    "course_id": file_id
                }

                # 如果Excel中有对应的数据，添加额外字段
                if file_id in excel_data:
                    merged_item.update(excel_data[file_id])
                    print(f"已处理文件: {filename} (包含资源信息)")
                else:
                    print(f"已处理文件: {filename} (未找到对应的资源信息)")

                # 最后添加dialogue字段
                merged_item["dialogue"] = dialogue_content

                merged_data.append(merged_item)

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")

        # 保存合并后的数据
        try:
            output_path = self.base_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)

            print(f"\n合并完成！")
            print(f"总共处理了 {len(merged_data)} 个文件")
            print(f"结果保存在: {output_path}")

            # 统计有多少文件包含了Excel数据
            with_excel_data = sum(1 for item in merged_data if 'resource_name' in item)
            print(f"其中 {with_excel_data} 个文件包含了Excel资源信息")

        except Exception as e:
            print(f"保存文件时出错: {e}")

    def process_all(self, input_json: str = None, excel_file: str = "数据.xlsx",
                   output_file: str = "merged_dialogues.json",
                   extract_dialogues: bool = True) -> None:
        """
        完整的数据处理流程
        """
        print("=" * 50)
        print("开始数据处理流程")
        print("=" * 50)

        # 1. 如果提供了输入JSON文件，先提取对话
        if extract_dialogues and input_json and os.path.exists(input_json):
            print("\n步骤1: 提取对话内容")
            print("-" * 30)
            self.extract_dialogues_from_json(input_json)
        else:
            print("\n步骤1: 跳过对话提取（使用现有文件）")
            print("-" * 30)

        # 2. 合并JSON文件并整合Excel数据
        print("\n步骤2: 合并JSON文件并整合Excel数据")
        print("-" * 30)
        if os.path.exists(excel_file):
            self.merge_with_excel_data(excel_file, output_file)
        else:
            print(f"警告: Excel文件 {excel_file} 不存在，将只合并JSON文件")
            self.merge_with_excel_data("", output_file)

        print("\n" + "=" * 50)
        print("数据处理完成！")
        print("=" * 50)

def main():
    """主函数：不询问，直接合并已有 handleJSON 目录下的 json 文件"""
    processor = DataProcessor()

    # 不再询问，直接跳过对话提取，使用现有 handleJSON/*.json
    processor.process_all(
        input_json=None,            # 不再传原始大 JSON
        excel_file="数据.xlsx",
        output_file="merged_dialogues.json",
        extract_dialogues=False     # 关键：False 表示不再提取
    )

# if __name__ == "__main__":
#     main()
import json

with open("merged_dialogues.json", "r", encoding="utf-8") as f:
    merged_dialogues = json.load(f)
dialogue_list = []
# 取前 10 个对话
for dialogue in merged_dialogues[100:]:
    dialogue_list.append(dialogue)

with open("merged_dialogue.json", "w", encoding="utf-8") as f:
    json.dump(dialogue_list, f, ensure_ascii=False)