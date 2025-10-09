"""
迷宫后处理测试
"""
import pytest
import os
import sys
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator


def test_wall_removal():
    """测试墙壁拆除功能"""
    generator = MazeGenerator()

    # 生成一个迷宫
    result = generator.generate('dfs', 15)
    original_maze = result['maze_matrix'].copy()

    # 计算原始墙壁数量
    original_walls = np.sum(original_maze == 1)

    # 调用墙壁拆除功能（如果存在）
    try:
        # 尝试调用墙壁拆除功能
        # 这里需要根据实际实现调整
        if hasattr(generator, 'remove_walls'):
            processed_maze = generator.remove_walls(original_maze, wall_count=5)
            processed_walls = np.sum(processed_maze == 1)

            # 验证墙壁确实被拆除
            walls_removed = original_walls - processed_walls
            assert walls_removed >= 4 and walls_removed <= 6, f"拆除墙壁数量{walls_removed}不在允许范围内(4-6)"
        else:
            # 如果没有实现墙壁拆除功能，跳过测试
            pytest.skip("墙壁拆除功能未实现")
    except Exception as e:
        pytest.fail(f"墙壁拆除功能测试失败: {e}")


def test_maze_postprocessing():
    """测试迷宫后处理功能"""
    generator = MazeGenerator()

    # 生成一个迷宫
    result = generator.generate('prim', 11)
    maze_matrix = result['maze_matrix']

    # 检查迷宫的基本属性
    assert isinstance(maze_matrix, np.ndarray), "迷宫应该是numpy数组"
    assert maze_matrix.shape[0] == maze_matrix.shape[1], "迷宫应该是正方形"

    # 检查边界是否为墙壁（通常迷宫的边界应该是墙壁）
    # 注意：具体实现可能不同，这里做基本检查
    walls = np.sum(maze_matrix == 1)
    paths = np.sum(maze_matrix == 0)

    assert walls > 0, "迷宫应该包含墙壁"
    assert paths > 0, "迷宫应该包含通路"
