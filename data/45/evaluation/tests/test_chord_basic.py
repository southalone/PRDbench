"""
基础的Chord DHT算法单元测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from Node import Node
from Network import Network


def test_node_initialization():
    """测试节点初始化"""
    Node.m = 4
    Node.ring_size = 16
    node = Node(5, 4)

    assert node.node_id == 5
    assert node.predecessor == node
    assert node.successor == node
    assert len(node.fingers_table) == 4
    assert isinstance(node.data, dict)


def test_network_initialization():
    """测试网络初始化"""
    m = 4
    node_ids = [0, 4, 8, 12]
    network = Network(m, node_ids)

    assert network.m == 4
    assert network.ring_size == 16
    assert len(network.nodes) == 1  # 只有第一个节点被初始化
    assert network.first_node.node_id == 0


def test_hash_function():
    """测试哈希函数"""
    m = 4
    network = Network(m, [0])

    # 测试相同输入产生相同哈希值
    hash1 = network.hash_function("test_data")
    hash2 = network.hash_function("test_data")
    assert hash1 == hash2

    # 测试哈希值在有效范围内
    assert 0 <= hash1 < 2**m


def test_node_distance_calculation():
    """测试节点距离计算"""
    Node.m = 4
    Node.ring_size = 16
    node = Node(5, 4)

    # 测试正向距离
    assert node.distance(5, 8) == 3
    # 测试环形距离
    assert node.distance(12, 3) == 7


def test_finger_table_size():
    """测试finger表大小"""
    Node.m = 6
    Node.ring_size = 64
    node = Node(10, 6)

    assert len(node.fingers_table) == 6
    # 初始时所有finger都指向自己
    for finger in node.fingers_table:
        assert finger == node


if __name__ == "__main__":
    pytest.main([__file__])
