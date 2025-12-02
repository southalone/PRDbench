# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from recommenders.neural_network_recommender import NeuralNetworkRecommender

class TestNeuralNetwork:
    """轻量级神经网络推荐-MLPRegressor使用测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = {
            'recommendation': {
                'default_top_n': 5,
                'min_ratings': 3
            },
            'neural_network': {
                'hidden_layer_sizes': [64, 32],
                'max_iter': 500,
                'random_state': 42
            }
        }
        
        # 创建测试数据
        # 创建足够大的测试数据集（30条记录以满足验证集要求）
        user_ids = []
        product_ids = []
        ratings = []
        
        for user in range(1, 11):  # 10个用户
            for product in range(1, 6):  # 5个商品
                if np.random.random() > 0.3:  # 70%概率有评分
                    user_ids.append(user)
                    product_ids.append(product)
                    ratings.append(np.random.randint(3, 6))  # 3-5分评分
        
        self.ratings_df = pd.DataFrame({
            'user_id': user_ids,
            'product_id': product_ids,
            'rating': ratings
        })
        
        self.products_df = pd.DataFrame({
            'product_id': [1, 2, 3, 4, 5],
            'name': ['商品A', '商品B', '商品C', '商品D', '商品E'],
            'category': ['电子产品', '服装', '家居', '图书', '运动'],
            'brand': ['品牌A', '品牌B', '品牌C', '品牌D', '品牌E'],
            'price': [100.0, 200.0, 300.0, 400.0, 500.0],
            'price_range': ['低价', '中价', '中价', '高价', '高价'],
            'avg_rating': [4.0, 4.5, 3.5, 4.5, 3.8]
        })
        
        self.users_df = pd.DataFrame({
            'user_id': range(1, 11),
            'age': np.random.randint(20, 60, 10),
            'gender': np.random.choice(['男', '女'], 10)
        })
    
    def test_mlp_regressor_usage(self):
        """测试MLPRegressor使用和CPU训练"""
        recommender = NeuralNetworkRecommender(self.config)
        
        # 训练模型
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        # 断言：模型使用MLPRegressor
        assert hasattr(recommender, 'model'), "应该有训练好的模型"
        
        # 断言：CPU训练成功（无GPU依赖）
        assert recommender.is_trained, "模型应该成功训练"
        
        # 生成推荐
        recommendations = recommender.predict(user_id=1, top_n=5)
        
        # 断言：能输出推荐结果
        assert len(recommendations) > 0, "应该能生成推荐结果"
        assert all('score' in rec for rec in recommendations), "推荐结果应包含分数"
        
        # 断言：验证模型类型和训练状态
        assert str(type(recommender.model)).find('MLPRegressor') != -1, "应使用scikit-learn的MLPRegressor"
        print("✓ 使用scikit-learn MLPRegressor，CPU训练完成")
        
        return True