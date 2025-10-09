"""
环境验证测试
"""
import pytest
import os
import sys
import importlib.util


def test_core_modules_exist():
    """测试核心模块文件存在性"""
    # 添加src目录到路径
    src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
    sys.path.insert(0, src_path)

    # 核心文件列表
    core_files = [
        'maze_generator.py',
        'path_finder.py',
        'maze_validator.py',
        'algorithms/dfs_generator.py',
        'algorithms/prim_generator.py',
        'algorithms/dfs_solver.py',
        'algorithms/bfs_solver.py',
        'algorithms/astar_solver.py',
        'utils/data_manager.py',
        'utils/performance.py'
    ]

    # 检查文件存在性
    missing_files = []
    for file_path in core_files:
        full_path = os.path.join(src_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)

    assert len(missing_files) == 0, f"缺少核心文件: {missing_files}"

    # 尝试导入模块
    import_errors = []

    try:
        import maze_generator
        import path_finder
        import maze_validator
        from algorithms import dfs_generator, prim_generator
        from algorithms import dfs_solver, bfs_solver, astar_solver
        from utils import data_manager, performance
    except ImportError as e:
        import_errors.append(str(e))

    assert len(import_errors) == 0, f"导入错误: {import_errors}"


def test_numpy_available():
    """测试numpy依赖可用性"""
    try:
        import numpy as np
        version = np.__version__
        # 检查版本是否合理
        major, minor = version.split('.')[:2]
        assert int(major) >= 1, f"numpy版本过低: {version}"
    except ImportError:
        pytest.fail("numpy无法导入")
    except Exception as e:
        pytest.fail(f"numpy检查失败: {e}")
