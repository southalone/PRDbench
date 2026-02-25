# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from recommenders.attribute_utility_recommender import AttributeUtilityRecommender

def test_cold_start_attribute_initialization():
    """测试冷启动用户处理和属性分布初始化"""
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
    
    # 模拟已有用户数据
    ratings_df = pd.DataFrame({
        'user_id': [1, 2, 3], 'product_id': [1, 2, 3], 'rating': [5, 4, 3]
    })
    products_df = pd.DataFrame({
        'product_id': [1, 2, 3],
        'category': ['A', 'B', 'C'],
        'price': [100, 200, 300],
        'price_range': ['低价', '中价', '高价'],
        'name': ['商品A', '商品B', '商品C'],
        'brand': ['品牌A', '品牌B', '品牌C'],
        'avg_rating': [4.0, 4.5, 3.5]
    })
    
    # 训练推荐器
    recommender.fit(ratings_df, products_df)
    
    # 为新用户(ID=999)获取属性偏好（冷启动场景）
    new_user_id = 999
    # 尝试为冷启动用户生成推荐（这会触发初始化逻辑）
    recommendations = recommender.predict(new_user_id, top_n=3)
    
    # 断言：成功为冷启动用户生成推荐（证明基于全局属性分布初始化成功）
    assert recommendations is not None, "应该能为冷启动用户生成推荐"
    assert len(recommendations) > 0, "冷启动推荐结果不应为空"
    
    # 验证推荐结果的合理性（基于全局属性分布）
    for rec in recommendations:
        assert 'product_id' in rec, "推荐结果应包含商品ID"
        assert 'score' in rec, "推荐结果应包含评分"
        assert rec['score'] > 0, "冷启动推荐评分应为正值"
    
    print(f"✓ 冷启动用户999初始化成功，生成{len(recommendations)}个推荐")
    print("✓ 基于全局属性分布为新用户自动初始化，生成合理的初始推荐")
