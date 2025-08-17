#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from ....services.rag_service import rag_service

rag_router = APIRouter()


@rag_router.post("/process", summary="批量处理课程数据")
async def process_course_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        result = await rag_service.process_course_data(course_data=data)
        return {
            "code": 200,
            "msg": "处理完成",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rag_router.get("/search/courses", summary="根据查询搜索相似课程")
async def search_similar_courses(query: str = Query(..., description="搜索查询字符串")) -> Dict[str, Any]:
    """
    根据用户查询字符串搜索最相似的课程
    
    - **query**: 用户输入的搜索查询
    """
    try:
        results = await rag_service.ask_recommendation(query=query)
        return {
            "code": 200,
            "msg": "搜索完成",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rag_router.get("/search/reports/{course_uuid}", summary="根据课程ID搜索相似报告")
async def search_similar_reports(
    course_uuid: str,
    query: str = Query(..., description="搜索查询字符串"),
) -> Dict[str, Any]:
    """
    根据课程ID和查询字符串搜索该课程下最相似的报告
    
    - **course_id**: 课程的唯一标识符
    - **query**: 用户输入的搜索查询
    """
    try:
        results = await rag_service.ask_resource(
            course_uuid=course_uuid,
            query=query
        )
        return {
            "code": 200,
            "msg": "搜索完成",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

