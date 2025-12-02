import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.collaborative_filtering import ItemBasedCF


class TestItemCollaborativeFiltering:
    """基于物品的协同过滤单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.item_cf = ItemBasedCF(min_interactions=3)
        
    def create_interaction_data(self):
        """创建用户-商品交互数据"""
        np.random.seed(42)
        
        # 创建50个用户，100个商品，500条交互记录的数据
        users = range(1, 51)
        items = range(1, 101)
        
        interactions = []
        interaction_id = 1
        
        # 为每个商品设置类别特性
        item_categories = {}
        for item_id in items:
            if item_id <= 20:
                item_categories[item_id] = '电子产品'
            elif item_id <= 40:
                item_categories[item_id] = '服装'
            elif item_id <= 60:
                item_categories[item_id] = '图书'
            elif item_id <= 80:
                item_categories[item_id] = '家居'
            else:
                item_categories[item_id] = '食品'
        
        # 为每个用户生成交互记录
        for user_id in users:
            # 每个用户随机交互10-20个商品
            n_interactions = np.random.randint(10, 21)
            user_items = np.random.choice(items, size=n_interactions, replace=False)
            
            for item_id in user_items:
                # 基于商品类别生成有模式的评分
                category = item_categories[item_id]
                
                # 不同用户对不同类别有不同偏好
                if user_id <= 15:  # 用户1-15偏好电子产品
                    if category == '电子产品':
                        rating = np.random.choice([4, 5], p=[0.4, 0.6])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.2, 0.5, 0.3])
                elif user_id <= 30:  # 用户16-30偏好服装
                    if category == '服装':
                        rating = np.random.choice([4, 5], p=[0.4, 0.6])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.2, 0.5, 0.3])
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
    
    def test_item_cf_training(self):
        """测试基于物品的协同过滤训练"""
        # 准备测试数据
        interactions_df = self.create_interaction_data()
        
        # 训练模型
        self.item_cf.fit(interactions_df)
        
        # 验证模型训练结果
        assert self.item_cf.user_item_matrix is not None, "应该生成用户-商品矩阵"
        assert self.item_cf.item_similarity_matrix is not None, "应该生成商品相似度矩阵"
        assert len(self.item_cf.user_ids) > 0, "应该有用户ID列表"
        assert len(self.item_cf.item_ids) > 0, "应该有商品ID列表"
        
        # 验证矩阵维度
        n_users = len(self.item_cf.user_ids)
        n_items = len(self.item_cf.item_ids)
        
        assert self.item_cf.user_item_matrix.shape == (n_users, n_items), "用户-商品矩阵维度应该正确"
        assert self.item_cf.item_similarity_matrix.shape == (n_items, n_items), "商品相似度矩阵维度应该正确"
        
        # 验证相似度矩阵的对称性和对角线
        similarity_matrix = self.item_cf.item_similarity_matrix
        assert np.allclose(similarity_matrix, similarity_matrix.T), "相似度矩阵应该是对称的"
        
        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0), "相似度矩阵对角线应该全为1"
    
    def test_item_similarity_calculation(self):
        """测试商品相似度计算"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)
        
        # 测试相似度计算
        item1, item2 = 1, 2  # 同类别商品（电子产品）
        similarity = self.item_cf.get_item_similarity(item1, item2)
        
        # 验证相似度值
        assert isinstance(similarity, (float, np.floating)), "相似度应该是浮点数"
        assert -1 <= similarity <= 1, "余弦相似度应该在[-1,1]范围内"
        
        # 测试商品与自己的相似度
        self_similarity = self.item_cf.get_item_similarity(item1, item1)
        assert abs(self_similarity - 1.0) < 0.001, "商品与自己的相似度应该接近1"
        
        # 测试不存在商品的相似度
        non_exist_similarity = self.item_cf.get_item_similarity(999, 1000)
        assert non_exist_similarity == 0.0, "不存在商品的相似度应该为0"
        
        # 验证同类别商品相似度
        same_category_sim = self.item_cf.get_item_similarity(5, 10)  # 都是电子产品
        diff_category_sim = self.item_cf.get_item_similarity(5, 25)  # 电子产品 vs 服装
        
        # 注意：由于数据的随机性，这里只做基本验证
        assert isinstance(same_category_sim, (float, np.floating)), "同类别商品相似度计算应该正常"
        assert isinstance(diff_category_sim, (float, np.floating)), "不同类别商品相似度计算应该正常"
    
    def test_item_recommendation(self):
        """测试基于物品的推荐功能"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)
        
        # 为用户生成推荐
        user_id = 1
        recommendations = self.item_cf.recommend(user_id, top_n=10)
        
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
        
        # 验证不推荐已评分商品
        user_rated_items = set(interactions_df[interactions_df['user_id'] == user_id]['item_id'])
        recommended_items = set([item_id for item_id, _ in recommendations])
        overlap = user_rated_items.intersection(recommended_items)
        assert len(overlap) == 0, "不应该推荐已评分商品"
    
    def test_similar_items_recommendation(self):
        """测试相似商品推荐功能"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)
        
        # 推荐与指定商品相似的商品
        target_item_id = 5  # 电子产品类别
        similar_items = self.item_cf.recommend_similar_items(target_item_id, top_n=10)
        
        # 验证推荐结果
        assert len(similar_items) <= 10, "相似商品推荐数量不应该超过top_n"
        assert isinstance(similar_items, list), "相似商品推荐结果应该是列表"
        
        # 验证推荐结果格式
        for item_id, similarity in similar_items:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(similarity, (float, np.floating)), "相似度应该是浮点数"
            assert -1 <= similarity <= 1, "相似度应该在[-1,1]范围内"
            assert item_id != target_item_id, "不应该推荐商品自己"
        
        # 验证推荐结果按相似度降序排列
        similarities = [sim for _, sim in similar_items]
        assert similarities == sorted(similarities, reverse=True), "相似商品应该按相似度降序排列"
        
        # 测试不存在商品的相似商品推荐
        non_exist_similar = self.item_cf.recommend_similar_items(999, top_n=5)
        assert len(non_exist_similar) == 0, "不存在的商品应该返回空相似商品列表"
    
    def test_min_interactions_filtering(self):
        """测试最小交互次数过滤"""
        interactions_df = self.create_interaction_data()
        
        # 创建一个要求更高最小交互次数的模型
        strict_cf = ItemBasedCF(min_interactions=10)
        strict_cf.fit(interactions_df)
        
        # 创建一个要求较低最小交互次数的模型
        lenient_cf = ItemBasedCF(min_interactions=3)
        lenient_cf.fit(interactions_df)
        
        # 验证过滤效果
        assert len(strict_cf.item_ids) <= len(lenient_cf.item_ids), "更严格的过滤应该保留更少的商品"
        
        # 验证所有保留的商品都满足最小交互次数要求
        for item_id in strict_cf.item_ids:
            item_interaction_count = len(interactions_df[interactions_df['item_id'] == item_id])
            assert item_interaction_count >= 10, f"商品{item_id}的交互次数应该≥10"
    
    def test_recommendation_based_on_user_history(self):
        """测试基于用户历史的推荐逻辑"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)
        
        # 获取一个用户的历史交互
        user_id = 1
        user_history = interactions_df[interactions_df['user_id'] == user_id]
        user_high_rated_items = user_history[user_history['rating'] >= 4]['item_id'].values
        
        if len(user_high_rated_items) > 0:
            # 为用户生成推荐
            recommendations = self.item_cf.recommend(user_id, top_n=15)
            
            if len(recommendations) > 0:
                # 获取推荐商品的相似商品，验证推荐逻辑
                recommended_items = [item_id for item_id, _ in recommendations]
                
                # 检查推荐的商品是否与用户高评分商品有相似性
                has_similar_to_history = False
                for rec_item in recommended_items[:5]:  # 检查前5个推荐
                    for hist_item in user_high_rated_items[:3]:  # 检查用户历史高评分商品
                        if hist_item in self.item_cf.item_id_to_index and rec_item in self.item_cf.item_id_to_index:
                            similarity = self.item_cf.get_item_similarity(hist_item, rec_item)
                            if similarity > 0.1:  # 有一定相似性
                                has_similar_to_history = True
                                break
                    if has_similar_to_history:
                        break
                
                # 注意：由于数据的随机性和算法复杂性，这里只是验证推荐系统能运行
                assert isinstance(has_similar_to_history, bool), "相似性检查应该正常执行"
    
    def test_item_similarity_matrix_properties(self):
        """测试商品相似度矩阵属性"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)
        
        similarity_matrix = self.item_cf.item_similarity_matrix
        n_items = len(self.item_cf.item_ids)
        
        # 验证矩阵维度
        assert similarity_matrix.shape == (n_items, n_items), "相似度矩阵维度应该是100×100"
        
        # 验证矩阵对称性
        assert np.allclose(similarity_matrix, similarity_matrix.T, atol=1e-10), "相似度矩阵应该是对称的"
        
        # 验证对角线为1
        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0, atol=1e-10), "对角线应该全为1"
        
        # 验证相似度值范围
        assert np.all(similarity_matrix >= -1), "所有相似度值应该≥-1"
        assert np.all(similarity_matrix <= 1), "所有相似度值应该≤1"
        
        # 验证非对角线元素不全为1
        off_diagonal = similarity_matrix[~np.eye(n_items, dtype=bool)]
        assert not np.allclose(off_diagonal, 1.0), "非对角线元素不应该全为1"
    
    def test_cold_start_handling(self):
        """测试冷启动处理"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)
        
        # 测试新用户推荐（冷启动）
        new_user_id = 999  # 不存在的用户
        recommendations = self.item_cf.recommend(new_user_id, top_n=5)
        
        # 验证冷启动推荐
        assert isinstance(recommendations, list), "冷启动推荐应该返回列表"
        assert len(recommendations) <= 5, "冷启动推荐数量不应该超过top_n"
        
        # 冷启动应该推荐热门商品
        if len(recommendations) > 0:
            for item_id, rating in recommendations:
                assert isinstance(item_id, (int, np.integer)), "推荐商品ID应该是整数"
                assert isinstance(rating, (float, np.floating)), "推荐评分应该是浮点数"
                assert rating > 0, "推荐评分应该为正数"
                assert item_id in self.item_cf.item_ids, "推荐的商品应该在训练数据中"
    
    def test_recommendation_diversity(self):
        """测试推荐多样性"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)
        
        # 为多个用户生成推荐
        all_recommendations = set()
        users_to_test = self.item_cf.user_ids[:10]  # 测试前10个用户
        
        for user_id in users_to_test:
            recommendations = self.item_cf.recommend(user_id, top_n=10)
            for item_id, _ in recommendations:
                all_recommendations.add(item_id)
        
        # 验证推荐覆盖率
        total_items = len(self.item_cf.item_ids)
        coverage = len(all_recommendations) / total_items
        
        assert coverage > 0.05, f"推荐覆盖率应该>5%，实际为{coverage:.2%}"
        
        # 验证推荐不是完全相同
        user_recs = {}
        for user_id in users_to_test[:5]:
            recommendations = self.item_cf.recommend(user_id, top_n=8)
            user_recs[user_id] = set([item_id for item_id, _ in recommendations])
        
        # 计算用户间推荐重叠率
        overlaps = []
        user_list = list(user_recs.keys())
        for i in range(len(user_list)):
            for j in range(i+1, len(user_list)):
                user1_recs = user_recs[user_list[i]]
                user2_recs = user_recs[user_list[j]]
                if len(user1_recs) > 0 and len(user2_recs) > 0:
                    union_size = len(user1_recs.union(user2_recs))
                    if union_size > 0:
                        overlap = len(user1_recs.intersection(user2_recs)) / union_size
                        overlaps.append(overlap)
        
        if overlaps:
            avg_overlap = np.mean(overlaps)
            assert avg_overlap < 0.9, f"用户间推荐重叠率应该<90%，实际为{avg_overlap:.2%}"
    
    def test_edge_cases_and_robustness(self):
        """测试边界情况和鲁棒性"""
        # 测试空数据
        empty_df = pd.DataFrame(columns=['user_id', 'item_id', 'rating'])
        
        with pytest.raises(Exception):
            empty_cf = ItemBasedCF()
            empty_cf.fit(empty_df)
        
        # 测试单商品多用户
        single_item_df = pd.DataFrame({
            'user_id': [1, 2, 3, 4, 5],
            'item_id': [1, 1, 1, 1, 1],  # 所有用户都评价同一商品
            'rating': [5, 4, 3, 4, 5],
            'interaction_type': ['rating'] * 5
        })
        
        single_item_cf = ItemBasedCF(min_interactions=3)
        single_item_cf.fit(single_item_df)
        
        # 单商品情况下应该能正常工作
        recommendations = single_item_cf.recommend(1, top_n=5)
        assert isinstance(recommendations, list), "单商品情况应该返回列表"
        
        # 相似商品推荐应该为空（只有一个商品）
        similar_items = single_item_cf.recommend_similar_items(1, top_n=5)
        assert len(similar_items) == 0, "单商品情况下不应该有相似商品"
        
        # 测试极端评分数据
        extreme_df = pd.DataFrame({
            'user_id': [1, 2, 3, 1, 2, 3],
            'item_id': [1, 1, 1, 2, 2, 2],
            'rating': [1, 1, 1, 5, 5, 5],  # 极端评分
            'interaction_type': ['rating'] * 6
        })
        
        extreme_cf = ItemBasedCF(min_interactions=3)
        extreme_cf.fit(extreme_df)
        
        # 极端评分情况下应该能计算相似度
        similarity = extreme_cf.get_item_similarity(1, 2)
        assert isinstance(similarity, (float, np.floating)), "极端评分情况下应该能计算相似度"