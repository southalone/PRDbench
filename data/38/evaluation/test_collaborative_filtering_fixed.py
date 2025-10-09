#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from recommenders.collaborative_filtering_recommender import CollaborativeFilteringRecommender

def create_proper_test_data():
    """创建包含所需字段的正确测试数据"""
    ratings_df = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'product_id': [1, 2, 3, 1, 2, 4, 2, 3, 4],
        'rating': [5.0, 4.0, 3.0, 4.0, 5.0, 3.0, 3.0, 4.0, 5.0]
    })
    
    products_df = pd.DataFrame({
        'product_id': [1, 2, 3, 4],
        'name': ['商品A', '商品B', '商品C', '商品D'],
        'category': ['电子产品', '服装', '家居', '图书'],
        'brand': ['品牌A', '品牌B', '品牌C', '品牌D'],
        'price': [100.0, 200.0, 300.0, 400.0],
        'price_range': ['low', 'medium', 'high', 'high']
    })
    
    return ratings_df, products_df

def test_cosine_similarity():
    """测试余弦相似度"""
    try:
        config = {'recommendation': {'default_top_n': 5, 'min_ratings': 3}}
        ratings_df, products_df = create_proper_test_data()
        
        recommender = CollaborativeFilteringRecommender(config, similarity_metric='cosine')
        recommender.fit(ratings_df, products_df)
        
        # 使用正确的方法名predict
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        print("PASS: 余弦相似度算法测试通过")
        print(f"推荐结果数量: {len(recommendations)}")
        print(f"算法类型: {recommender.similarity_metric}")
        
        return True
        
    except Exception as e:
        print(f"FAIL: 余弦相似度测试失败: {e}")
        return False

def test_pearson_similarity():
    """测试皮尔逊相关系数"""
    try:
        config = {'recommendation': {'default_top_n': 5}}
        ratings_df, products_df = create_proper_test_data()
        
        recommender = CollaborativeFilteringRecommender(config, similarity_metric='pearson')
        recommender.fit(ratings_df, products_df)
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        print("PASS: 皮尔逊相关系数测试通过")
        print(f"算法类型: {recommender.similarity_metric}")
        return True
        
    except Exception as e:
        print(f"FAIL: 皮尔逊测试失败: {e}")
        return False

def test_euclidean_similarity():
    """测试欧几里得距离"""
    try:
        config = {'recommendation': {'default_top_n': 5}}
        ratings_df, products_df = create_proper_test_data()
        
        recommender = CollaborativeFilteringRecommender(config, similarity_metric='euclidean')
        recommender.fit(ratings_df, products_df)
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        print("PASS: 欧几里得距离测试通过")
        print(f"算法类型: {recommender.similarity_metric}")
        return True
        
    except Exception as e:
        print(f"FAIL: 欧几里得测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("协同过滤推荐算法评估")
    print("=" * 50)
    
    results = []
    results.append(test_cosine_similarity())
    results.append(test_pearson_similarity()) 
    results.append(test_euclidean_similarity())
    
    passed = sum(results)
    print(f"\n协同过滤评估结果: {passed}/3 通过")
    
    sys.exit(0 if passed == 3 else 1)