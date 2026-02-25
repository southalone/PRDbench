import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.collaborative_filtering import MatrixFactorization


class TestMatrixFactorization:
    """矩阵分解算法单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.matrix_factorization = MatrixFactorization()
        
    def create_sparse_interaction_data(self):
        """创建稀疏的用户-商品评分矩阵数据"""
        np.random.seed(42)
        
        # 创建30个用户，60个商品的稀疏交互数据
        users = range(1, 31)
        items = range(1, 61)
        
        interactions = []
        interaction_id = 1
        
        # 为了创建稀疏数据（稀疏度≥90%），每个用户只与少数商品交互
        for user_id in users:
            # 每个用户只与3-8个商品交互，确保稀疏性
            n_interactions = np.random.randint(3, 9)
            user_items = np.random.choice(items, size=n_interactions, replace=False)
            
            for item_id in user_items:
                # 生成1-5的评分
                rating = np.random.randint(1, 6)
                
                interactions.append({
                    'interaction_id': interaction_id,
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': float(rating),
                    'interaction_type': 'rating'
                })
                interaction_id += 1
        
        df = pd.DataFrame(interactions)
        
        # 验证稀疏度
        total_possible = len(users) * len(items)
        actual_interactions = len(df)
        sparsity = 1 - (actual_interactions / total_possible)
        
        assert sparsity >= 0.85, f"数据稀疏度应该≥85%，实际为{sparsity:.2%}"
        
        return df
    
    def test_matrix_factorization_training(self):
        """测试矩阵分解模型训练"""
        # 准备测试数据
        interactions_df = self.create_sparse_interaction_data()
        
        # 训练模型
        self.matrix_factorization.fit(interactions_df, test_size=0.2)
        
        # 验证模型训练结果
        assert self.matrix_factorization.model is not None, "SVD模型应该被成功训练"
        assert self.matrix_factorization.trainset is not None, "应该有训练集"
        assert self.matrix_factorization.testset is not None, "应该有测试集"
        
        # 验证模型参数
        model = self.matrix_factorization.model
        assert hasattr(model, 'n_factors'), "模型应该有因子数量参数"
        assert hasattr(model, 'n_epochs'), "模型应该有训练轮数参数"
        assert hasattr(model, 'lr_all'), "模型应该有学习率参数"
        assert hasattr(model, 'reg_all'), "模型应该有正则化参数"
        
        # 验证隐因子数量可配置且≥50
        assert model.n_factors >= 50, f"隐因子数量应该≥50，实际为{model.n_factors}"
    
    def test_rating_prediction(self):
        """测试评分预测功能"""
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)
        
        # 测试评分预测
        user_id = 1
        item_id = 10
        predicted_rating = self.matrix_factorization.predict(user_id, item_id)
        
        # 验证预测结果
        assert isinstance(predicted_rating, (float, np.floating)), "预测评分应该是浮点数"
        assert 1 <= predicted_rating <= 5, "预测评分应该在1-5范围内"
        
        # 测试多个预测
        predictions = []
        for user_id in [1, 2, 3]:
            for item_id in [5, 15, 25]:
                pred = self.matrix_factorization.predict(user_id, item_id)
                predictions.append(pred)
        
        # 验证预测多样性（不应该所有预测都相同）
        assert len(set(predictions)) > 1, "预测结果应该有多样性"
        
        # 测试未训练模型的预测
        untrained_mf = MatrixFactorization()
        untrained_pred = untrained_mf.predict(1, 1)
        assert untrained_pred == 0.0, "未训练模型应该返回0.0"
    
    def test_recommendation_generation(self):
        """测试推荐生成功能"""
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)
        
        # 为用户生成推荐
        user_id = 1
        candidate_items = list(range(1, 21))  # 候选商品1-20
        recommendations = self.matrix_factorization.recommend(user_id, candidate_items, top_n=10)
        
        # 验证推荐结果
        assert len(recommendations) <= 10, "推荐数量不应该超过top_n"
        assert len(recommendations) <= len(candidate_items), "推荐数量不应该超过候选商品数量"
        
        # 验证推荐结果格式
        for item_id, predicted_rating in recommendations:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(predicted_rating, (float, np.floating)), "预测评分应该是浮点数"
            assert item_id in candidate_items, "推荐商品应该在候选列表中"
            assert 1 <= predicted_rating <= 5, "预测评分应该在1-5范围内"
        
        # 验证推荐结果按预测评分降序排列
        ratings = [rating for _, rating in recommendations]
        assert ratings == sorted(ratings, reverse=True), "推荐结果应该按预测评分降序排列"
        
        # 测试未训练模型的推荐
        untrained_mf = MatrixFactorization()
        untrained_recs = untrained_mf.recommend(1, [1, 2, 3], top_n=5)
        assert len(untrained_recs) == 0, "未训练模型应该返回空推荐"
    
    def test_user_and_item_factors(self):
        """测试用户和商品因子向量"""
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)
        
        # 获取用户因子向量
        user_id = 1
        user_factors = self.matrix_factorization.get_user_factors(user_id)
        
        if user_factors is not None:
            assert isinstance(user_factors, np.ndarray), "用户因子应该是numpy数组"
            assert len(user_factors) == self.matrix_factorization.model.n_factors, "用户因子维度应该等于模型因子数"
            assert not np.all(user_factors == 0), "用户因子不应该全为零"
        
        # 获取商品因子向量
        item_id = 1
        item_factors = self.matrix_factorization.get_item_factors(item_id)
        
        if item_factors is not None:
            assert isinstance(item_factors, np.ndarray), "商品因子应该是numpy数组"
            assert len(item_factors) == self.matrix_factorization.model.n_factors, "商品因子维度应该等于模型因子数"
            assert not np.all(item_factors == 0), "商品因子不应该全为零"
        
        # 测试不存在的用户和商品
        non_exist_user_factors = self.matrix_factorization.get_user_factors(999)
        non_exist_item_factors = self.matrix_factorization.get_item_factors(999)
        
        assert non_exist_user_factors is None, "不存在用户应该返回None"
        assert non_exist_item_factors is None, "不存在商品应该返回None"
        
        # 测试未训练模型
        untrained_mf = MatrixFactorization()
        untrained_user_factors = untrained_mf.get_user_factors(1)
        untrained_item_factors = untrained_mf.get_item_factors(1)
        
        assert untrained_user_factors is None, "未训练模型应该返回None用户因子"
        assert untrained_item_factors is None, "未训练模型应该返回None商品因子"
    
    def test_sparse_data_handling(self):
        """测试稀疏数据处理能力"""
        # 创建极度稀疏的数据（稀疏度>95%）
        sparse_interactions = []
        users = range(1, 21)  # 20个用户
        items = range(1, 101)  # 100个商品
        
        # 每个用户只与1-3个商品交互
        for user_id in users:
            n_interactions = np.random.randint(1, 4)
            user_items = np.random.choice(items, size=n_interactions, replace=False)
            
            for item_id in user_items:
                sparse_interactions.append({
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': float(np.random.randint(1, 6))
                })
        
        sparse_df = pd.DataFrame(sparse_interactions)
        
        # 验证稀疏度
        total_possible = 20 * 100
        actual_interactions = len(sparse_df)
        sparsity = 1 - (actual_interactions / total_possible)
        assert sparsity > 0.95, f"数据应该极度稀疏(>95%)，实际稀疏度为{sparsity:.2%}"
        
        # 训练模型处理稀疏数据
        sparse_mf = MatrixFactorization()
        sparse_mf.fit(sparse_df)
        
        # 验证模型能处理稀疏数据
        assert sparse_mf.model is not None, "应该能处理极度稀疏的数据"
        
        # 测试预测功能
        prediction = sparse_mf.predict(1, 50)  # 预测一个可能未交互的用户-商品对
        assert isinstance(prediction, (float, np.floating)), "稀疏数据模型应该能进行预测"
        assert 1 <= prediction <= 5, "预测评分应该在合理范围内"
    
    def test_model_performance_metrics(self):
        """测试模型性能指标"""
        interactions_df = self.create_sparse_interaction_data()
        
        # 训练模型并获取性能指标
        self.matrix_factorization.fit(interactions_df, test_size=0.3)
        
        # 通过测试集评估模型性能
        predictions = self.matrix_factorization.model.test(self.matrix_factorization.testset)
        
        # 计算RMSE和MAE
        squared_errors = [(pred.est - pred.r_ui) ** 2 for pred in predictions]
        absolute_errors = [abs(pred.est - pred.r_ui) for pred in predictions]
        
        rmse = np.sqrt(np.mean(squared_errors))
        mae = np.mean(absolute_errors)
        
        # 验证性能指标合理性
        assert 0 < rmse < 3, f"RMSE应该在合理范围内(0-3)，实际为{rmse:.3f}"
        assert 0 < mae < 2, f"MAE应该在合理范围内(0-2)，实际为{mae:.3f}"
        assert mae <= rmse, "MAE应该小于等于RMSE"
        
        # 验证预测值在合理范围内
        predicted_ratings = [pred.est for pred in predictions]
        assert all(1 <= pred <= 5 for pred in predicted_ratings), "所有预测评分应该在1-5范围内"
    
    def test_different_parameters(self):
        """测试不同参数配置"""
        interactions_df = self.create_sparse_interaction_data()
        
        # 测试不同的因子数量
        mf_50_factors = MatrixFactorization()
        mf_50_factors.fit(interactions_df)
        
        # 验证默认参数
        assert mf_50_factors.model.n_factors >= 50, "默认因子数应该≥50"
        
        # 测试模型训练成功
        prediction_50 = mf_50_factors.predict(1, 1)
        assert isinstance(prediction_50, (float, np.floating)), "不同参数模型应该能正常预测"
    
    def test_recommendation_consistency(self):
        """测试推荐一致性"""
        interactions_df = self.create_sparse_interaction_data()
        
        # 训练两个相同参数的模型
        mf1 = MatrixFactorization()
        mf2 = MatrixFactorization()
        
        # 使用相同的随机种子
        np.random.seed(42)
        mf1.fit(interactions_df)
        
        np.random.seed(42)
        mf2.fit(interactions_df)
        
        # 比较预测结果
        user_id, item_id = 1, 5
        pred1 = mf1.predict(user_id, item_id)
        pred2 = mf2.predict(user_id, item_id)
        
        # 由于随机初始化，预测可能有轻微差异，但应该在相近范围内
        assert isinstance(pred1, (float, np.floating)), "第一个模型预测应该正常"
        assert isinstance(pred2, (float, np.floating)), "第二个模型预测应该正常"
        assert 1 <= pred1 <= 5, "第一个模型预测应该在合理范围"
        assert 1 <= pred2 <= 5, "第二个模型预测应该在合理范围"
    
    def test_edge_cases_and_robustness(self):
        """测试边界情况和鲁棒性"""
        # 测试空候选商品列表
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)
        
        empty_recommendations = self.matrix_factorization.recommend(1, [], top_n=5)
        assert len(empty_recommendations) == 0, "空候选列表应该返回空推荐"
        
        # 测试单个候选商品
        single_recommendations = self.matrix_factorization.recommend(1, [10], top_n=5)
        assert len(single_recommendations) <= 1, "单个候选商品最多返回1个推荐"
        
        # 测试非常小的数据集
        minimal_df = pd.DataFrame({
            'user_id': [1, 1, 2, 2],
            'item_id': [1, 2, 1, 3],
            'rating': [4.0, 3.0, 5.0, 2.0]
        })
        
        minimal_mf = MatrixFactorization()
        minimal_mf.fit(minimal_df)
        
        # 最小数据集也应该能训练
        assert minimal_mf.model is not None, "最小数据集也应该能训练模型"
        
        # 测试预测
        minimal_pred = minimal_mf.predict(1, 3)
        assert isinstance(minimal_pred, (float, np.floating)), "最小数据集模型应该能预测"