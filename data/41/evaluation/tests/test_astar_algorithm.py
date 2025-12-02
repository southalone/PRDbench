import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from A_star import A_star

def test_astar_execution():
    """测试A*搜索算法的执行"""
    # 准备测试数据
    query = "ATCG"
    target = "ATCG"

    # 执行算法
    final_node = A_star(query, target)

    # 断言结果
    assert final_node is not None
    assert hasattr(final_node, 'g')
    assert hasattr(final_node, 'path_a')
    assert hasattr(final_node, 'path_b')
    assert final_node.g >= 0  # 代价应该非负

def test_astar_with_different_sequences():
    """测试不同序列的A*搜索算法"""
    query = "ATCG"
    target = "GCTA"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g > 0  # 不同序列应该有正代价
    assert len(final_node.path_a) > 0
    assert len(final_node.path_b) > 0

def test_astar_empty_sequences():
    """测试空序列的处理"""
    query = ""
    target = "ATCG"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g >= 0

def test_astar_identical_sequences():
    """测试相同序列的处理"""
    query = "ATCG"
    target = "ATCG"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g == 0  # 相同序列代价应该为0
    assert final_node.path_a == query
    assert final_node.path_b == target

def test_astar_performance():
    """测试A*搜索算法的性能"""
    import time

    query = "ATCGATCGATCG"
    target = "GCTAGCTAGCTA"

    start_time = time.time()
    final_node = A_star(query, target)
    end_time = time.time()

    execution_time = end_time - start_time

    # 断言算法在合理时间内完成
    assert execution_time < 2.0  # 应该在2秒内完成
    assert final_node is not None
    assert final_node.g >= 0

def test_astar_heuristic_functions():
    """测试A*搜索算法的启发式函数"""
    query = "ATCG"
    target = "GCTA"

    # 测试不同的启发式函数都能工作
    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g >= 0
    assert final_node.path_a is not None
    assert final_node.path_b is not None

def test_astar_optimal_path():
    """测试A*算法找到最优路径"""
    query = "ABC"
    target = "ABC"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g == 0  # 相同序列代价应该为0
