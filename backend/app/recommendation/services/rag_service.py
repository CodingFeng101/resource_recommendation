#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Dict, Any

from sklearn.metrics.pairwise import cosine_similarity

from backend.app.recommendation.crud.course import course_dao
from backend.app.recommendation.crud.report import report_dao
from backend.app.recommendation.crud.report_embedding import report_embedding_dao
from backend.app.recommendation.crud.summary_embedding import summary_embedding_dao
from backend.app.recommendation.crud.video_summary import video_summary_dao
from backend.app.recommendation.schema import CourseCreate, CourseUpdate, VideoSummaryCreate, SummaryEmbeddingCreate, \
    ReportCreate, ReportEmbeddingCreate
from backend.common.core.llm.response_getter import GenericResponseGetter
from backend.common.core.rag.build_index.dialogue_process.dialogue_process import DialogueProcessor
from backend.database.db_mysql import async_db_session
import json
import numpy as np



class RagService:
    """
    提供RAG(检索增强生成)相关的数据处理服务
    处理课程对话数据，生成摘要、报告和嵌入向量
    """
    
    def __init__(self):
        self.dialogue_processor = DialogueProcessor()
    
    @staticmethod
    async def process_course_data(*, course_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理课程数据
        
        Args:
            course_data: 课程数据列表
            
        Returns:
            处理结果统计
        """
        service = RagService()
        
        results = {
            "total_items": len(course_data),
            "processed_items": 0,
            "failed_items": 0,
            "errors": []
        }
        
        for index, item in enumerate(course_data):
            try:
                print("已完成:", index)
                await service._process_single_course(item)
                results["processed_items"] += 1
            except Exception as e:
                results["failed_items"] += 1
                results["errors"].append({
                    "index": index,
                    "error": str(e),
                    "course_id": str(item.get("course_id", "unknown"))
                })

        return results

    async def _process_single_course(self, item: Dict[str, Any]) -> None:
        """处理单个课程数据"""
        course_id = item.get("id")
        resource_name = item.get("class_name")
        version = item.get("version", "")
        book_name = item.get("book_name", "")
        chapter_name = item.get("chapter_name", "")
        grade = item.get("level")
        subject = item.get("disciplines")
        video_link = item.get("down_url")
        dialogue = item.get("identification_result", [])

        async with async_db_session.begin() as db:
            course_create = CourseCreate(
                course_id=course_id,
                resource_name=resource_name,
                version=version,
                book_name=book_name,
                chapter_name=chapter_name,
                grade=grade,
                subject=subject,
                video_link=video_link,
                dialogue=dialogue,
                learning_objectives=None,
                learning_style_preference=None,
                knowledge_level_self_assessment=None
            )

            course = await course_dao.create_async(db, obj_in=course_create)
            course_uuid = course.uuid

            # 处理对话数据
            if dialogue:
                processed_result = await self.dialogue_processor.process(dialogue)
                # 从label_with_embedding中提取字段更新course表
                if processed_result.get("label_with_embedding"):
                    labels = processed_result["label_with_embedding"]
                    update_data = CourseUpdate(
                        learning_objectives=labels.get("learning_objectives"),
                        learning_style_preference=labels.get("learning_style_preference"),
                        knowledge_level_self_assessment=labels.get("knowledge_level_self_assessment")
                    )
                    await course_dao.update_async(db, db_obj=course, obj_in=update_data)

                # 处理label_with_embedding中的summary和summary_embedding，分别存入video_summary和summary_embedding表
                if processed_result.get("label_with_embedding"):
                    label_data = processed_result["label_with_embedding"]

                    if "class_summary" in label_data:
                        video_summary_create = VideoSummaryCreate(
                            course_uuid=course_uuid,
                            video_summary=label_data["class_summary"]
                        )
                        video_summary = await video_summary_dao.create_async(db, obj_in=video_summary_create)

                        # 将summary_embedding存入summary_embedding表
                        if "summary_embedding" in label_data:
                            embedding_create = SummaryEmbeddingCreate(
                                video_summary_uuid=video_summary.uuid,
                                vector=label_data["summary_embedding"]
                            )
                            await summary_embedding_dao.create_async(db, obj_in=embedding_create)

                # 处理report_with_embedding数据，存入report和report_embedding表
                if processed_result.get("report_with_embedding"):
                    reports = processed_result["report_with_embedding"]

                    for report_data in reports:
                        # 将report数据存入report表
                        report_create = ReportCreate(
                            course_uuid=course_uuid,
                            start_time=report_data.get("start_time"),
                            end_time=report_data.get("end_time"),
                            duration=report_data.get("duration"),
                            segment_topic=report_data.get("segment_topic"),
                            key_points=report_data.get("key_points")
                        )
                        report = await report_dao.create_async(db, obj_in=report_create)

                        # 将report_embedding存入report_embedding表
                        if "segment_topic_embedding" in report_data:
                            report_embedding_create = ReportEmbeddingCreate(
                                report_uuid=report.uuid,
                                vector=report_data["segment_topic_embedding"]
                            )
                            await report_embedding_dao.create_async(db, obj_in=report_embedding_create)

    @staticmethod
    async def ask_recommendation(*, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        根据查询向量从summary_embeddings表中检索最相似的top_k个summary，并返回对应的完整课程信息，
        同时包含每个课程最相似的报告信息
        
        Args:
            query: 用户查询字符串
            top_k: 返回的最相似课程数量
            
        Returns:
            包含完整课程信息和最相似报告信息的列表，按相似度排序
        """
        
        llm = GenericResponseGetter()
        
        # 1. 将查询向量化
        query_embedding = await llm.get_vector(query=query)
        query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        
        async with async_db_session.begin() as db:
            # 2. 获取所有summary_embeddings和对应的video_summary
            all_embeddings = await summary_embedding_dao.get_all_async(db)
            
            if not all_embeddings:
                return []
            
            similarities = []
            similarity_threshold = 0
            # 3. 计算每个summary与查询的相似度
            for embedding in all_embeddings:
                try:
                    # 解析存储的向量字符串
                    vector_data = json.loads(embedding.vector)
                    embedding_vector = np.array(vector_data, dtype=np.float32).reshape(1, -1)
                    
                    # 计算余弦相似度
                    similarity = float(cosine_similarity(query_vector, embedding_vector))
                    if similarity < similarity_threshold:
                        continue
                    similarities.append((embedding, similarity))
                    
                except (json.JSONDecodeError, ValueError) as e:
                    continue
            
            # 4. 按相似度排序并获取top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_k_embeddings = similarities[:top_k]
            
            results = []
            
            # 5. 获取对应的课程信息和最相似的报告
            for embedding, similarity in top_k_embeddings:
                try:
                    # 获取video_summary
                    video_summary = await video_summary_dao.get_async(db, uuid=embedding.video_summary_uuid)
                    if not video_summary:
                        continue
                    
                    # 获取对应的课程
                    course = await course_dao.get_async(db, uuid=video_summary.course_uuid)
                    if not course:
                        continue
                    
                    # 获取该课程的所有报告
                    reports = await report_dao.get_by_course_uuid_async(db, course_uuid=course.uuid)
                    
                    # 计算所有报告的相似度，找出最相似的一个
                    report_similarities = []
                    
                    for report in reports:
                        # 获取对应的report_embedding
                        report_embeddings = await report_embedding_dao.get_by_report_uuid_async(db, report_uuid=report.uuid)
                        
                        if not report_embeddings:
                            continue
                        
                        # 可能有多个embedding，取第一个
                        report_embedding = report_embeddings[0] if report_embeddings else None
                        if not report_embedding:
                            continue
                        
                        try:
                            # 解析存储的向量字符串
                            vector_data = json.loads(report_embedding.vector)
                            report_vector = np.array(vector_data, dtype=np.float32).reshape(1, -1)
                            
                            # 计算余弦相似度
                            report_similarity = float(cosine_similarity(query_vector, report_vector))
                            
                            # 记录所有报告的相似度
                            report_similarities.append({
                                "report": report,
                                "similarity": report_similarity
                            })
                        
                        except (json.JSONDecodeError, ValueError) as e:
                            continue
                    
                    # 找出相似度最高的报告
                    best_report = None
                    if report_similarities:
                        # 按相似度排序，取最高的
                        report_similarities.sort(key=lambda x: x["similarity"], reverse=True)
                        top_report = report_similarities[0]
                        
                        best_report = {
                            "report_uuid": top_report["report"].uuid,
                            "start_time": top_report["report"].start_time,
                            "end_time": top_report["report"].end_time,
                            "duration": top_report["report"].duration,
                            "segment_topic": top_report["report"].segment_topic,
                            "key_points": top_report["report"].key_points,
                            "similarity_score": top_report["similarity"]
                        }
                    
                    # 构建完整的课程信息，包含最相似的报告
                    course_info = {
                        "course_uuid": course.uuid,
                        "course_id": course.course_id,
                        "resource_name": course.resource_name,
                        "version": course.version,
                        "book_name": course.book_name,
                        "chapter_name": course.chapter_name,
                        "grade": course.grade,
                        "subject": course.subject,
                        "video_link": course.video_link,
                        "learning_objectives": course.learning_objectives,
                        "learning_style_preference": course.learning_style_preference,
                        "knowledge_level_self_assessment": course.knowledge_level_self_assessment,
                        "video_summary": video_summary.video_summary,
                        "start_time": best_report.get("start_time") if best_report else None,
                        "end_time": best_report.get("end_time") if best_report else None,
                    }
                    
                    results.append(course_info)
                    
                except Exception as e:
                    continue
            
            return results

    @staticmethod
    async def ask_resource(*, course_uuid: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        根据课程ID和查询向量从report_embeddings表中检索最相似的top_k个report
        
        Args:
            course_uuid: 课程UUID
            query: 用户查询字符串
            top_k: 返回的最相似报告数量
            
        Returns:
            包含报告信息和相似度评分的列表，按相似度排序
        """
        llm = GenericResponseGetter()
        
        # 1. 将查询向量化
        query_embedding = await llm.get_vector(query=query)
        query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        
        async with async_db_session.begin() as db:
            # 2. 根据课程ID获取课程
            course = await course_dao.get_by_course_id_async(db, course_uuid=course_uuid)
            if not course:
                return []
            
            # 3. 获取该课程的所有报告
            reports = await report_dao.get_by_course_uuid_async(db, course_uuid=course.uuid)
            
            if not reports:
                return []
            
            similarities = []
            similarity_threshold = 0
            # 4. 计算每个报告的embedding与查询的相似度
            for report in reports:
                # 获取对应的report_embedding
                report_embeddings = await report_embedding_dao.get_by_report_uuid_async(db, report_uuid=report.uuid)
                
                if not report_embeddings:
                    continue
                
                # 可能有多个embedding，取第一个
                embedding = report_embeddings[0] if report_embeddings else None
                if not embedding:
                    continue
                
                try:
                    # 解析存储的向量字符串
                    vector_data = json.loads(embedding.vector)
                    embedding_vector = np.array(vector_data, dtype=np.float32).reshape(1, -1)
                    
                    # 计算余弦相似度
                    similarity = float(cosine_similarity(query_vector, embedding_vector))
                    if similarity < similarity_threshold:
                        continue
                    # 构建报告信息
                    report_info = {
                        "report_uuid": str(report.uuid),
                        "start_time": report.start_time,
                        "end_time": report.end_time,
                        "duration": report.duration,
                        "segment_topic": report.segment_topic,
                        "key_points": report.key_points,
                        "similarity_score": similarity
                    }
                    
                    similarities.append(report_info)
                    
                except (json.JSONDecodeError, ValueError) as e:
                    continue
            
            # 5. 按相似度排序并返回top_k
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similarities[:top_k]


rag_service = RagService()