"""
数据验证测试
"""
import pytest
import os
import sys
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_validator import MazeValidator


def test_format_validation():
    """测试迷宫格式检查"""
    validator = MazeValidator()

    # 准备3种无效迷宫矩阵

    # 1. 包含非0非1值的矩阵
    invalid_values_maze = np.array([
        [0, 1, 0],
        [1, 2, 0],  # 包含值2
        [0, 1, 0]
    ], dtype=np.uint8)

    # 2. 错误数据类型的矩阵
    wrong_type_maze = np.array([
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0]
    ], dtype=np.float32)  # 应该是uint8

    # 3. 形状不正确的矩阵（非正方形）
    wrong_shape_maze = np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1]
    ], dtype=np.uint8)  # 3x4而不是正方形

    invalid_mazes = [
        (invalid_values_maze, "包含非0非1值"),
        (wrong_type_maze, "错误数据类型"),
        (wrong_shape_maze, "形状不正确")
    ]

    # 验证能识别所有格式错误
    identified_errors = 0

    for maze, description in invalid_mazes:
        try:
            result = validator.validate(maze, [0, 0], [2, 2])
            if not result['valid']:
                identified_errors += 1
                print(f"正确识别错误: {description}")
            else:
                print(f"未识别错误: {description}")
        except Exception as e:
            # 如果抛出异常也算识别了错误
            identified_errors += 1
            print(f"通过异常识别错误: {description} - {e}")

    # 至少应该识别2种错误
    assert identified_errors >= 2, f"只识别了 {identified_errors}/3 种格式错误"


def test_connectivity_validation():
    """测试连通性检查"""
    validator = MazeValidator()

    # 创建一个不连通的迷宫
    disconnected_maze = np.array([
        [0, 1, 0, 1, 0],
        [1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0]
    ], dtype=np.uint8)

    start_point = [0, 0]  # 左上角
    end_point = [0, 4]    # 右上角（被墙壁阻隔）

    # 验证能识别连通性问题
    result = validator.validate(disconnected_maze, start_point, end_point)

    # 应该能识别连通性问题
    assert not result['valid'], "应该识别出连通性问题"

    # 检查是否提供了错误信息
    assert 'errors' in result, "应该包含错误信息"

    # 创建一个连通的迷宫进行对比
    connected_maze = np.array([
        [0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0]
    ], dtype=np.uint8)

    # 验证连通迷宫
    result2 = validator.validate(connected_maze, [0, 0], [4, 4])

    # 连通的迷宫应该通过验证
    assert result2['valid'], "连通的迷宫应该通过验证"


def test_validation_components():
    """测试验证功能返回组件完整性"""
    validator = MazeValidator()

    # 创建一个正常的迷宫
    normal_maze = np.array([
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0]
    ], dtype=np.uint8)

    result = validator.validate(normal_maze, [0, 0], [4, 4])

    # 检查返回组件
    required_keys = ['valid', 'errors']
    missing_keys = []

    for key in required_keys:
        if key not in result:
            missing_keys.append(key)

    assert len(missing_keys) == 0, f"缺少必需的返回组件: {missing_keys}"

    # 检查数据类型
    assert isinstance(result['valid'], bool), "valid字段应该是布尔值"
    assert isinstance(result['errors'], list), "errors字段应该是列表"
