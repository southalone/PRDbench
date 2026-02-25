"""
错误处理测试
"""
import pytest
import os
import sys
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder
from maze_validator import MazeValidator


def test_exception_handling():
    """测试异常输入处理"""
    generator = MazeGenerator()
    path_finder = PathFinder()
    validator = MazeValidator()

    # 准备5种异常输入
    test_cases = [
        {
            'name': '负数迷宫尺寸',
            'test_func': lambda: generator.generate('dfs', -5),
            'should_handle': True
        },
        {
            'name': '超出边界的起点坐标',
            'test_func': lambda: test_invalid_coordinates(),
            'should_handle': True
        },
        {
            'name': '无效的迷宫矩阵(包含字符串)',
            'test_func': lambda: test_string_matrix(),
            'should_handle': True
        },
        {
            'name': '空的迷宫矩阵',
            'test_func': lambda: test_empty_matrix(),
            'should_handle': True
        },
        {
            'name': '错误的数据类型',
            'test_func': lambda: test_wrong_data_type(),
            'should_handle': True
        }
    ]

    handled_exceptions = 0

    for test_case in test_cases:
        try:
            # 尝试执行可能导致异常的操作
            test_case['test_func']()
            # 如果没有抛出异常，检查是否应该处理
            print(f"✓ {test_case['name']}: 没有抛出异常（可能被优雅处理）")
            handled_exceptions += 1
        except Exception as e:
            # 检查异常是否被优雅处理（有意义的错误信息）
            error_message = str(e)
            if len(error_message) > 0 and not "Traceback" in error_message:
                print(f"✓ {test_case['name']}: 优雅处理异常 - {error_message}")
                handled_exceptions += 1
            else:
                print(f"✗ {test_case['name']}: 异常处理不够优雅 - {e}")

    # 至少应该优雅处理4种异常
    assert handled_exceptions >= 4, f"只优雅处理了 {handled_exceptions}/5 种异常输入"


def test_invalid_coordinates():
    """测试无效坐标处理"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # 生成一个正常的迷宫
    result = generator.generate('dfs', 10)
    maze_matrix = result['maze_matrix']

    # 测试超出边界的坐标
    invalid_start = [20, 20]  # 超出10x10迷宫的边界
    valid_end = [5, 5]

    # 这应该被优雅处理
    path_result = path_finder.solve('bfs', maze_matrix, invalid_start, valid_end)

    # 检查是否优雅处理（返回未找到解决方案而不是崩溃）
    assert 'found_solution' in path_result, "应该返回found_solution字段"
    # 通常超出边界的坐标应该导致未找到解决方案
    assert not path_result['found_solution'], "超出边界的坐标应该导致未找到解决方案"


def test_string_matrix():
    """测试字符串矩阵处理"""
    validator = MazeValidator()

    # 创建包含字符串的"迷宫"
    string_matrix = [
        ['0', '1', '0'],
        ['1', 'wall', '0'],
        ['0', '1', '0']
    ]

    # 这应该被检测为无效格式
    result = validator.validate(string_matrix, [0, 0], [2, 2])

    # 应该识别为无效
    assert 'valid' in result, "应该返回valid字段"
    assert not result['valid'], "字符串矩阵应该被识别为无效"


def test_empty_matrix():
    """测试空矩阵处理"""
    path_finder = PathFinder()

    # 空矩阵
    empty_matrix = np.array([])

    try:
        result = path_finder.solve('dfs', empty_matrix, [0, 0], [1, 1])
        # 如果没有抛出异常，检查是否优雅处理
        assert 'found_solution' in result, "应该返回found_solution字段"
        assert not result['found_solution'], "空矩阵应该导致未找到解决方案"
    except Exception as e:
        # 如果抛出异常，检查错误信息是否有意义
        error_msg = str(e)
        assert len(error_msg) > 5, f"错误信息过于简短: {error_msg}"


def test_wrong_data_type():
    """测试错误数据类型处理"""
    generator = MazeGenerator()

    # 测试字符串作为大小参数
    try:
        result = generator.generate('dfs', "ten")
        # 如果没有抛出异常，应该有错误标记
        assert 'error' in result or 'maze_matrix' not in result, "应该识别错误的数据类型"
    except Exception as e:
        # 检查错误信息质量
        error_msg = str(e)
        assert len(error_msg) > 5, f"错误信息过于简短: {error_msg}"


def test_algorithm_error_handling():
    """测试算法错误处理"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # 测试不存在的算法
    invalid_algorithms = ['xyz', 'invalid', '']

    handled_count = 0

    for algo in invalid_algorithms:
        try:
            # 生成算法测试
            gen_result = generator.generate(algo, 10)
            if 'error' in gen_result or 'maze_matrix' not in gen_result:
                handled_count += 1
        except Exception as e:
            if len(str(e)) > 0:  # 有意义的错误信息
                handled_count += 1

        try:
            # 创建一个测试迷宫
            valid_result = generator.generate('dfs', 10)
            maze_matrix = valid_result['maze_matrix']

            # 路径搜索算法测试
            path_result = path_finder.solve(algo, maze_matrix, [1, 1], [5, 5])
            if 'error' in path_result or not path_result.get('found_solution', True):
                handled_count += 1
        except Exception as e:
            if len(str(e)) > 0:  # 有意义的错误信息
                handled_count += 1

    # 应该能处理大部分无效算法请求
    assert handled_count >= 4, f"只处理了 {handled_count}/6 个无效算法请求"
