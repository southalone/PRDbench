import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from GA import GA

def test_ga_execution():
    """测试遗传算法的执行"""
    # 准备测试数据
    query = "ATCG"
    target = "ATCG"

    # 执行算法
    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)

    # 断言结果
    assert cost is not None
    assert out_a is not None
    assert out_b is not None
    assert cost >= 0  # 代价应该非负
    assert len(out_a) > 0
    assert len(out_b) > 0

def test_ga_with_different_sequences():
    """测试不同序列的遗传算法"""
    query = "ATCG"
    target = "GCTA"

    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)

    assert cost is not None
    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

def test_ga_parameters():
    """测试遗传算法的参数配置"""
    query = "ATCG"
    target = "GCTA"

    # 测试不同的参数配置
    cost1, out_a1, out_b1 = GA(query, target, 1.2, 10, 5, 2)
    cost2, out_a2, out_b2 = GA(query, target, 1.5, 30, 15, 5)

    # 两次运行都应该成功
    assert cost1 >= 0
    assert cost2 >= 0
    assert out_a1 is not None
    assert out_a2 is not None
    assert out_b1 is not None
    assert out_b2 is not None

def test_ga_performance():
    """测试遗传算法的性能"""
    import time

    query = "ATCGATCG"
    target = "GCTAGCTA"

    start_time = time.time()
    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)
    end_time = time.time()

    execution_time = end_time - start_time

    # 断言算法在合理时间内完成
    assert execution_time < 5.0  # 应该在5秒内完成
    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

def test_ga_convergence():
    """测试遗传算法的收敛性"""
    query = "ATCG"
    target = "ATCG"

    # 相同序列应该收敛到较低的代价
    cost, out_a, out_b = GA(query, target, 1.2, 50, 20, 5)

    assert cost >= 0
    assert cost < 10  # 相同序列的代价应该较低
    assert out_a is not None
    assert out_b is not None

def test_ga_edge_cases():
    """测试遗传算法的边界情况"""
    # 测试短序列
    query = "AT"
    target = "GC"

    cost, out_a, out_b = GA(query, target, 1.2, 10, 5, 2)

    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

    # 测试较长序列
    query = "ATCGATCGATCGATCG"
    target = "GCTAGCTAGCTAGCTA"

    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)

    assert cost >= 0
    assert out_a is not None
    assert out_b is not None
