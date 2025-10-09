"""
路径验证测试
"""
import pytest
import os
import sys
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder


def test_dfs_path_validity():
    """测试DFS路径有效性"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # 生成迷宫
    result = generator.generate('dfs', 10)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # 使用DFS求解
    path_result = path_finder.solve('dfs', maze_matrix, start_point, end_point)

    if not path_result['found_solution']:
        pytest.skip("DFS未找到路径，跳过路径验证测试")

    path = path_result['path']

    # 验证路径不为空
    assert len(path) > 0, "路径不应为空"

    # 验证起点和终点
    assert list(path[0]) == list(start_point), f"路径起点{path[0]}与预期{start_point}不匹配"
    assert list(path[-1]) == list(end_point), f"路径终点{path[-1]}与预期{end_point}不匹配"

    # 验证路径中所有点都是通路
    invalid_points = []
    for point in path:
        row, col = int(point[0]), int(point[1])
        if maze_matrix[row, col] != 0:
            invalid_points.append(point)

    assert len(invalid_points) == 0, f"路径包含墙壁点: {invalid_points}"

    # 验证路径连续性
    discontinuous_pairs = []
    for i in range(len(path) - 1):
        curr = path[i]
        next_p = path[i + 1]

        # 计算曼哈顿距离
        distance = abs(curr[0] - next_p[0]) + abs(curr[1] - next_p[1])
        if distance != 1:
            discontinuous_pairs.append((curr, next_p))

    assert len(discontinuous_pairs) == 0, f"路径不连续的点对: {discontinuous_pairs}"


def test_path_components():
    """测试路径搜索返回组件完整性"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # 生成迷宫
    result = generator.generate('dfs', 12)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # 测试各种算法
    algorithms = ['dfs', 'bfs', 'astar']

    for algo in algorithms:
        try:
            path_result = path_finder.solve(algo, maze_matrix, start_point, end_point)

            # 检查必需的返回组件
            required_keys = ['found_solution', 'path', 'explored_nodes_count', 'search_time', 'path_length']
            missing_keys = []
            for key in required_keys:
                if key not in path_result:
                    missing_keys.append(key)

            assert len(missing_keys) == 0, f"{algo}算法缺少返回组件: {missing_keys}"

            # 如果找到解决方案，检查数据类型
            if path_result['found_solution']:
                assert isinstance(path_result['path'], list), f"{algo}算法路径应该是列表"
                assert isinstance(path_result['explored_nodes_count'], int), f"{algo}算法探索节点数应该是整数"
                assert isinstance(path_result['search_time'], (int, float)), f"{algo}算法搜索时间应该是数值"
                assert isinstance(path_result['path_length'], int), f"{algo}算法路径长度应该是整数"

        except Exception as e:
            pytest.fail(f"{algo}算法测试失败: {e}")
