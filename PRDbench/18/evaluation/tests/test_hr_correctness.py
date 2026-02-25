# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.HouseHold import householder_reflection
from utils import matrixFromFile

def test_hr_factorization_correctness():
    """测试Householder镜面对称变换（反射）分解的计算结果正确性"""
    # 加载测试矩阵
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Household.txt')
    matrix = matrixFromFile.load_array(input_file, 'HR')
    
    # 执行Householder反射分解
    Q, R = householder_reflection(matrix)
    
    # 验证Q*R = A
    reconstructed = np.dot(Q, R)
    
    # 检查重构误差
    error = np.linalg.norm(matrix - reconstructed)
    assert error < 1e-10, f"Householder反射分解重构误差过大: {error}"
    
    # 验证Q是正交矩阵 (Q^T * Q = I)
    m, n = Q.shape
    QTQ = np.dot(Q.T, Q)
    identity = np.eye(m)  # Householder通常产生方阵Q
    orthogonal_error = np.linalg.norm(QTQ - identity)
    assert orthogonal_error < 1e-10, f"Q矩阵不是正交矩阵: ||Q^T*Q - I|| = {orthogonal_error}"
    
    # 验证R是上三角矩阵
    m, n = R.shape
    for i in range(1, m):
        for j in range(min(i, n)):
            assert abs(R[i, j]) < 1e-12, f"R矩阵不是上三角矩阵: R[{i},{j}] = {R[i, j]}"

if __name__ == "__main__":
    test_hr_factorization_correctness()
    print("Householder反射分解正确性测试通过")