"""
迷宫生成测试
"""
import pytest
import os
import sys
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder


def test_dfs_connectivity():
    """测试DFS迷宫连通性"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    connected_count = 0
    total_tests = 5

    for i in range(total_tests):
        # 生成迷宫
        result = generator.generate('dfs', 10)

        maze_matrix = result['maze_matrix']
        start_point = result['start_point']
        end_point = result['end_point']

        # 检查连通性
        path_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)

        if path_result['found_solution']:
            connected_count += 1

    # 至少4个迷宫应该是连通的
    assert connected_count >= 4, f"只有 {connected_count}/{total_tests} 个迷宫连通"


def test_prim_connectivity():
    """测试PRIM迷宫连通性"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    connected_count = 0
    total_tests = 5

    for i in range(total_tests):
        # 生成迷宫
        result = generator.generate('prim', 10)

        maze_matrix = result['maze_matrix']
        start_point = result['start_point']
        end_point = result['end_point']

        # 检查连通性
        path_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)

        if path_result['found_solution']:
            connected_count += 1

    # 至少4个迷宫应该是连通的
    assert connected_count >= 4, f"只有 {connected_count}/{total_tests} 个迷宫连通"


def test_maze_format():
    """测试迷宫格式正确性"""
    generator = MazeGenerator()

    # 测试DFS
    result = generator.generate('dfs', 10)
    maze_matrix = result['maze_matrix']

    # 检查类型和形状
    assert isinstance(maze_matrix, np.ndarray), "迷宫矩阵应该是numpy数组"
    assert maze_matrix.dtype == np.uint8, f"数据类型应该是uint8，实际是{maze_matrix.dtype}"
    assert len(maze_matrix.shape) == 2, "迷宫应该是2D数组"

    # 检查值范围
    unique_values = np.unique(maze_matrix)
    assert all(val in [0, 1] for val in unique_values), f"迷宫值应该只包含0和1，实际包含{unique_values}"

    # 检查必需的返回组件
    required_keys = ['maze_matrix', 'generation_time', 'start_point', 'end_point']
    for key in required_keys:
        assert key in result, f"缺少必需的返回组件: {key}"
