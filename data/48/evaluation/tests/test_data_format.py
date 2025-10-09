"""
数据格式规范测试
"""
import pytest
import os
import sys
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder


def test_coordinate_consistency():
    """测试坐标系统一致性"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # 生成迷宫并收集所有坐标
    result = generator.generate('dfs', 10)
    maze_matrix = result['maze_matrix']

    coordinates_to_check = []

    # 收集起点和终点坐标
    start_point = result['start_point']
    end_point = result['end_point']

    coordinates_to_check.append(('start_point', start_point))
    coordinates_to_check.append(('end_point', end_point))

    # 收集路径坐标
    path_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)
    if path_result['found_solution']:
        path = path_result['path']
        for i, coord in enumerate(path[:5]):  # 检查前5个路径点
            coordinates_to_check.append((f'path_point_{i}', coord))

    # 验证所有坐标格式一致性
    format_issues = []

    for coord_name, coord in coordinates_to_check:
        # 检查数据类型 (允许tuple、list或ndarray)
        if not isinstance(coord, (list, np.ndarray, tuple)):
            format_issues.append(f"{coord_name}: 类型不是list、ndarray或tuple，而是{type(coord)}")
            continue

        # 检查长度
        if len(coord) != 2:
            format_issues.append(f"{coord_name}: 长度不是2，而是{len(coord)}")
            continue

        # 检查值类型
        try:
            row, col = int(coord[0]), int(coord[1])
            # 检查坐标范围合理性
            if row < 0 or col < 0:
                format_issues.append(f"{coord_name}: 包含负数坐标[{row}, {col}]")
            if row >= maze_matrix.shape[0] or col >= maze_matrix.shape[1]:
                format_issues.append(f"{coord_name}: 坐标[{row}, {col}]超出迷宫边界")
        except (ValueError, TypeError):
            format_issues.append(f"{coord_name}: 坐标值无法转换为整数: {coord}")

    # 断言没有格式问题
    assert len(format_issues) == 0, f"坐标格式问题: {format_issues}"


def test_maze_matrix_format():
    """测试迷宫矩阵格式一致性"""
    generator = MazeGenerator()

    # 测试不同算法生成的迷宫格式
    algorithms = ['dfs', 'prim']
    format_issues = []

    for algo in algorithms:
        try:
            result = generator.generate(algo, 10)
            maze_matrix = result['maze_matrix']

            # 检查数据类型
            if not isinstance(maze_matrix, np.ndarray):
                format_issues.append(f"{algo}: 迷宫矩阵不是numpy数组，而是{type(maze_matrix)}")
                continue

            # 检查数据类型
            if maze_matrix.dtype != np.uint8:
                format_issues.append(f"{algo}: 数据类型不是uint8，而是{maze_matrix.dtype}")

            # 检查维度
            if len(maze_matrix.shape) != 2:
                format_issues.append(f"{algo}: 不是2D数组，而是{len(maze_matrix.shape)}D")

            # 检查值范围
            unique_values = np.unique(maze_matrix)
            invalid_values = [v for v in unique_values if v not in [0, 1]]
            if invalid_values:
                format_issues.append(f"{algo}: 包含无效值{invalid_values}，应该只有0和1")

        except Exception as e:
            format_issues.append(f"{algo}: 生成迷宫时出错: {e}")

    assert len(format_issues) == 0, f"迷宫矩阵格式问题: {format_issues}"


def test_path_data_format():
    """测试路径数据格式一致性"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # 生成测试迷宫
    result = generator.generate('dfs', 12)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # 测试不同算法的路径数据格式
    algorithms = ['dfs', 'bfs', 'astar']
    format_issues = []

    for algo in algorithms:
        try:
            path_result = path_finder.solve(algo, maze_matrix, start_point, end_point)

            if not path_result['found_solution']:
                continue  # 跳过未找到解决方案的情况

            path = path_result['path']

            # 检查路径是列表
            if not isinstance(path, list):
                format_issues.append(f"{algo}: 路径不是列表，而是{type(path)}")
                continue

            # 检查路径点格式
            for i, point in enumerate(path[:3]):  # 检查前3个点
                if not isinstance(point, (list, np.ndarray, tuple)):
                    format_issues.append(f"{algo}: 路径点{i}类型错误: {type(point)}")
                    continue

                if len(point) != 2:
                    format_issues.append(f"{algo}: 路径点{i}长度不是2: {len(point)}")

                try:
                    row, col = int(point[0]), int(point[1])
                except (ValueError, TypeError):
                    format_issues.append(f"{algo}: 路径点{i}无法转换为整数: {point}")

            # 检查统计数据类型
            if not isinstance(path_result['path_length'], int):
                format_issues.append(f"{algo}: path_length不是整数: {type(path_result['path_length'])}")

            if not isinstance(path_result['explored_nodes_count'], int):
                format_issues.append(f"{algo}: explored_nodes_count不是整数: {type(path_result['explored_nodes_count'])}")

            if not isinstance(path_result['search_time'], (int, float)):
                format_issues.append(f"{algo}: search_time不是数值: {type(path_result['search_time'])}")

        except Exception as e:
            format_issues.append(f"{algo}: 路径搜索时出错: {e}")

    assert len(format_issues) == 0, f"路径数据格式问题: {format_issues}"
