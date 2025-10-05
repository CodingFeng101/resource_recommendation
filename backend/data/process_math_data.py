#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class MathDataProcessor:
    """数学数据处理器"""
    
    def __init__(self, data_dir: str = "math"):
        """
        初始化数据处理器
        
        :param data_dir: 数据目录路径
        """
        self.data_dir = Path(__file__).parent / data_dir
        self.total_files = 0
        self.processed_files = 0
        
    def count_files(self) -> int:
        """统计目录下JSON文件总数"""
        if not self.data_dir.exists():
            print(f"错误：目录 {self.data_dir} 不存在")
            return 0
            
        json_files = list(self.data_dir.glob("*.json"))
        self.total_files = len(json_files)
        return self.total_files
    
    def load_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        加载单个JSON文件
        
        :param file_path: 文件路径
        :return: 解析后的字典数据或None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.processed_files += 1
                return data
        except json.JSONDecodeError as e:
            print(f"JSON解析错误 {file_path.name}: {e}")
            return None
        except Exception as e:
            print(f"文件读取错误 {file_path.name}: {e}")
            return None
    
    def process_files(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        处理JSON文件并提取数据
        
        :param limit: 限制处理的文件数量，None表示处理所有文件
        :return: 包含所有数据的列表
        """
        if not self.data_dir.exists():
            print(f"错误：目录 {self.data_dir} 不存在")
            return []
        
        # 获取所有JSON文件
        json_files = sorted(self.data_dir.glob("*.json"))
        
        if not json_files:
            print(f"警告：目录 {self.data_dir} 中没有找到JSON文件")
            return []
        
        # 应用限制
        if limit is not None and limit > 0:
            json_files = json_files[:limit]
            print(f"限制处理文件数量为: {limit}")
        
        print(f"开始处理 {len(json_files)} 个文件...")
        
        # 重置计数器
        self.processed_files = 0
        all_data = []
        
        for i, file_path in enumerate(json_files, 1):
            print(f"正在处理 ({i}/{len(json_files)}): {file_path.name}")
            
            data = self.load_single_file(file_path)
            if data is not None:
                all_data.append(data)
            
            # 显示进度
            if i % 50 == 0 or i == len(json_files):
                print(f"进度: {i}/{len(json_files)} ({i/len(json_files)*100:.1f}%)")
        
        print(f"\n处理完成！")
        print(f"成功处理: {self.processed_files} 个文件")
        print(f"失败文件: {len(json_files) - self.processed_files} 个")
        
        return all_data
    
    def get_data_summary(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取数据摘要信息
        
        :param data_list: 数据列表
        :return: 摘要信息字典
        """
        if not data_list:
            return {"total_records": 0}
        
        # 统计基本信息
        summary = {
            "total_records": len(data_list),
            "sample_keys": list(data_list[0].keys()) if data_list else [],
            "subjects": set(),
            "levels": set(),
            "versions": set(),
            "stages": set()
        }
        
        # 统计各种分类
        for item in data_list:
            if "disciplines" in item:
                summary["subjects"].add(item["disciplines"])
            if "level" in item:
                summary["levels"].add(item["level"])
            if "version" in item:
                summary["versions"].add(item["version"])
            if "stage" in item:
                summary["stages"].add(item["stage"])
        
        # 转换set为list以便JSON序列化
        summary["subjects"] = list(summary["subjects"])
        summary["levels"] = list(summary["levels"])
        summary["versions"] = list(summary["versions"])
        summary["stages"] = list(summary["stages"])
        
        return summary
    
    def save_processed_data(self, data_list: List[Dict[str, Any]], 
                          output_file: str = "processed_math_data.json") -> bool:
        """
        保存处理后的数据到文件
        
        :param data_list: 要保存的数据列表
        :param output_file: 输出文件名
        :return: 是否保存成功
        """
        try:
            output_path = Path(__file__).parent / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            
            print(f"数据已保存到: {output_path}")
            return True
        except Exception as e:
            print(f"保存数据时出错: {e}")
            return False


def main():
    """主函数 - 演示如何使用数据处理器"""
    print("=" * 60)
    print("数学课程数据处理器")
    print("=" * 60)
    
    # 创建处理器实例
    processor = MathDataProcessor()
    
    # 统计文件总数
    total_files = processor.count_files()
    print(f"发现JSON文件总数: {total_files}")
    
    if total_files == 0:
        return
    
    # 获取用户输入
    print(f"\n请选择处理方式:")
    print(f"1. 处理所有文件 ({total_files} 个)")
    print(f"2. 限制处理文件数量")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        limit = None
        if choice == "2":
            limit_input = input(f"请输入要处理的文件数量 (1-{total_files}): ").strip()
            limit = int(limit_input)
            if limit <= 0 or limit > total_files:
                print(f"无效的数量，将处理所有 {total_files} 个文件")
                limit = None
        elif choice != "1":
            print("无效选择，将处理所有文件")
    
    except (ValueError, KeyboardInterrupt):
        print("使用默认设置：处理所有文件")
        limit = None
    
    print("\n" + "=" * 60)
    
    # 处理数据
    data_list = processor.process_files(limit=limit)
    
    if not data_list:
        print("没有成功处理任何数据")
        return
    
    # 显示摘要信息
    print("\n" + "=" * 60)
    print("数据摘要信息:")
    print("=" * 60)
    
    summary = processor.get_data_summary(data_list)
    print(f"总记录数: {summary['total_records']}")
    print(f"数据字段: {', '.join(summary['sample_keys'][:10])}{'...' if len(summary['sample_keys']) > 10 else ''}")
    print(f"学科分类: {', '.join(summary['subjects'])}")
    print(f"年级分类: {', '.join(summary['levels'])}")
    print(f"版本分类: {', '.join(summary['versions'])}")
    print(f"学段分类: {', '.join(summary['stages'])}")
    
    # 询问是否保存数据
    try:
        save_choice = input(f"\n是否保存处理后的数据到文件? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes', '是']:
            processor.save_processed_data(data_list)
    except KeyboardInterrupt:
        print("\n操作已取消")
    
    print(f"\n处理完成！共处理 {len(data_list)} 条记录")


if __name__ == "__main__":
    main()