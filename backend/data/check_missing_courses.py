#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并处理缺失的课程数据

该脚本会：
1. 读取 merged_dialogues.json 文件中的所有 course_id
2. 检查数据库中是否存在这些 course_id
3. 将缺失的课程数据提取出来，保存到新的 JSON 文件中
"""

import json
import asyncio
import sys
import os
from typing import List, Dict, Any, Set
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from backend.core.config import Settings
from backend.database.db_mysql import SessionLocal

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# 初始化配置
settings = Settings()

def load_merged_dialogues(file_path: str) -> List[Dict[str, Any]]:
    """
    加载 merged_dialogues.json 文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        课程数据列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载 {len(data)} 条课程数据")
        return data
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return []
    except json.JSONDecodeError as e:
        print(f"错误：JSON文件格式错误 - {e}")
        return []
    except Exception as e:
        print(f"错误：加载文件时发生异常 - {e}")
        return []

def get_existing_course_ids() -> Set[str]:
    """
    从数据库中获取已存在的 course_id 集合
    
    Returns:
        已存在的 course_id 集合
    """
    try:
        db = SessionLocal()
        
        # 查询数据库中所有的 course_id
        result = db.execute(text("SELECT course_id FROM courses"))
        existing_ids = {row[0] for row in result.fetchall()}
        
        db.close()
        print(f"数据库中已存在 {len(existing_ids)} 个课程")
        return existing_ids
        
    except Exception as e:
        print(f"错误：查询数据库时发生异常 - {e}")
        return set()

def find_missing_courses(all_courses: List[Dict[str, Any]], existing_ids: Set[str]) -> List[Dict[str, Any]]:
    """
    找出缺失的课程数据
    
    Args:
        all_courses: 所有课程数据
        existing_ids: 已存在的 course_id 集合
        
    Returns:
        缺失的课程数据列表
    """
    missing_courses = []
    
    for course in all_courses:
        course_id = course.get('course_id')
        if course_id == "1837024298040266754":
            missing_courses.append(course)

    
    print(f"发现 {len(missing_courses)} 个缺失的课程")
    return missing_courses

def save_missing_courses(missing_courses: List[Dict[str, Any]], output_path: str) -> bool:
    """
    保存缺失的课程数据到文件
    
    Args:
        missing_courses: 缺失的课程数据
        output_path: 输出文件路径
        
    Returns:
        是否保存成功
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(missing_courses, f, ensure_ascii=False, indent=2)
        
        print(f"成功保存 {len(missing_courses)} 个缺失课程到 {output_path}")
        return True
        
    except Exception as e:
        print(f"错误：保存文件时发生异常 - {e}")
        return False

def print_statistics(all_courses: List[Dict[str, Any]], existing_ids: Set[str], missing_courses: List[Dict[str, Any]]):
    """
    打印统计信息
    
    Args:
        all_courses: 所有课程数据
        existing_ids: 已存在的 course_id 集合
        missing_courses: 缺失的课程数据
    """
    print("\n=== 统计信息 ===")
    print(f"JSON文件中总课程数: {len(all_courses)}")
    print(f"数据库中已存在课程数: {len(existing_ids)}")
    print(f"缺失课程数: {len(missing_courses)}")
    print(f"缺失率: {len(missing_courses) / len(all_courses) * 100:.2f}%")
    
    if missing_courses:
        print("\n=== 缺失课程示例 ===")
        for i, course in enumerate(missing_courses[:5]):  # 显示前5个缺失课程
            print(f"{i+1}. course_id: {course.get('course_id')}, resource_name: {course.get('resource_name')}")
        
        if len(missing_courses) > 5:
            print(f"... 还有 {len(missing_courses) - 5} 个缺失课程")

def main():
    """
    主函数
    """
    print("开始检查缺失的课程数据...")
    
    # 文件路径
    input_file = "D:\\PycharmProjects\\resource_recommendation\\backend\\data\\merged_dialogues.json"
    output_file = "D:\\PycharmProjects\\resource_recommendation\\backend\\data\\missing_courses.json"
    
    # 1. 加载 JSON 文件
    all_courses = load_merged_dialogues(input_file)
    if not all_courses:
        print("没有加载到课程数据，程序退出")
        return
    missing_courses = []
    for course in all_courses[:30]:
        missing_courses.append(course)
    
    # # 2. 获取数据库中已存在的 course_id
    # existing_ids = get_existing_course_ids()
    #
    # # 3. 找出缺失的课程
    # missing_courses = find_missing_courses(all_courses, existing_ids)
    #
    # # 4. 打印统计信息
    # print_statistics(all_courses, existing_ids, missing_courses)
    #
    # # 5. 保存缺失的课程数据
    # if missing_courses:
    success = save_missing_courses(missing_courses, output_file)
    #     if success:
    #         print(f"\n缺失的课程数据已保存到: {output_file}")
    #         print("你可以使用这个文件重新导入缺失的课程数据")
    #     else:
    #         print("\n保存文件失败")
    # else:
    #     print("\n没有发现缺失的课程数据，所有课程都已存在于数据库中")
    #
    # print("\n检查完成！")

if __name__ == "__main__":
    main()