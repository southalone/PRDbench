# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.LU import LU_factorization
from model.Gram_Schmidt import gram_schmidt
from model.HouseHold import householder_reflection
from model.Givens import givens_rotation
from model.URV import URV_factorization
from utils import matrixFromFile, auxiliary

def test_lu_matrix_rank():
    """测试LU分解中矩阵秩的计算"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/LU.txt')
    matrix = matrixFromFile.load_array(input_file, 'LU')
    
    # 计算矩阵的秩
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)
    
    # 验证秩计算的正确性
    assert calculated_rank == expected_rank, f"矩阵秩计算错误: 计算值={calculated_rank}, 期望值={expected_rank}"
    
    # 验证矩阵是满秩的（对于方阵）
    m, n = matrix.shape
    if m == n:
        assert calculated_rank == m, f"方阵应该是满秩的: 秩={calculated_rank}, 维度={m}"

def test_qr_matrix_rank():
    """测试QR分解中矩阵秩的计算"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/GramSchmidt.txt')
    matrix = matrixFromFile.load_array(input_file, 'QR')
    
    # 计算矩阵的秩
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)
    
    # 验证秩计算的正确性
    assert calculated_rank == expected_rank, f"矩阵秩计算错误: 计算值={calculated_rank}, 期望值={expected_rank}"

def test_hr_matrix_rank():
    """测试Householder反射中矩阵秩的计算"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Household.txt')
    matrix = matrixFromFile.load_array(input_file, 'HR')
    
    # 计算矩阵的秩
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)
    
    # 验证秩计算的正确性
    assert calculated_rank == expected_rank, f"矩阵秩计算错误: 计算值={calculated_rank}, 期望值={expected_rank}"

def test_gr_matrix_rank():
    """测试Givens旋转中矩阵秩的计算"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Givens.txt')
    matrix = matrixFromFile.load_array(input_file, 'GR')
    
    # 计算矩阵的秩
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)
    
    # 验证秩计算的正确性
    assert calculated_rank == expected_rank, f"矩阵秩计算错误: 计算值={calculated_rank}, 期望值={expected_rank}"

def test_urv_matrix_rank():
    """测试URV分解中矩阵秩的计算"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/URV.txt')
    matrix = matrixFromFile.load_array(input_file, 'URV')
    
    # 计算矩阵的秩
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)
    
    # 验证秩计算的正确性
    assert calculated_rank == expected_rank, f"矩阵秩计算错误: 计算值={calculated_rank}, 期望值={expected_rank}"

if __name__ == "__main__":
    test_lu_matrix_rank()
    test_qr_matrix_rank()
    test_hr_matrix_rank()
    test_gr_matrix_rank()
    test_urv_matrix_rank()
    print("所有矩阵秩计算测试通过")