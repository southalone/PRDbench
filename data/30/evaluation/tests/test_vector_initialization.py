#!/usr/bin/env python3
"""
TransE向量初始化测试
"""

import sys
import os
import pytest
import numpy as np

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from transE import TransE


def test_vector_dimensions():
    """测试向量维度是否正确"""
    # 创建测试数据
    entity_set = {'0', '1', '2'}
    relation_set = {'0', '1'}
    triple_list = [['0', '1', '0'], ['1', '2', '1']]

    # 创建TransE模型
    transE = TransE(entity_set, relation_set, triple_list,
                   embedding_dim=50, learning_rate=0.01, margin=1, L1=True)

    # 初始化向量
    transE.emb_initialize()

    # 检查实体向量维度
    for entity_id in entity_set:
        assert len(transE.entity[entity_id]) == 50, f"实体向量维度不正确: {len(transE.entity[entity_id])}"

    # 检查关系向量维度
    for relation_id in relation_set:
        assert len(transE.relation[relation_id]) == 50, f"关系向量维度不正确: {len(transE.relation[relation_id])}"

    print("向量维度测试通过：所有向量都是50维")


def test_vector_initialization_distribution():
    """测试向量初始化是否使用均匀分布"""
    entity_set = {'0', '1', '2'}
    relation_set = {'0', '1'}
    triple_list = [['0', '1', '0'], ['1', '2', '1']]

    transE = TransE(entity_set, relation_set, triple_list,
                   embedding_dim=50, learning_rate=0.01, margin=1, L1=True)

    transE.emb_initialize()

    # 检查向量值是否在合理范围内（均匀分布初始化后归一化）
    for entity_id in entity_set:
        vector = np.array(transE.entity[entity_id])
        # 检查向量是否已归一化
        norm = np.linalg.norm(vector)
        assert abs(norm - 1.0) < 1e-6, f"实体向量未正确归一化: {norm}"

    for relation_id in relation_set:
        vector = np.array(transE.relation[relation_id])
        norm = np.linalg.norm(vector)
        assert abs(norm - 1.0) < 1e-6, f"关系向量未正确归一化: {norm}"

    print("向量初始化分布测试通过：所有向量都已正确归一化")


if __name__ == '__main__':
    test_vector_dimensions()
    test_vector_initialization_distribution()
    print("所有测试通过！")
