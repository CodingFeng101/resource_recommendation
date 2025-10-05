#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy
import os
import sys
import glob
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('compile.log', mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 需要编译的核心模块路径
CORE_MODULES = [
    # 推荐系统核心逻辑
    "app/recommendation/services/*.py",
    "app/recommendation/crud/*.py", 
    "app/recommendation/schema/*.py",
    
    # 数据库和工具模块
    "database/*.py",
    "utils/*.py",
    
    # 核心配置和通用模块
    "core/*.py",
    "common/core/*.py",
    "common/model.py",
    "common/schema.py",
]

# 排除不需要编译的文件
EXCLUDE_FILES = [
    "__init__.py",
    "main.py",  # 入口文件保持 Python 格式
    "*test*.py",  # 测试文件
    "*demo*.py",  # 演示文件
]

def get_py_files():
    """
    获取需要编译的 Python 文件列表
    """
    py_files = []
    
    try:
        for pattern in CORE_MODULES:
            logger.info(f"处理模块模式: {pattern}")
            
            try:
                files = glob.glob(pattern, recursive=True)
                logger.info(f"在模式 {pattern} 中找到 {len(files)} 个文件")
                
                for file in files:
                    try:
                        # 检查是否在排除列表中
                        should_exclude = False
                        for exclude_pattern in EXCLUDE_FILES:
                            if exclude_pattern in os.path.basename(file):
                                should_exclude = True
                                logger.debug(f"排除文件: {file} (匹配模式: {exclude_pattern})")
                                break
                        
                        if not should_exclude and file.endswith('.py'):
                            py_files.append(file)
                            logger.info(f"添加编译文件: {file}")
                    except Exception as e:
                        logger.error(f"处理文件 {file} 时出错: {e}")
                        
            except Exception as e:
                logger.error(f"处理模式 {pattern} 时出错: {e}")
        
        logger.info(f"总共找到 {len(py_files)} 个需要编译的 Python 文件")
        return py_files
        
    except Exception as e:
        logger.error(f"获取 Python 文件列表时出错: {e}")
        raise

def create_extension_modules():
    """
    创建 Cython 扩展模块
    """
    try:
        py_files = get_py_files()
        
        if not py_files:
            logger.warning("没有找到需要编译的 Python 文件")
            return []
        
        # 编译选项
        compiler_directives = {
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'initializedcheck': False,
            'cdivision': True,
            'embedsignature': True,
        }
        
        logger.info(f"开始 Cython 编译，编译选项: {compiler_directives}")
        
        try:
            extensions = cythonize(
                py_files,
                compiler_directives=compiler_directives,
                build_dir="build",
                language_level=3
            )
            
            logger.info(f"成功创建 {len(extensions)} 个扩展模块")
            return extensions
            
        except Exception as e:
            logger.error(f"Cython 编译失败: {e}")
            raise
            
    except Exception as e:
        logger.error(f"创建扩展模块时出错: {e}")
        raise

class CustomBuildExt(build_ext):
    """
    自定义构建扩展类
    """
    def build_extensions(self):
        try:
            logger.info(f"开始构建 {len(self.extensions)} 个扩展模块")
            logger.info(f"编译器类型: {self.compiler.compiler_type}")
            
            # 添加编译选项
            if self.compiler.compiler_type == 'msvc':
                logger.info("使用 MSVC 编译器优化选项")
                for ext in self.extensions:
                    ext.extra_compile_args = ['/O2', '/Ob2']
            else:
                logger.info("使用 GCC/Clang 编译器优化选项")
                for ext in self.extensions:
                    ext.extra_compile_args = ['-O3', '-ffast-math']
                    ext.extra_link_args = ['-s']  # 去除符号表
            
            super().build_extensions()
            logger.info("扩展模块构建完成")
            
        except Exception as e:
            logger.error(f"构建扩展模块时出错: {e}")
            raise

# 读取依赖
def get_requirements():
    """
    读取 requirements.txt 文件
    """
    try:
        logger.info("读取 requirements.txt 文件")
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            logger.info(f"找到 {len(requirements)} 个依赖包")
            return requirements
    except FileNotFoundError:
        logger.warning("未找到 requirements.txt 文件，使用空依赖列表")
        return []
    except Exception as e:
        logger.error(f"读取 requirements.txt 文件时出错: {e}")
        return []

setup(
    name="resource-recommendation-backend",
    version="1.0.0",
    description="Resource Recommendation Backend - Compiled Version",
    author="Development Team",
    packages=find_packages(),
    
    # Cython 扩展模块
    ext_modules=create_extension_modules(),
    
    # 自定义构建命令
    cmdclass={'build_ext': CustomBuildExt},
    
    # 包含数据文件
    include_package_data=True,
    package_data={
        '': ['*.json', '*.yml', '*.yaml', '*.txt', '*.md', '*.sql', '*.ini'],
    },
    
    # 依赖
    install_requires=get_requirements() + ['Cython>=0.29.0', 'numpy'],
    
    # Python 版本要求
    python_requires='>=3.10',
    
    # 包含目录
    include_dirs=[numpy.get_include()],
    
    # ZIP 安全
    zip_safe=False,
    
    # 分类信息
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)