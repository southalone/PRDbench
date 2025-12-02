import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from DP import DP

def test_dp_execution():
    """测试动态规划算法的执行"""
    # 准备测试数据
    query = "ATCG"
    target = "ATCG"

    # 执行算法
    aligned_query, aligned_target, cost_matrix = DP(query, target)

    # 断言结果
    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix is not None
    assert len(aligned_query) > 0
    assert len(aligned_target) > 0
    assert cost_matrix[0][0] >= 0  # 代价应该非负

def test_dp_with_different_sequences():
    """测试不同序列的动态规划算法"""
    query = "ATCG"
    target = "GCTA"

    aligned_query, aligned_target, cost_matrix = DP(query, target)

    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix[0][0] > 0  # 不同序列应该有正代价

def test_dp_empty_sequences():
    """测试空序列的处理"""
    query = ""
    target = "ATCG"

    aligned_query, aligned_target, cost_matrix = DP(query, target)

    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix is not None

def test_dp_identical_sequences():
    """测试相同序列的处理"""
    query = "ATCGATCG"
    target = "ATCGATCG"

    aligned_query, aligned_target, cost_matrix = DP(query, target)

    assert aligned_query == target
    assert aligned_target == query
    assert cost_matrix[0][0] == 0  # 相同序列代价应该为0

def test_dp_performance():
    """测试动态规划算法的性能"""
    import time

    query = "ATCGATCGATCGATCG"
    target = "GCTAGCTAGCTAGCTA"

    start_time = time.time()
    aligned_query, aligned_target, cost_matrix = DP(query, target)
    end_time = time.time()

    execution_time = end_time - start_time

    # 断言算法在合理时间内完成
    assert execution_time < 1.0  # 应该在1秒内完成
    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix[0][0] >= 0
