#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import glob

def clean_build_files():
    """
    清理构建文件
    """
    print("清理构建文件...")
    
    # 要清理的目录和文件模式
    clean_patterns = [
        "build/",
        "dist/",
        "*.egg-info/",
        "**/*.c",
        "**/*.so",
        "**/__pycache__/",
        "**/*.pyc",
    ]
    
    for pattern in clean_patterns:
        if pattern.endswith("/"):
            # 目录
            for path in glob.glob(pattern, recursive=True):
                if os.path.isdir(path):
                    print(f"删除目录: {path}")
                    shutil.rmtree(path, ignore_errors=True)
        else:
            # 文件
            for path in glob.glob(pattern, recursive=True):
                if os.path.isfile(path):
                    print(f"删除文件: {path}")
                    os.remove(path)

def install_dependencies():
    """
    安装编译依赖
    """
    print("安装编译依赖...")
    
    dependencies = [
        "Cython>=0.29.0",
        "numpy",
        "setuptools",
        "wheel",
    ]
    
    for dep in dependencies:
        print(f"安装 {dep}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", dep],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"安装 {dep} 失败: {result.stderr}")
            return False
    
    return True

def compile_cython():
    """
    编译 Cython 扩展
    """
    print("开始编译 Cython 扩展...")
    
    # 构建扩展
    result = subprocess.run(
        [sys.executable, "setup.py", "build_ext", "--inplace"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"编译失败: {result.stderr}")
        return False
    
    print("编译成功!")
    return True

def create_wheel():
    """
    创建 wheel 分发包
    """
    print("创建 wheel 分发包...")
    
    result = subprocess.run(
        [sys.executable, "setup.py", "bdist_wheel"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"创建 wheel 失败: {result.stderr}")
        return False
    
    print("wheel 包创建成功!")
    return True

def remove_source_files():
    """
    删除源代码文件，只保留编译后的文件
    """
    print("删除源代码文件...")
    
    # 保护的文件
    protected_files = [
        "main.py",
        "setup.py",
        "compile.py",
        "requirements.txt",
        "alembic.ini",
        "Dockerfile*",
        "docker-compose*",
        ".env*",
    ]
    
    # 保护的目录
    protected_dirs = [
        "sql/",
        "data/",
        "temp_files/",
        "logs/",
        "build/",
        "dist/",
    ]
    
    # 查找所有 .py 文件
    for py_file in glob.glob("**/*.py", recursive=True):
        should_protect = False
        
        # 检查是否在保护列表中
        for protected in protected_files:
            if protected in py_file or py_file.endswith(protected):
                should_protect = True
                break
        
        # 检查是否在保护目录中
        for protected_dir in protected_dirs:
            if py_file.startswith(protected_dir):
                should_protect = True
                break
        
        # 保留 __init__.py 文件
        if py_file.endswith("__init__.py"):
            should_protect = True
        
        if not should_protect:
            print(f"删除源文件: {py_file}")
            os.remove(py_file)

def verify_compilation():
    """
    验证编译结果
    """
    print("验证编译结果...")
    
    # 检查是否有 .so 文件生成
    so_files = list(glob.glob("**/*.so", recursive=True))
    
    if not so_files:
        print("警告: 没有找到编译后的 .so 文件")
        return False
    
    print(f"找到 {len(so_files)} 个编译后的文件:")
    for so_file in so_files:
        print(f"  - {so_file}")
    
    # 检查 wheel 文件
    wheel_files = list(glob.glob("dist/*.whl"))
    if wheel_files:
        print(f"\n生成的 wheel 文件:")
        for wheel_file in wheel_files:
            print(f"  - {wheel_file}")
    
    return True

def main():
    """
    主编译流程
    """
    print("=== Resource Recommendation Backend Cython 编译工具 ===")
    print()
    
    # 检查是否在正确的目录
    if not os.path.exists("setup.py"):
        print("错误: 请在包含 setup.py 的目录中运行此脚本")
        sys.exit(1)
    
    try:
        # 1. 清理构建文件
        clean_build_files()
        
        # 2. 安装依赖
        if not install_dependencies():
            print("依赖安装失败")
            sys.exit(1)
        
        # 3. 编译 Cython 扩展
        if not compile_cython():
            print("Cython 编译失败")
            sys.exit(1)
        
        # 4. 创建 wheel 包
        if not create_wheel():
            print("wheel 包创建失败")
            sys.exit(1)
        
        # 5. 验证编译结果
        if not verify_compilation():
            print("编译验证失败")
            sys.exit(1)
        
        print("\n=== 编译完成 ===")
        print("\n可选操作:")
        print("1. 运行 'python compile.py --remove-source' 删除源代码文件")
        print("2. 使用 'docker build -f Dockerfile.compile -t app:compiled .' 构建 Docker 镜像")
        
        # 检查是否需要删除源文件
        if "--remove-source" in sys.argv:
            print("\n删除源代码文件...")
            remove_source_files()
            print("源代码文件已删除")
        
    except KeyboardInterrupt:
        print("\n编译被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n编译过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()