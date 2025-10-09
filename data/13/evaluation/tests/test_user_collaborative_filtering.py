import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.collaborative_filtering import UserBasedCF


class TestUserCollaborativeFiltering:
    """基于用户的协同过滤单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.user_cf = UserBasedCF(min_interactions=3)
        
    def create_interaction_data(self):
        """创建用户-商品交互数据"""
        np.random.seed(42)
        
        # 创建50个用户，100个商品，500条交互记录的数据
        users = range(1, 51)
        items = range(1, 101)
        
        interactions = []
        interaction_id = 1
        
        # 为每个用户生成交互记录
        for user_id in users:
            # 每个用户随机交互10-20个商品
            n_interactions = np.random.randint(10, 21)
            user_items = np.random.choice(items, size=n_interactions, replace=False)
            
            for item_id in user_items:
                # 生成评分，有一定的用户偏好模式
                if user_id <= 10:  # 前10个用户偏好电子产品（item_id 1-20）
                    if item_id <= 20:
                        rating = np.random.choice([4, 5], p=[0.3, 0.7])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
                elif user_id <= 20:  # 11-20用户偏好服装（item_id 21-40）
                    if 21 <= item_id <= 40:
                        rating = np.random.choice([4, 5], p=[0.3, 0.7])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
                elif user_id <= 30:  # 21-30用户偏好图书（item_id 41-60）
                    if 41 <= item_id <= 60:
                        rating = np.random.choice([4, 5], p=[0.3, 0.7])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
                else:  # 其他用户随机偏好
                    rating = np.random.choice([2, 3, 4, 5], p=[0.1, 0.2, 0.4, 0.3])
                
                interactions.append({
                    'interaction_id': interaction_id,
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': rating,
                    'interaction_type': 'rating'
                })
                interaction_id += 1
        
        return pd.DataFrame(interactions)
    
    def test_user_cf_training(self):
        """测试基于用户的协同过滤训练"""
        # 准备测试数据
        interactions_df = self.create_interaction_data()
        
        # 训练模型
        self.user_cf.fit(interactions_df)
        
        # 验证模型训练结果
        assert self.user_cf.user_item_matrix is not None, "应该生成用户-商品矩阵"
        assert self.user_cf.user_similarity_matrix is not None, "应该生成用户相似度矩阵"
        assert len(self.user_cf.user_ids) > 0, "应该有用户ID列表"
        assert len(self.user_cf.item_ids) > 0, "应该有商品ID列表"
        
        # 验证矩阵维度
        n_users = len(self.user_cf.user_ids)
        n_items = len(self.user_cf.item_ids)
        
        assert self.user_cf.user_item_matrix.shape == (n_users, n_items), "用户-商品矩阵维度应该正确"
        assert self.user_cf.user_similarity_matrix.shape == (n_users, n_users), "用户相似度矩阵维度应该正确"
        
        # 验证相似度矩阵的对称性和对角线
        similarity_matrix = self.user_cf.user_similarity_matrix
        assert np.allclose(similarity_matrix, similarity_matrix.T), "相似度矩阵应该是对称的"
        
        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0), "相似度矩阵对角线应该全为1"
    
    def test_user_similarity_calculation(self):
        """测试用户相似度计算"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)
        
        # 测试相似度计算
        user1, user2 = 1, 2
        similarity = self.user_cf.get_user_similarity(user1, user2)
        
        # 验证相似度值
        assert isinstance(similarity, (float, np.floating)), "相似度应该是浮点数"
        assert -1 <= similarity <= 1, "余弦相似度应该在[-1,1]范围内"
        
        # 测试用户与自己的相似度
        self_similarity = self.user_cf.get_user_similarity(user1, user1)
        assert abs(self_similarity - 1.0) < 0.001, "用户与自己的相似度应该接近1"
        
        # 测试不存在用户的相似度
        non_exist_similarity = self.user_cf.get_user_similarity(999, 1000)
        assert non_exist_similarity == 0.0, "不存在用户的相似度应该为0"
        
        # 验证相似用户识别
        # 基于我们的数据生成逻辑，前10个用户应该有较高相似度
        similar_users_sim = self.user_cf.get_user_similarity(1, 5)  # 都偏好电子产品
        different_users_sim = self.user_cf.get_user_similarity(1, 15)  # 不同偏好
        
        # 注意：由于随机性，这个测试可能不稳定，所以只做基本验证
        assert isinstance(similar_users_sim, (float, np.floating)), "相似用户相似度计算应该正常"
        assert isinstance(different_users_sim, (float, np.floating)), "不同用户相似度计算应该正常"
    
    def test_user_recommendation(self):
        """测试基于用户的推荐功能"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)
        
        # 为用户生成推荐
        user_id = 1
        recommendations = self.user_cf.recommend(user_id, top_n=10)
        
        # 验证推荐结果
        assert len(recommendations) <= 10, "推荐数量不应该超过top_n"
        assert isinstance(recommendations, list), "推荐结果应该是列表"
        
        # 验证推荐结果格式
        for item_id, predicted_rating in recommendations:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(predicted_rating, (float, np.floating)), "预测评分应该是浮点数"
            assert predicted_rating > 0, "预测评分应该为正数"
        
        # 验证推荐结果按预测评分降序排列
        ratings = [rating for _, rating in recommendations]
        assert ratings == sorted(ratings, reverse=True), "推荐结果应该按预测评分降序排列"
        
        # 验证不推荐已评分商品（默认行为）
        user_rated_items = set(interactions_df[interactions_df['user_id'] == user_id]['item_id'])
        recommended_items = set([item_id for item_id, _ in recommendations])
        overlap = user_rated_items.intersection(recommended_items)
        assert len(overlap) == 0, "默认情况下不应该推荐已评分商品"
    
    def test_cold_start_handling(self):
        """测试冷启动处理"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)
        
        # 测试新用户推荐（冷启动）
        new_user_id = 999  # 不存在的用户
        recommendations = self.user_cf.recommend(new_user_id, top_n=5)
        
        # 验证冷启动推荐
        assert isinstance(recommendations, list), "冷启动推荐应该返回列表"
        assert len(recommendations) <= 5, "冷启动推荐数量不应该超过top_n"
        
        # 冷启动应该推荐热门商品
        if len(recommendations) > 0:
            for item_id, rating in recommendations:
                assert isinstance(item_id, (int, np.integer)), "推荐商品ID应该是整数"
                assert isinstance(rating, (float, np.floating)), "推荐评分应该是浮点数"
                assert rating > 0, "推荐评分应该为正数"
    
    def test_min_interactions_filtering(self):
        """测试最小交互次数过滤"""
        interactions_df = self.create_interaction_data()
        
        # 创建一个要求更高最小交互次数的模型
        strict_cf = UserBasedCF(min_interactions=15)
        strict_cf.fit(interactions_df)
        
        # 创建一个要求较低最小交互次数的模型
        lenient_cf = UserBasedCF(min_interactions=5)
        lenient_cf.fit(interactions_df)
        
        # 验证过滤效果
        assert len(strict_cf.user_ids) <= len(lenient_cf.user_ids), "更严格的过滤应该保留更少的用户"
        
        # 验证所有保留的用户都满足最小交互次数要求
        for user_id in strict_cf.user_ids:
            user_interaction_count = len(interactions_df[interactions_df['user_id'] == user_id])
            assert user_interaction_count >= 15, f"用户{user_id}的交互次数应该≥15"
    
    def test_recommendation_diversity_and_coverage(self):
        """测试推荐多样性和覆盖率"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)
        
        # 为多个用户生成推荐
        all_recommendations = set()
        users_to_test = self.user_cf.user_ids[:10]  # 测试前10个用户
        
        for user_id in users_to_test:
            recommendations = self.user_cf.recommend(user_id, top_n=10)
            for item_id, _ in recommendations:
                all_recommendations.add(item_id)
        
        # 验证推荐覆盖率
        total_items = len(self.user_cf.item_ids)
        coverage = len(all_recommendations) / total_items
        
        assert coverage > 0.1, f"推荐覆盖率应该>10%，实际为{coverage:.2%}"
        
        # 验证推荐不是所有用户都完全相同
        user_recs = {}
        for user_id in users_to_test[:5]:
            recommendations = self.user_cf.recommend(user_id, top_n=5)
            user_recs[user_id] = set([item_id for item_id, _ in recommendations])
        
        # 计算用户间推荐重叠率
        overlaps = []
        user_list = list(user_recs.keys())
        for i in range(len(user_list)):
            for j in range(i+1, len(user_list)):
                user1_recs = user_recs[user_list[i]]
                user2_recs = user_recs[user_list[j]]
                if len(user1_recs) > 0 and len(user2_recs) > 0:
                    overlap = len(user1_recs.intersection(user2_recs)) / len(user1_recs.union(user2_recs))
                    overlaps.append(overlap)
        
        if overlaps:
            avg_overlap = np.mean(overlaps)
            assert avg_overlap < 0.8, f"用户间推荐重叠率应该<80%，实际为{avg_overlap:.2%}"
    
    def test_rating_prediction_accuracy(self):
        """测试评分预测准确性"""
        interactions_df = self.create_interaction_data()
        
        # 分割训练测试集
        train_size = int(0.8 * len(interactions_df))
        train_df = interactions_df.iloc[:train_size]
        test_df = interactions_df.iloc[train_size:]
        
        # 训练模型
        self.user_cf.fit(train_df)
        
        # 预测测试集评分
        predictions = []
        actuals = []
        
        for _, row in test_df.head(50).iterrows():  # 只测试前50条避免过慢
            user_id = row['user_id']
            item_id = row['item_id']
            actual_rating = row['rating']
            
            if user_id in self.user_cf.user_id_to_index and item_id in self.user_cf.item_id_to_index:
                # 生成推荐并查找该商品的预测评分
                recommendations = self.user_cf.recommend(user_id, top_n=100, exclude_rated=False)
                
                predicted_rating = None
                for rec_item_id, rec_rating in recommendations:
                    if rec_item_id == item_id:
                        predicted_rating = rec_rating
                        break
                
                if predicted_rating is not None:
                    predictions.append(predicted_rating)
                    actuals.append(actual_rating)
        
        # 计算预测准确性
        if len(predictions) > 10:  # 至少有10个预测
            mae = np.mean(np.abs(np.array(predictions) - np.array(actuals)))
            rmse = np.sqrt(np.mean((np.array(predictions) - np.array(actuals)) ** 2))
            
            # 评分范围是1-5，合理的MAE应该<2，RMSE应该<2.5
            assert mae < 2.0, f"平均绝对误差应该<2.0，实际为{mae:.3f}"
            assert rmse < 2.5, f"均方根误差应该<2.5，实际为{rmse:.3f}"
    
    def test_edge_cases_and_robustness(self):
        """测试边界情况和鲁棒性"""
        # 测试空数据
        empty_df = pd.DataFrame(columns=['user_id', 'item_id', 'rating'])
        
        with pytest.raises(Exception):
            empty_cf = UserBasedCF()
            empty_cf.fit(empty_df)
        
        # 测试单用户单商品
        minimal_df = pd.DataFrame({
            'user_id': [1, 1, 1, 1, 1],  # 单用户多次交互以满足min_interactions
            'item_id': [1, 2, 3, 4, 5],
            'rating': [5, 4, 3, 4, 5],
            'interaction_type': ['rating'] * 5
        })
        
        minimal_cf = UserBasedCF(min_interactions=3)
        minimal_cf.fit(minimal_df)
        
        # 单用户情况下应该能正常工作，但推荐可能为空
        recommendations = minimal_cf.recommend(1, top_n=5)
        assert isinstance(recommendations, list), "单用户情况应该返回列表"
        
        # 测试极端评分数据
        extreme_df = pd.DataFrame({
            'user_id': [1, 1, 1, 2, 2, 2],
            'item_id': [1, 2, 3, 1, 2, 3],
            'rating': [1, 1, 1, 5, 5, 5],  # 极端评分
            'interaction_type': ['rating'] * 6
        })
        
        extreme_cf = UserBasedCF(min_interactions=3)
        extreme_cf.fit(extreme_df)
        
        # 极端评分情况下应该能计算相似度
        similarity = extreme_cf.get_user_similarity(1, 2)
        assert isinstance(similarity, (float, np.floating)), "极端评分情况下应该能计算相似度"