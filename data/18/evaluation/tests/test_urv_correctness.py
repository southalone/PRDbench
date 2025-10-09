# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.URV import URV_factorization
from utils import matrixFromFile

def test_urv_factorization_correctness():
    """测试URV分解的计算结果正确性"""
    # 加载测试矩阵
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/URV.txt')
    matrix = matrixFromFile.load_array(input_file, 'URV')
    
    # 执行URV分解
    U, R, V = URV_factorization(matrix)
    
    # 验证U*R*V^T = A
    reconstructed = U.dot(R).dot(V.T)
    
    # 检查重构误差
    error = np.linalg.norm(matrix - reconstructed)
    assert error < 1e-10, f"URV分解重构误差过大: {error}"
    
    # 验证U是正交矩阵 (U^T * U = I)
    m, n = U.shape
    UTU = np.dot(U.T, U)
    identity_u = np.eye(n)
    orthogonal_error_u = np.linalg.norm(UTU - identity_u)
    assert orthogonal_error_u < 1e-10, f"U矩阵不是正交矩阵: ||U^T*U - I|| = {orthogonal_error_u}"
    
    # 验证V是正交矩阵 (V^T * V = I)
    m, n = V.shape
    VTV = np.dot(V.T, V)
    identity_v = np.eye(n)
    orthogonal_error_v = np.linalg.norm(VTV - identity_v)
    assert orthogonal_error_v < 1e-10, f"V矩阵不是正交矩阵: ||V^T*V - I|| = {orthogonal_error_v}"

if __name__ == "__main__":
    test_urv_factorization_correctness()
    print("URV分解正确性测试通过")