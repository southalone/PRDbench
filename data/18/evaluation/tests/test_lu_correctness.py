# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.LU import LU_factorization
from utils import matrixFromFile, auxiliary

def test_lu_factorization_correctness():
    """测试LU分解的计算结果正确性"""
    # 加载测试矩阵
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/LU.txt')
    matrix = matrixFromFile.load_array(input_file, 'LU')
    
    # 提取原始矩阵（去掉行号列）并保存副本
    # 重要：必须在调用LU_factorization之前保存副本，因为该函数会修改输入矩阵
    original_matrix = matrix[:, :-1].copy()
    m, n = original_matrix.shape
    
    # 执行LU分解（注意：这个函数会修改输入的matrix）
    L, U, P = LU_factorization(matrix)
    
    # 验证返回的矩阵不为空且形状正确
    assert L is not None and L.size > 0, "L矩阵不能为空"
    assert U is not None and U.size > 0, "U矩阵不能为空"
    assert P is not None and P.size > 0, "P矩阵不能为空"
    
    # 验证矩阵形状
    assert L.shape == (m, n), f"L矩阵形状错误: 期望{(m, n)}, 实际{L.shape}"
    assert U.shape == (m, n), f"U矩阵形状错误: 期望{(m, n)}, 实际{U.shape}"
    assert P.shape == (m, n), f"P矩阵形状错误: 期望{(m, n)}, 实际{P.shape}"
    
    # 验证L是下三角矩阵（对角线为1）
    for i in range(m):
        for j in range(i+1, n):
            assert abs(L[i, j]) < 1e-12, f"L矩阵不是下三角矩阵: L[{i},{j}] = {L[i, j]}"
        assert abs(L[i, i] - 1.0) < 1e-12, f"L矩阵对角线应为1: L[{i},{i}] = {L[i, i]}"
    
    # 验证U是上三角矩阵
    for i in range(1, m):
        for j in range(i):
            assert abs(U[i, j]) < 1e-12, f"U矩阵不是上三角矩阵: U[{i},{j}] = {U[i, j]}"
    
    # 验证P是置换矩阵（每行每列恰好有一个1）
    for i in range(m):
        row_sum = np.sum(P[i, :])
        assert abs(row_sum - 1.0) < 1e-12, f"P矩阵第{i}行和不为1: {row_sum}"
    
    for j in range(n):
        col_sum = np.sum(P[:, j])
        assert abs(col_sum - 1.0) < 1e-12, f"P矩阵第{j}列和不为1: {col_sum}"
    
    # 验证标准LU分解公式：PA = LU
    PA = P.dot(original_matrix)
    LU = L.dot(U)
    
    # 检查PA与LU的误差
    error = np.linalg.norm(PA - LU)
    assert error < 1e-6, f"LU分解验证失败: ||PA - LU|| = {error}"
    
    # 验证函数能正常运行并产生合理的输出
    assert not np.any(np.isnan(L)), "L矩阵包含NaN值"
    assert not np.any(np.isnan(U)), "U矩阵包含NaN值"
    assert not np.any(np.isnan(P)), "P矩阵包含NaN值"
    assert not np.any(np.isnan(PA)), "PA矩阵包含NaN值"
    assert not np.any(np.isnan(LU)), "LU矩阵包含NaN值"

if __name__ == "__main__":
    test_lu_factorization_correctness()
    print("LU分解正确性测试通过")