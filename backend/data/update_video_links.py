# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# 更新数据库中courses表的video_link字段
#
# 该脚本会：
# 1. 读取Excel文件中的新链接数据
# 2. 通过course_id匹配，更新数据库中courses表的video_link字段
# """
#
# import pandas as pd
# import os
# from typing import Dict, List, Tuple
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
#
# def get_database_url():
#     """
#     获取数据库连接URL
#     """
#     # 从环境变量或直接配置获取数据库连接信息
#     mysql_host = os.getenv('MYSQL_HOST', '127.0.0.1')
#     mysql_port = os.getenv('MYSQL_PORT', '3306')
#     mysql_user = os.getenv('MYSQL_USER', 'root')
#     mysql_password = os.getenv('MYSQL_PASSWORD', '12345678')
#     mysql_database = os.getenv('MYSQL_DATABASE', 'resource_recommendation')
#
#     return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
#
# def create_db_session():
#     """
#     创建数据库会话
#     """
#     try:
#         database_url = get_database_url()
#         engine = create_engine(database_url, echo=False)
#         SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#         return SessionLocal()
#     except Exception as e:
#         print(f"错误：创建数据库连接失败 - {e}")
#         print("请确保：")
#         print("1. MySQL服务正在运行")
#         print("2. 数据库连接信息正确")
#         print("3. 已安装pymysql: pip install pymysql")
#         return None
#
# def read_excel_data(file_path: str) -> pd.DataFrame:
#     """
#     读取Excel文件数据
#
#     Args:
#         file_path: Excel文件路径
#
#     Returns:
#         DataFrame包含课程数据
#     """
#     try:
#         # 读取Excel文件
#         df = pd.read_excel(file_path)
#         print(f"成功读取Excel文件，共 {len(df)} 行数据")
#
#         # 显示列名
#         print(f"Excel文件列名: {list(df.columns)}")
#
#         # 显示前几行数据
#         print("\n前5行数据:")
#         print(df.head())
#
#         return df
#
#     except FileNotFoundError:
#         print(f"错误：文件 {file_path} 不存在")
#         return pd.DataFrame()
#     except Exception as e:
#         print(f"错误：读取Excel文件时发生异常 - {e}")
#         print("请确保已安装openpyxl: pip install openpyxl")
#         return pd.DataFrame()
#
# def prepare_update_data(df: pd.DataFrame) -> List[Tuple[str, str]]:
#     """
#     准备更新数据
#
#     Args:
#         df: Excel数据DataFrame
#
#     Returns:
#         包含(course_id, video_link)元组的列表
#     """
#     update_data = []
#
#     # 根据实际的列名进行调整，这里假设列名为'数据ID'和'链接'
#     # 如果列名不同，需要根据实际情况修改
#     course_id_col = None
#     video_link_col = None
#
#     # 尝试找到course_id列
#     possible_id_cols = ['数据ID', 'course_id', 'ID', 'id', '课程ID', 'CourseID']
#     for col in possible_id_cols:
#         if col in df.columns:
#             course_id_col = col
#             break
#
#     # 尝试找到video_link列
#     possible_link_cols = ['链接', 'video_link', 'link', 'url', '视频链接', 'URL', 'Link']
#     for col in possible_link_cols:
#         if col in df.columns:
#             video_link_col = col
#             break
#
#     if not course_id_col:
#         print("错误：未找到course_id列，请检查Excel文件列名")
#         print(f"可用列名: {list(df.columns)}")
#         return []
#
#     if not video_link_col:
#         print("错误：未找到video_link列，请检查Excel文件列名")
#         print(f"可用列名: {list(df.columns)}")
#         return []
#
#     print(f"使用列: course_id='{course_id_col}', video_link='{video_link_col}'")
#
#     # 提取数据
#     for index, row in df.iterrows():
#         course_id = str(row[course_id_col]).strip()
#         video_link = str(row[video_link_col]).strip()
#
#         # 跳过空值
#         if pd.isna(row[course_id_col]) or pd.isna(row[video_link_col]):
#             continue
#
#         if course_id and video_link and video_link != 'nan':
#             update_data.append((course_id, video_link))
#
#     print(f"准备更新 {len(update_data)} 条记录")
#     return update_data
#
# def check_existing_courses(db, update_data: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], List[str]]:
#     """
#     检查哪些course_id在数据库中存在
#
#     Args:
#         db: 数据库会话
#         update_data: 要更新的数据列表
#
#     Returns:
#         (存在的数据, 不存在的course_id列表)
#     """
#     try:
#         existing_data = []
#         missing_ids = []
#
#         for course_id, video_link in update_data:
#             # 检查course_id是否存在
#             result = db.execute(
#                 text("SELECT COUNT(*) FROM courses WHERE course_id = :course_id"),
#                 {"course_id": course_id}
#             )
#             count = result.scalar()
#
#             if count > 0:
#                 existing_data.append((course_id, video_link))
#             else:
#                 missing_ids.append(course_id)
#
#         print(f"数据库中存在 {len(existing_data)} 个course_id")
#         print(f"数据库中不存在 {len(missing_ids)} 个course_id")
#
#         if missing_ids:
#             print("\n不存在的course_id示例:")
#             for i, missing_id in enumerate(missing_ids[:5]):
#                 print(f"  {i+1}. {missing_id}")
#             if len(missing_ids) > 5:
#                 print(f"  ... 还有 {len(missing_ids) - 5} 个")
#
#         return existing_data, missing_ids
#
#     except Exception as e:
#         print(f"错误：检查数据库时发生异常 - {e}")
#         return [], []
#
# def update_video_links(db, update_data: List[Tuple[str, str]]) -> Dict[str, int]:
#     """
#     更新数据库中的video_link字段
#
#     Args:
#         db: 数据库会话
#         update_data: 要更新的数据列表
#
#     Returns:
#         更新结果统计
#     """
#     results = {
#         "total": len(update_data),
#         "success": 0,
#         "failed": 0,
#         "errors": []
#     }
#
#     try:
#         for course_id, video_link in update_data:
#             try:
#                 # 更新video_link字段
#                 result = db.execute(
#                     text("UPDATE courses SET video_link = :video_link WHERE course_id = :course_id"),
#                     {"course_id": course_id, "video_link": video_link}
#                 )
#
#                 if result.rowcount > 0:
#                     results["success"] += 1
#                     print(f"✓ 更新成功: {course_id}")
#                 else:
#                     results["failed"] += 1
#                     results["errors"].append(f"course_id {course_id}: 未找到匹配记录")
#
#             except Exception as e:
#                 results["failed"] += 1
#                 results["errors"].append(f"course_id {course_id}: {str(e)}")
#                 print(f"✗ 更新失败: {course_id} - {str(e)}")
#
#         # 提交事务
#         db.commit()
#
#     except Exception as e:
#         print(f"错误：更新数据库时发生异常 - {e}")
#         db.rollback()
#         results["failed"] = results["total"]
#         results["success"] = 0
#
#     return results
#
# def print_update_results(results: Dict[str, int]):
#     """
#     打印更新结果
#
#     Args:
#         results: 更新结果统计
#     """
#     print("\n=== 更新结果统计 ===")
#     print(f"总记录数: {results['total']}")
#     print(f"更新成功: {results['success']}")
#     print(f"更新失败: {results['failed']}")
#
#     if results['total'] > 0:
#         success_rate = results['success'] / results['total'] * 100
#         print(f"成功率: {success_rate:.2f}%")
#
#     # 显示错误详情
#     if results['errors']:
#         print(f"\n=== 错误详情 (显示前10个) ===")
#         for i, error in enumerate(results['errors'][:10]):
#             print(f"{i+1}. {error}")
#
#         if len(results['errors']) > 10:
#             print(f"... 还有 {len(results['errors']) - 10} 个错误")
#
# def main():
#     """
#     主函数
#     """
#     print("开始更新数据库中的video_link字段...")
#
#     # Excel文件路径
#     excel_file = "D:\\PycharmProjects\\resource_recommendation\\backend\\data\\初二下数学.xlsx"
#
#     # 1. 读取Excel文件
#     df = read_excel_data(excel_file)
#     if df.empty:
#         print("没有读取到数据，程序退出")
#         return
#
#     # 2. 准备更新数据
#     update_data = prepare_update_data(df)
#     if not update_data:
#         print("没有准备到更新数据，程序退出")
#         return
#
#     # 3. 创建数据库连接
#     db = create_db_session()
#     if not db:
#         print("无法连接数据库，程序退出")
#         return
#
#     try:
#         # 4. 检查哪些course_id存在于数据库中
#         existing_data, missing_ids = check_existing_courses(db, update_data)
#         if not existing_data:
#             print("没有找到可以更新的记录，程序退出")
#             return
#
#         # 5. 确认更新
#         print(f"\n准备更新 {len(existing_data)} 条记录的video_link字段")
#         confirm = input("是否继续？(y/N): ").strip().lower()
#         if confirm not in ['y', 'yes']:
#             print("用户取消更新")
#             return
#
#         # 6. 执行更新
#         print("\n开始更新数据库...")
#         results = update_video_links(db, existing_data)
#
#         # 7. 打印结果
#         print_update_results(results)
#
#         print("\n更新完成！")
#
#     finally:
#         db.close()
#
# if __name__ == "__main__":
#     main()
import json

with open("output.json", "r", encoding="utf-8") as f:
    course_data = json.load(f)
target_str = json.dumps(
    course_data,
    ensure_ascii=False,  # 关键：中文不转义（如"初中数学"不变成"\u521d\u4e2d\u6570\u5b66"）
    separators=(',', ':')  # 关键：去除逗号后空格（, 变为 ,）、冒号后空格（: 变为 :），压缩成单行
)

# 3. （可选）如果需要外层包裹双引号（如之前示例的 "{...}"），执行这一步
final_str = f'"{target_str}"'

# 4. 输出结果（直接复制即可用）
print("转换后的目标格式：")
print(final_str)