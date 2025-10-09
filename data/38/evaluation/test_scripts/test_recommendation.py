#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from recommenders.attribute_utility_recommender import AttributeUtilityRecommender
import pandas as pd

def test_attribute_utility_recommendation():
    """测试属性效用叠加推荐功能"""
    try:
        config = {
            'recommendation': {'default_top_n': 5},
            'recommendation_settings': {
                'attribute_weights': {
                    'price': 0.3,
                    'quality': 0.25,
                    'function': 0.25,
                    'appearance': 0.2
                }
            }
        }
        recommender = AttributeUtilityRecommender(config)
        
        # 创建测试数据
        ratings_df = pd.DataFrame({
            'user_id': [1, 1, 2, 2],
            'product_id': [1, 2, 1, 3], 
            'rating': [5.0, 4.0, 3.0, 5.0]
        })
        
        products_df = pd.DataFrame({
            'product_id': [1, 2, 3],
            'name': ['商品A', '商品B', '商品C'],
            'category': ['电子产品', '服装', '家居'],
            'brand': ['品牌A', '品牌B', '品牌C'],
            'price': [100.0, 200.0, 300.0],
            'price_range': ['低价', '中价', '高价'],
            'avg_rating': [4.0, 4.5, 3.5]
        })
        
        # 训练并生成推荐
        recommender.fit(ratings_df, products_df)
        recommendations = recommender.predict(user_id=1, top_n=5)
        
        print("SUCCESS: 属性效用推荐成功")
        print(f"推荐数量: {len(recommendations)}")
        
        # 检查推荐解释
        has_explanation = any('explanation' in rec or 'reason' in rec for rec in recommendations)
        if has_explanation:
            print("SUCCESS: 包含推荐解释")
        
        return True
        
    except Exception as e:
        print(f"ERROR: 推荐生成失败: {e}")
        return False

if __name__ == "__main__":
    success = test_attribute_utility_recommendation()
    sys.exit(0 if success else 1)
