#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from utils.matrix_utils import MatrixUtils
import pandas as pd

def test_tfidf_matrix_transform():
    """测试TF-IDF矩阵转化功能"""
    try:
        # 创建测试数据
        ratings_df = pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3, 3],
            'product_id': [1, 2, 1, 3, 2, 3],
            'rating': [5.0, 4.0, 3.0, 5.0, 4.0, 3.0]
        })
        
        products_df = pd.DataFrame({
            'product_id': [1, 2, 3],
            'category': ['电子产品', '服装', '家居'],
            'brand': ['品牌A', '品牌B', '品牌C'],
            'price_range': ['中价', '低价', '高价']
        })
        
        # 执行矩阵转化
        user_attribute_matrix = MatrixUtils.create_user_attribute_matrix(ratings_df, products_df)
        
        # 保存结果
        output_path = '../evaluation/tfidf_output.csv'
        user_attribute_matrix.to_csv(output_path)
        
        print("SUCCESS: TF-IDF矩阵转化成功")
        print(f"矩阵维度: {user_attribute_matrix.shape}")
        print(f"输出文件: {output_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: 矩阵转化失败: {e}")
        return False

if __name__ == "__main__":
    success = test_tfidf_matrix_transform()
    sys.exit(0 if success else 1)
