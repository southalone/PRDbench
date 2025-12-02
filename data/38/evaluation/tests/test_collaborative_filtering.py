# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from recommenders.collaborative_filtering_recommender import CollaborativeFilteringRecommender

class TestCollaborativeFiltering:
    """协同过滤推荐-多种相似度计算测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = {
            'recommendation': {
                'default_top_n': 5,
                'min_ratings': 3
            }
        }
        
        # 创建测试数据
        self.ratings_df = pd.DataFrame({
            'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'product_id': [1, 2, 3, 1, 2, 4, 2, 3, 4],
            'rating': [5.0, 4.0, 3.0, 4.0, 5.0, 3.0, 3.0, 4.0, 5.0]
        })
        
        self.products_df = pd.DataFrame({
            'product_id': [1, 2, 3, 4],
            'name': ['商品A', '商品B', '商品C', '商品D'],
            'category': ['电子产品', '服装', '家居', '图书'],
            'brand': ['品牌A', '品牌B', '品牌C', '品牌D'],
            'price': [100.0, 200.0, 300.0, 400.0],
            'price_range': ['低价', '中价', '中价', '高价'],
            'avg_rating': [4.0, 4.5, 3.5, 4.5]
        })
        
        self.users_df = pd.DataFrame({
            'user_id': [1, 2, 3],
            'age': [25, 30, 35],
            'gender': ['男', '女', '男']
        })
    
    def test_cosine_similarity(self):
        """测试余弦相似度"""
        recommender = CollaborativeFilteringRecommender(self.config, similarity_metric='cosine')
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        # 为用户1生成推荐
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        # 断言：余弦相似度计算正确
        assert len(recommendations) > 0, "余弦相似度推荐结果不应为空"
        assert all('score' in rec for rec in recommendations), "推荐结果应包含分数"
        assert recommender.similarity_metric == 'cosine', "应使用余弦相似度"
        
        return True
    
    def test_pearson_similarity(self):
        """测试皮尔逊相关系数"""
        recommender = CollaborativeFilteringRecommender(self.config, similarity_metric='pearson')
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        # 断言：皮尔逊相关系数计算正确
        assert len(recommendations) > 0, "皮尔逊相关系数推荐结果不应为空"
        assert recommender.similarity_metric == 'pearson', "应使用皮尔逊相关系数"
        
        return True
    
    def test_euclidean_similarity(self):
        """测试欧几里得距离"""
        recommender = CollaborativeFilteringRecommender(self.config, similarity_metric='euclidean')
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        # 断言：欧几里得距离计算正确
        assert len(recommendations) > 0, "欧几里得距离推荐结果不应为空"
        assert recommender.similarity_metric == 'euclidean', "应使用欧几里得距离"
        
        return True
    
    def test_similarity_methods_difference(self):
        """测试不同相似度方法产生不同结果"""
        # 创建三个不同的推荐器
        cosine_rec = CollaborativeFilteringRecommender(self.config, similarity_metric='cosine')
        pearson_rec = CollaborativeFilteringRecommender(self.config, similarity_metric='pearson')
        euclidean_rec = CollaborativeFilteringRecommender(self.config, similarity_metric='euclidean')
        
        # 训练模型
        cosine_rec.fit(self.ratings_df, self.products_df)
        pearson_rec.fit(self.ratings_df, self.products_df)
        euclidean_rec.fit(self.ratings_df, self.products_df)
        
        # 生成推荐
        cosine_recs = cosine_rec.recommend(user_id=1, top_n=3)
        pearson_recs = pearson_rec.recommend(user_id=1, top_n=3)
        euclidean_recs = euclidean_rec.recommend(user_id=1, top_n=3)
        
        # 断言：不同方法产生的推荐结果应有差异
        cosine_scores = [rec['score'] for rec in cosine_recs]
        pearson_scores = [rec['score'] for rec in pearson_recs]
        euclidean_scores = [rec['score'] for rec in euclidean_recs]
        
        # 至少有一个方法的结果与其他方法不同
        methods_different = (cosine_scores != pearson_scores or 
                           pearson_scores != euclidean_scores or 
                           cosine_scores != euclidean_scores)
        
        assert methods_different, "不同相似度方法应产生不同的推荐结果"
        
        return True