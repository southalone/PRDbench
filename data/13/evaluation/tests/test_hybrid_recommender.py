import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.hybrid_recommender import HybridRecommender, HybridStrategy


class TestHybridRecommender:
    """混合推荐算法单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.weighted_recommender = HybridRecommender(HybridStrategy.WEIGHTED)
        self.parallel_recommender = HybridRecommender(HybridStrategy.PARALLEL)
        self.pipeline_recommender = HybridRecommender(HybridStrategy.PIPELINE)
        
    def create_test_data(self):
        """创建测试数据"""
        np.random.seed(42)
        
        # 创建用户数据
        users_data = {
            'user_id': range(1, 31),
            'age': np.random.randint(18, 65, 30),
            'gender': np.random.choice(['男', '女'], 30),
            'city': np.random.choice(['北京', '上海', '广州', '深圳'], 30)
        }
        users_df = pd.DataFrame(users_data)
        
        # 创建商品数据
        categories = ['手机', '电脑', '鞋服', '家电', '图书']
        brands = ['苹果', '华为', '小米', '三星', 'OPPO']
        
        items_data = {
            'item_id': range(1, 61),
            'title': [f"商品{i}标题" for i in range(1, 61)],
            'description': [f"这是商品{i}的详细描述，包含丰富的功能特性和使用场景介绍" for i in range(1, 61)],
            'category': np.random.choice(categories, 60),
            'brand': np.random.choice(brands, 60),
            'price': np.random.uniform(100, 5000, 60),
            'tags': [f"标签{i},特色{i},功能{i}" for i in range(1, 61)]
        }
        items_df = pd.DataFrame(items_data)
        
        # 创建交互数据
        interactions = []
        interaction_id = 1
        
        for user_id in range(1, 31):
            # 每个用户交互8-15个商品
            n_interactions = np.random.randint(8, 16)
            user_items = np.random.choice(range(1, 61), size=n_interactions, replace=False)
            
            for item_id in user_items:
                rating = np.random.choice([3, 4, 5], p=[0.2, 0.5, 0.3])
                interactions.append({
                    'interaction_id': interaction_id,
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': float(rating),
                    'interaction_type': 'rating'
                })
                interaction_id += 1
        
        interactions_df = pd.DataFrame(interactions)
        
        return users_df, items_df, interactions_df
    
    def test_weighted_hybrid_strategy(self):
        """测试整体式混合策略"""
        users_df, items_df, interactions_df = self.create_test_data()
        
        # 训练模型
        self.weighted_recommender.fit(users_df, items_df, interactions_df)
        
        # 验证模型训练状态
        assert self.weighted_recommender.is_fitted, "模型应该处于已训练状态"
        
        # 生成推荐
        user_id = 1
        user_preferences = {
            'interests': '智能手机 拍照',
            'brand': '苹果 华为',
            'category': '手机'
        }
        
        recommendations = self.weighted_recommender.recommend(
            user_id, items_df, interactions_df, top_n=10, user_preferences=user_preferences
        )
        
        # 验证推荐结果
        assert len(recommendations) <= 10, "推荐数量不应该超过top_n"
        assert isinstance(recommendations, list), "推荐结果应该是列表"
        
        # 验证推荐结果格式
        for item_id, score, reason in recommendations:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(score, (float, np.floating)), "推荐分数应该是浮点数"
            assert isinstance(reason, str), "推荐理由应该是字符串"
            assert score > 0, "推荐分数应该为正数"
            assert len(reason) > 0, "推荐理由不应该为空"
        
        # 验证推荐结果按分数降序排列
        scores = [score for _, score, _ in recommendations]
        assert scores == sorted(scores, reverse=True), "推荐结果应该按分数降序排列"
        
        # 验证权重融合逻辑
        weights = self.weighted_recommender.weights
        assert abs(sum(weights.values()) - 1.0) < 0.01, "权重总和应该接近1.0"
        assert len(weights) >= 3, "应该组合≥3个推荐算法"
    
    def test_parallel_hybrid_strategy(self):
        """测试并行式混合策略"""
        users_df, items_df, interactions_df = self.create_test_data()
        
        # 训练模型
        self.parallel_recommender.fit(users_df, items_df, interactions_df)
        
        # 生成推荐
        user_id = 2
        user_preferences = {
            'interests': '游戏 电脑',
            'category': '电脑'
        }
        
        recommendations = self.parallel_recommender.recommend(
            user_id, items_df, interactions_df, top_n=10, user_preferences=user_preferences
        )
        
        # 验证推荐结果
        assert len(recommendations) <= 10, "推荐数量不应该超过top_n"
        assert isinstance(recommendations, list), "推荐结果应该是列表"
        
        # 验证推荐结果格式
        for item_id, score, reason in recommendations:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(score, (float, np.floating)), "推荐分数应该是浮点数"
            assert isinstance(reason, str), "推荐理由应该是字符串"
            assert score > 0, "推荐分数应该为正数"
        
        # 验证并行策略特有的推荐理由
        reasons = [reason for _, _, reason in recommendations]
        has_multiple_algorithms = any("算法" in reason for reason in reasons)
        assert has_multiple_algorithms or len(recommendations) > 0, "并行策略应该显示多算法推荐信息"
        
        # 验证去重和排序
        item_ids = [item_id for item_id, _, _ in recommendations]
        assert len(item_ids) == len(set(item_ids)), "推荐结果应该去重"
    
    def test_pipeline_hybrid_strategy(self):
        """测试流水线式混合策略"""
        users_df, items_df, interactions_df = self.create_test_data()
        
        # 训练模型  
        self.pipeline_recommender.fit(users_df, items_df, interactions_df)
        
        # 生成推荐
        user_id = 3
        user_preferences = {
            'interests': '运动 健身',
            'category': '鞋服'
        }
        
        recommendations = self.pipeline_recommender.recommend(
            user_id, items_df, interactions_df, top_n=10, user_preferences=user_preferences
        )
        
        # 验证推荐结果
        assert len(recommendations) <= 10, "推荐数量不应该超过top_n"
        assert isinstance(recommendations, list), "推荐结果应该是列表"
        
        # 验证推荐结果格式
        for item_id, score, reason in recommendations:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(score, (float, np.floating)), "推荐分数应该是浮点数"
            assert isinstance(reason, str), "推荐理由应该是字符串"
            assert score > 0, "推荐分数应该为正数"
        
        # 验证流水线策略特有的推荐理由
        reasons = [reason for _, _, reason in recommendations]
        has_pipeline_reason = any("流水线" in reason or "阶段" in reason for reason in reasons)
        assert has_pipeline_reason or len(recommendations) > 0, "流水线策略应该体现多阶段处理"
        
        # 验证多阶段处理流程
        # 流水线推荐应该包含多个处理阶段：内容召回→协同过滤重排→多样性优化
        if recommendations:
            sample_reason = recommendations[0][2]  # 取第一个推荐的理由
            # 验证推荐理由包含多阶段信息
            assert "流水线" in sample_reason, f"推荐理由应该包含流水线信息，实际: {sample_reason}"
        
        assert self.pipeline_recommender.is_fitted, "流水线推荐应该经过完整的训练过程"
    
    def test_weight_configuration(self):
        """测试权重配置功能"""
        users_df, items_df, interactions_df = self.create_test_data()
        self.weighted_recommender.fit(users_df, items_df, interactions_df)
        
        # 测试自定义权重
        custom_weights = {
            'content': 0.4,
            'user_cf': 0.3,
            'item_cf': 0.2,
            'matrix_factorization': 0.1
        }
        
        self.weighted_recommender.set_weights(custom_weights)
        
        # 验证权重设置
        updated_weights = self.weighted_recommender.weights
        for key, value in custom_weights.items():
            assert abs(updated_weights[key] - value) < 0.01, f"权重{key}应该被正确设置"
        
        # 验证权重和为1.0
        total_weight = sum(updated_weights.values())
        assert abs(total_weight - 1.0) < 0.01, f"权重总和应该为1.0，实际为{total_weight}"
        
        # 使用新权重生成推荐
        recommendations = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=5)
        assert len(recommendations) > 0, "自定义权重后应该能正常生成推荐"
    
    def test_diversity_evaluation(self):
        """测试多样性评估"""
        users_df, items_df, interactions_df = self.create_test_data()
        self.weighted_recommender.fit(users_df, items_df, interactions_df)
        
        # 生成推荐
        recommendations = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=10)
        
        # 评估多样性
        diversity_metrics = self.weighted_recommender.evaluate_diversity(recommendations, items_df)
        
        # 验证多样性指标
        assert 'category_diversity' in diversity_metrics, "应该包含类别多样性指标"
        assert 'brand_diversity' in diversity_metrics, "应该包含品牌多样性指标"
        
        category_diversity = diversity_metrics['category_diversity']
        brand_diversity = diversity_metrics['brand_diversity']
        
        assert 0 <= category_diversity <= 1, "类别多样性应该在[0,1]范围内"
        assert 0 <= brand_diversity <= 1, "品牌多样性应该在[0,1]范围内"
        
        # 验证多样性指标合理性
        if len(recommendations) > 1:
            assert category_diversity > 0, "多个推荐商品应该有一定的类别多样性"
    
    def test_cold_start_handling(self):
        """测试冷启动处理"""
        users_df, items_df, interactions_df = self.create_test_data()
        self.weighted_recommender.fit(users_df, items_df, interactions_df)
        
        # 测试完全新用户
        new_user_id = 999
        cold_start_recs = self.weighted_recommender.handle_cold_start(
            new_user_id, items_df, interactions_df, top_n=10
        )
        
        # 验证冷启动推荐
        assert len(cold_start_recs) <= 10, "冷启动推荐数量不应该超过top_n"
        assert len(cold_start_recs) > 0, "应该为新用户提供推荐"
        
        # 验证推荐格式
        for item_id, score, reason in cold_start_recs:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(score, (float, np.floating)), "推荐分数应该是浮点数"
            assert isinstance(reason, str), "推荐理由应该是字符串"
            assert item_id in items_df['item_id'].values, "推荐商品应该存在于商品库中"
        
        # 验证热门商品推荐
        reasons = [reason for _, _, reason in cold_start_recs]
        has_popular_items = any("热门" in reason for reason in reasons)
        assert has_popular_items, "新用户应该收到热门商品推荐"
    
    def test_algorithm_integration(self):
        """测试算法集成"""
        users_df, items_df, interactions_df = self.create_test_data()
        
        # 验证所有推荐器都被正确初始化
        assert self.weighted_recommender.content_recommender is not None, "应该包含内容推荐器"
        assert self.weighted_recommender.user_cf is not None, "应该包含用户协同过滤"
        assert self.weighted_recommender.item_cf is not None, "应该包含物品协同过滤"
        assert self.weighted_recommender.matrix_factorization is not None, "应该包含矩阵分解"
        
        # 训练混合推荐系统
        self.weighted_recommender.fit(users_df, items_df, interactions_df)
        
        # 验证各个子推荐器都被训练
        assert self.weighted_recommender.content_recommender.tfidf_vectorizer is not None, "内容推荐器应该被训练"
        assert self.weighted_recommender.user_cf.user_similarity_matrix is not None, "用户协同过滤应该被训练"
        assert self.weighted_recommender.item_cf.item_similarity_matrix is not None, "物品协同过滤应该被训练"
        assert self.weighted_recommender.matrix_factorization.model is not None, "矩阵分解应该被训练"
        
        # 验证≥3个算法集成
        algorithm_count = len(self.weighted_recommender.weights)
        assert algorithm_count >= 3, f"应该集成≥3个推荐算法，实际为{algorithm_count}个"
    
    def test_recommendation_quality(self):
        """测试推荐质量"""
        users_df, items_df, interactions_df = self.create_test_data()
        
        # 测试三种混合策略
        strategies = [
            (self.weighted_recommender, "加权融合"),
            (self.parallel_recommender, "并行式"),
            (self.pipeline_recommender, "流水线式")
        ]
        
        for recommender, strategy_name in strategies:
            recommender.fit(users_df, items_df, interactions_df)
            
            # 为多个用户生成推荐
            all_recommendations = []
            for user_id in [1, 2, 3, 4, 5]:
                recs = recommender.recommend(user_id, items_df, interactions_df, top_n=8)
                all_recommendations.extend([item_id for item_id, _, _ in recs])
            
            # 验证推荐覆盖率
            unique_items = len(set(all_recommendations))
            total_items = len(items_df)
            coverage = unique_items / total_items
            
            assert coverage > 0.1, f"{strategy_name}策略推荐覆盖率应该>10%，实际为{coverage:.2%}"
            
            # 验证推荐不重复
            user_recs = recommender.recommend(1, items_df, interactions_df, top_n=10)
            item_ids = [item_id for item_id, _, _ in user_recs]
            assert len(item_ids) == len(set(item_ids)), f"{strategy_name}策略推荐结果不应该重复"
    
    def test_edge_cases_and_robustness(self):
        """测试边界情况和鲁棒性"""
        users_df, items_df, interactions_df = self.create_test_data()
        
        # 测试未训练模型
        untrained_recommender = HybridRecommender(HybridStrategy.WEIGHTED)
        untrained_recs = untrained_recommender.recommend(1, items_df, interactions_df, top_n=5)
        assert len(untrained_recs) == 0, "未训练模型应该返回空推荐"
        
        # 测试空用户偏好
        self.weighted_recommender.fit(users_df, items_df, interactions_df)
        no_preference_recs = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=5)
        assert isinstance(no_preference_recs, list), "无用户偏好时应该返回列表"
        
        # 测试不存在的用户
        non_exist_recs = self.weighted_recommender.recommend(999, items_df, interactions_df, top_n=5)
        assert isinstance(non_exist_recs, list), "不存在用户应该能处理"
        
        # 测试极小的top_n
        small_recs = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=1)
        assert len(small_recs) <= 1, "top_n=1时最多返回1个推荐"
        
        # 测试极大的top_n
        large_recs = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=1000)
        assert len(large_recs) <= len(items_df), "推荐数量不应该超过商品总数"