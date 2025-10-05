from setuptools import setup, Extension
from Cython.Build import cythonize
from pathlib import Path

# 1. 需要编译的目录和文件
SRC_PATHS = [
    "common/core/unigraph/implementation/module/sapperrag"
]

# 2. 排除的文件或文件夹
EXCLUDE_FILES = []

# 3. 查找所有 .py 文件并创建 Extension 对象
extensions = []
for p_str in SRC_PATHS:
    path = Path(p_str)
    if path.is_dir():
        # 遍历目录
        for py_file in path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            # 检查文件是否在排除列表中
            if any(py_file.is_relative_to(Path(exclude)) for exclude in EXCLUDE_FILES):
                continue
            # 将文件路径转换为模块路径 (e.g., common/a/b.py -> common.a.b)
            module_path = ".".join(py_file.with_suffix("").parts)
            extensions.append(Extension(module_path, [str(py_file)]))
    elif path.is_file() and path.suffix == '.py':
        # 处理单个文件
        module_path = ".".join(path.with_suffix("").parts)
        extensions.append(Extension(module_path, [str(path)]))

print(f"Found {len(extensions)} Python files to compile into extensions.")

# 4. 使用 setuptools 进行编译
setup(
    name="core_module",
    packages=[],  # 明确禁用包发现
    py_modules=[],  # 明确禁用模块发现
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level': "3"}
    ) if extensions else [],
    zip_safe=False,
)