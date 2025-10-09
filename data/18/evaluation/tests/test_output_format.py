# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest
import io
from contextlib import redirect_stdout

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.LU import LU_factorization
from model.Gram_Schmidt import gram_schmidt
from model.HouseHold import householder_reflection
from model.Givens import givens_rotation
from model.URV import URV_factorization
from utils import matrixFromFile, auxiliary

def test_lu_output_format():
    """测试LU分解输出格式的规范性"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/LU.txt')
    matrix = matrixFromFile.load_array(input_file, 'LU')
    
    L, U, P = LU_factorization(matrix)
    
    # 捕获print_array的输出
    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(L)
    output = f.getvalue()
    
    # 检查输出格式：应该包含4位小数
    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            # 检查每行的数字格式
            numbers = line.split(',')[:-1]  # 去掉最后的空逗号
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    # 验证格式为8.4f
                    assert '.' in num_str, f"数字格式错误，缺少小数点: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"小数位数不是4位: {num_str}"

def test_qr_output_format():
    """测试QR分解输出格式的规范性"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/GramSchmidt.txt')
    matrix = matrixFromFile.load_array(input_file, 'QR')
    
    Q, R = gram_schmidt(matrix)
    
    # 测试Q矩阵格式
    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(Q)
    output = f.getvalue()
    
    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"数字格式错误: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"小数位数不是4位: {num_str}"

def test_hr_output_format():
    """测试Householder反射输出格式的规范性"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Household.txt')
    matrix = matrixFromFile.load_array(input_file, 'HR')
    
    Q, R = householder_reflection(matrix)
    
    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(Q)
    output = f.getvalue()
    
    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"数字格式错误: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"小数位数不是4位: {num_str}"

def test_gr_output_format():
    """测试Givens旋转输出格式的规范性"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Givens.txt')
    matrix = matrixFromFile.load_array(input_file, 'GR')
    
    Q, R = givens_rotation(matrix)
    
    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(Q)
    output = f.getvalue()
    
    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"数字格式错误: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"小数位数不是4位: {num_str}"

def test_urv_output_format():
    """测试URV分解输出格式的规范性"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/URV.txt')
    matrix = matrixFromFile.load_array(input_file, 'URV')
    
    U, R, V = URV_factorization(matrix)
    
    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(U)
    output = f.getvalue()
    
    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"数字格式错误: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"小数位数不是4位: {num_str}"

if __name__ == "__main__":
    test_lu_output_format()
    test_qr_output_format()
    test_hr_output_format()
    test_gr_output_format()
    test_urv_output_format()
    print("所有输出格式测试通过")