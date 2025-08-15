#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter
from backend.app.recommendation.api.v1.recommendation import router as recommendation_router

# 创建主API路由器
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(
    recommendation_router,
    prefix="/v1",
    tags=["recommendation"]
)
