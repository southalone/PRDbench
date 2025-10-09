import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import ContentBasedRecommender


class TestTFIDFImplementation:
    """TF-IDF实现单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.recommender = ContentBasedRecommender()
        
    def create_items_data(self):
        """创建商品文本描述数据集"""
        items_data = {
            'item_id': range(1, 101),
            'title': [
                "苹果iPhone 14 Pro智能手机", "华为Mate50 Pro 5G手机", "小米13 Ultra徕卡相机", 
                "OPPO Find X6 Pro哈苏影像", "vivo X90 Pro+蔡司光学", "三星Galaxy S23 Ultra",
                "一加11骁龙8Gen2处理器", "魅族20 Pro无界设计", "索尼Xperia 1 V显示屏",
                "谷歌Pixel 7 Pro系统", "联想拯救者Y9000P游戏本", "戴尔XPS 13 Plus超极本",
                "华硕ROG玩家国度电竞", "惠普暗影精灵8游戏本", "ThinkPad X1商务办公",
                "MacBook Pro 14英寸专业", "Surface Laptop微软认证", "机械革命蛟龙16K电竞",
                "炫龙毁灭者DD2游戏", "神舟战神Z8性价比", "耐克Air Jordan篮球鞋",
                "阿迪达斯Ultraboost跑步鞋", "新百伦990v5复古跑鞋", "匡威All Star帆布鞋",
                "万斯Old Skool滑板鞋", "彪马Suede Classic板鞋", "安踏KT7汤普森篮球",
                "李宁韦德之道10篮球鞋", "361度专业跑步鞋", "特步竞速160X马拉松",
                "美的变频空调节能静音", "格力品悦壁挂式空调", "海尔统帅智能空调",
                "奥克斯金典变频空调", "TCL卧室空调制冷", "海信舒适家变频空调",
                "长虹悦享节能空调", "志高云空调远程控制", "科龙悦雅静音空调",
                "春兰经典机械空调", "西门子滚筒洗衣机", "海尔波轮洗衣机",
                "小天鹅比佛利洗护", "美的洗烘一体机", "松下罗密欧洗衣机",
                "LG蒸汽洗衣机除菌", "博世欧洲进口洗衣机", "惠而浦美式洗衣机",
                "三洋波轮洗衣机", "统帅海尔洗衣机"
            ] + [f"商品{i}智能设备" for i in range(51, 101)],
            'description': [
                "这是一款高端智能手机，具有强大的摄影功能和优秀的性能表现，适合商务和娱乐使用。",
                "5G网络支持，鸿蒙操作系统，拍照效果出色，是华为最新旗舰产品。",
                "搭载徕卡影像系统，骁龙8Gen2处理器，提供专业级拍照体验。",
                "哈苏影像技术加持，旗舰级拍照手机，色彩还原真实自然。",
                "蔡司光学镜头，极夜人像拍摄能力强，夜景模式效果出众。",
                "S Pen手写笔支持，大屏幕设计，适合办公和创作。",
                "骁龙8Gen2处理器，2K 120Hz曲面屏，游戏性能强劲。",
                "星纪魅族双品牌，无界设计理念，外观简约时尚。",
                "4K HDR OLED显示技术，索尼专业显示调校。",
                "原生Android系统，谷歌服务完整，纯净系统体验。"
            ] + [f"这是商品{i}的详细描述，包含多种功能特性和使用场景。" for i in range(11, 101)],
            'category': ['手机'] * 10 + ['电脑'] * 10 + ['鞋服'] * 10 + ['家电'] * 20 + ['其他'] * 50,
            'tags': [
                "智能手机,摄影,高端", "5G,华为,旗舰", "徕卡,拍照,骁龙", "哈苏,影像,拍照",
                "蔡司,光学,夜景", "三星,S Pen,大屏", "一加,游戏,性能", "魅族,设计,时尚",
                "索尼,显示,专业", "谷歌,Android,纯净", "联想,游戏本,高性能", "戴尔,超极本,轻薄",
                "华硕,电竞,游戏", "惠普,游戏,性能", "联想,商务,办公", "苹果,专业,设计",
                "微软,认证,办公", "机械革命,电竞,游戏", "炫龙,游戏,高端", "神舟,性价比,游戏",
                "耐克,篮球,运动", "阿迪达斯,跑步,运动", "新百伦,复古,跑步", "匡威,帆布,潮流",
                "万斯,滑板,街头", "彪马,复古,经典", "安踏,篮球,专业", "李宁,篮球,专业",
                "361度,跑步,专业", "特步,马拉松,跑步", "美的,空调,节能", "格力,空调,家用",
                "海尔,智能,空调", "奥克斯,变频,空调", "TCL,制冷,空调", "海信,变频,智能",
                "长虹,节能,环保", "志高,远程,智能", "科龙,静音,舒适", "春兰,经典,传统",
                "西门子,洗衣机,滚筒", "海尔,洗衣机,波轮", "小天鹅,洗护,高端", "美的,洗烘,智能",
                "松下,日式,精工", "LG,蒸汽,除菌", "博世,进口,品质", "惠而浦,美式,大容量",
                "三洋,波轮,实用", "统帅,性价比,实用"
            ] + [f"标签{i},功能{i},特色{i}" for i in range(51, 101)]
        }
        
        return pd.DataFrame(items_data)
    
    def test_tfidf_implementation(self):
        """测试TF-IDF特征提取实现"""
        # 准备测试数据
        items_df = self.create_items_data()
        
        # 训练模型
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        # 验证TF-IDF特征矩阵生成
        assert self.recommender.item_features is not None, "应该生成TF-IDF特征矩阵"
        assert self.recommender.tfidf_vectorizer is not None, "应该创建TF-IDF向量化器"
        
        # 验证特征矩阵维度
        n_items = len(items_df)
        feature_matrix = self.recommender.item_features
        assert feature_matrix.shape[0] == n_items, f"特征矩阵行数应该等于商品数量{n_items}"
        
        # 验证特征矩阵不全为零
        assert feature_matrix.sum() > 0, "特征矩阵不应该全为零"
        
        # 验证相似度矩阵生成
        assert self.recommender.item_similarity_matrix is not None, "应该生成商品相似度矩阵"
        assert self.recommender.item_similarity_matrix.shape == (n_items, n_items), "相似度矩阵维度应该正确"
        
        # 验证相似度矩阵的对称性
        similarity_matrix = self.recommender.item_similarity_matrix
        assert np.allclose(similarity_matrix, similarity_matrix.T), "相似度矩阵应该是对称的"
        
        # 验证对角线为1（自己与自己的相似度）
        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0), "相似度矩阵对角线应该全为1"
    
    def test_similarity_calculation(self):
        """测试相似度计算准确性"""
        items_df = self.create_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        # 测试相同类别商品的相似度
        phone_items = items_df[items_df['category'] == '手机']['item_id'].values[:5]
        computer_items = items_df[items_df['category'] == '电脑']['item_id'].values[:5]
        
        # 计算手机类别内部相似度
        phone_similarities = []
        for i in range(len(phone_items)):
            for j in range(i+1, len(phone_items)):
                sim = self.recommender.get_item_similarity(phone_items[i], phone_items[j])
                phone_similarities.append(sim)
        
        # 计算手机与电脑类别间相似度
        cross_similarities = []
        for phone_id in phone_items:
            for computer_id in computer_items:
                sim = self.recommender.get_item_similarity(phone_id, computer_id)
                cross_similarities.append(sim)
        
        # 验证同类别商品相似度较高
        avg_phone_sim = np.mean(phone_similarities)
        avg_cross_sim = np.mean(cross_similarities)
        
        assert avg_phone_sim > avg_cross_sim, "同类别商品相似度应该高于跨类别相似度"
        assert avg_phone_sim > 0.1, "同类别商品相似度应该有合理的数值"
    
    def test_recommend_similar_items(self):
        """测试相似商品推荐功能"""
        items_df = self.create_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        # 测试推荐相似商品
        target_item_id = 1  # 苹果iPhone
        similar_items = self.recommender.recommend_similar_items(target_item_id, top_n=5)
        
        # 验证推荐结果
        assert len(similar_items) <= 5, "推荐数量不应该超过要求的top_n"
        assert len(similar_items) > 0, "应该有相似商品推荐"
        
        # 验证推荐结果格式
        for item_id, similarity in similar_items:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(similarity, (float, np.floating)), "相似度应该是浮点数"
            assert 0 <= similarity <= 1, "相似度应该在[0,1]范围内"
            assert item_id != target_item_id, "不应该推荐商品自己"
        
        # 验证推荐结果按相似度降序排列
        similarities = [sim for _, sim in similar_items]
        assert similarities == sorted(similarities, reverse=True), "推荐结果应该按相似度降序排列"
    
    def test_user_profile_recommendation(self):
        """测试基于用户画像的推荐"""
        items_df = self.create_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        # 创建用户偏好画像
        user_preferences = {
            'interests': '智能手机 拍照 摄影',
            'brand_preference': '苹果 华为',
            'category': '手机 数码'
        }
        
        # 获取基于用户画像的推荐
        recommendations = self.recommender.recommend_for_user_profile(
            user_preferences, items_df, top_n=10
        )
        
        # 验证推荐结果
        assert len(recommendations) <= 10, "推荐数量不应该超过要求的top_n"
        assert len(recommendations) > 0, "应该有推荐结果"
        
        # 验证推荐结果格式
        for item_id, score in recommendations:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(score, (float, np.floating)), "推荐分数应该是浮点数"
            assert score >= 0, "推荐分数应该为非负数"
        
        # 验证推荐结果按分数降序排列
        scores = [score for _, score in recommendations]
        assert scores == sorted(scores, reverse=True), "推荐结果应该按分数降序排列"
        
        # 验证推荐的商品与用户偏好相关
        recommended_items = items_df[items_df['item_id'].isin([item_id for item_id, _ in recommendations])]
        phone_count = len(recommended_items[recommended_items['category'] == '手机'])
        phone_ratio = phone_count / len(recommended_items) if len(recommended_items) > 0 else 0
        
        assert phone_ratio >= 0.3, "推荐结果中手机类商品占比应该较高（≥30%）"
    
    def test_tfidf_parameters(self):
        """测试TF-IDF参数配置"""
        items_df = self.create_items_data()
        
        # 测试不同的参数配置
        recommender = ContentBasedRecommender()
        recommender.fit(items_df, text_columns=['title', 'description'])
        
        # 验证TF-IDF向量化器参数
        vectorizer = recommender.tfidf_vectorizer
        assert hasattr(vectorizer, 'max_features'), "应该配置max_features参数"
        assert hasattr(vectorizer, 'min_df'), "应该配置min_df参数"
        assert hasattr(vectorizer, 'max_df'), "应该配置max_df参数"
        assert vectorizer.ngram_range == (1, 2), "应该使用1-2gram"
        
        # 验证词汇表大小合理
        feature_names = vectorizer.get_feature_names_out()
        assert len(feature_names) > 10, "词汇表应该包含足够的特征"
        assert len(feature_names) < 10000, "词汇表大小应该在合理范围内"
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试空数据
        empty_df = pd.DataFrame(columns=['item_id', 'title', 'description'])
        
        with pytest.raises(Exception):
            self.recommender.fit(empty_df)
        
        # 测试单个商品
        single_item_df = pd.DataFrame({
            'item_id': [1],
            'title': ['测试商品'],
            'description': ['这是一个测试商品'],
            'tags': ['测试,商品']
        })
        
        self.recommender.fit(single_item_df)
        similar_items = self.recommender.recommend_similar_items(1, top_n=5)
        assert len(similar_items) == 0, "单个商品不应该有相似商品推荐"
        
        # 测试不存在的商品ID
        items_df = self.create_items_data()
        self.recommender.fit(items_df)
        
        similarity = self.recommender.get_item_similarity(999, 1000)
        assert similarity == 0.0, "不存在的商品ID相似度应该为0"
        
        similar_items = self.recommender.recommend_similar_items(999)
        assert len(similar_items) == 0, "不存在的商品ID不应该有推荐结果"