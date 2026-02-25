"""
Chord DHT数据操作单元测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from Node import Node
from Network import Network


def test_data_insertion():
    """测试数据插入功能"""
    m = 4
    network = Network(m, [0, 4, 8, 12])

    # 创建完整网络
    for node_id in [4, 8, 12]:
        network.add_node(node_id)

    # 插入数据
    test_data = "test_file.txt"
    result = network.insert_data(test_data)

    # 验证数据已插入
    assert result is not None

    # 验证数据可以被找到
    found = network.lookup_data(test_data)
    assert found is not None


def test_data_lookup():
    """测试数据查找功能"""
    m = 4
    network = Network(m, [0])

    # 插入数据
    test_data = "lookup_test.txt"
    network.insert_data(test_data)

    # 查找存在的数据
    found = network.lookup_data(test_data)
    assert found is not None

    # 查找不存在的数据
    not_found = network.lookup_data("nonexistent.txt")
    assert not_found is None


def test_hash_consistency():
    """测试哈希一致性"""
    m = 4
    network = Network(m, [0])

    # 相同数据应产生相同哈希
    data = "consistency_test.txt"
    hash1 = network.hash_function(data)
    hash2 = network.hash_function(data)

    assert hash1 == hash2


def test_data_distribution():
    """测试数据分布"""
    m = 4
    network = Network(m, [0])

    # 添加多个节点
    for node_id in [4, 8, 12]:
        network.add_node(node_id)

    # 插入多个数据
    data_items = ["file1.txt", "file2.png", "file3.doc", "file4.mov"]
    for data in data_items:
        network.insert_data(data)

    # 验证数据被分布到不同节点
    total_data_count = sum(len(node.data) for node in network.nodes)
    assert total_data_count == len(data_items)


def test_node_data_transfer():
    """测试节点数据转移（删除节点时）"""
    m = 4
    network = Network(m, [0])

    # 添加节点
    network.add_node(8)

    # 在节点8上存储数据
    network.insert_data("transfer_test.txt")

    # 确保数据已存储
    assert network.lookup_data("transfer_test.txt") is not None

    # 删除节点8（如果实现了数据转移）
    if hasattr(network, 'remove_node'):
        network.remove_node(8)
        # 验证数据仍然可以找到
        assert network.lookup_data("transfer_test.txt") is not None


if __name__ == "__main__":
    pytest.main([__file__])
