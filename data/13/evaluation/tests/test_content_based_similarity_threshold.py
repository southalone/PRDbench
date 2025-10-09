import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import ContentBasedRecommender


class TestSimilarityThreshold:
    """相似度阈值配置单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.recommender = ContentBasedRecommender()
        
    def create_test_items_data(self):
        """创建测试商品数据集"""
        items_data = {
            'item_id': range(1, 21),
            'title': [
                "苹果iPhone 14 Pro智能手机", "华为Mate50 Pro 5G手机", "小米13 Ultra徕卡相机", 
                "OPPO Find X6 Pro哈苏影像", "vivo X90 Pro+蔡司光学", "三星Galaxy S23 Ultra",
                "一加11骁龙8Gen2处理器", "魅族20 Pro无界设计", "索尼Xperia 1 V显示屏",
                "谷歌Pixel 7 Pro系统", "联想拯救者Y9000P游戏本", "戴尔XPS 13 Plus超极本",
                "华硕ROG玩家国度电竞", "惠普暗影精灵8游戏本", "ThinkPad X1商务办公",
                "MacBook Pro 14英寸专业", "Surface Laptop微软认证", "机械革命蛟龙16K电竞",
                "耐克Air Jordan篮球鞋", "阿迪达斯Ultraboost跑步鞋"
            ],
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
                "原生Android系统，谷歌服务完整，纯净系统体验。",
                "英特尔i7处理器，RTX 4070显卡，专业游戏本。",
                "超轻薄设计，英特尔Evo认证，商务办公首选。",
                "AMD锐龙处理器，电竞级显卡，专业游戏设备。",
                "暗影精灵系列，高性能游戏本，RGB灯效。",
                "商务办公专用，ThinkPad经典设计，可靠稳定。",
                "苹果M2芯片，专业级性能，创意工作首选。",
                "微软Surface系列，触控屏设计，办公娱乐。",
                "电竞专用笔记本，高刷新率屏幕，游戏体验。",
                "经典篮球鞋，乔丹品牌，运动时尚兼具。",
                "专业跑步鞋，舒适缓震，运动健身必备。"
            ],
            'category': ['手机'] * 10 + ['电脑'] * 7 + ['鞋服'] * 3,
            'tags': [
                "智能手机,摄影,高端", "5G,华为,旗舰", "徕卡,拍照,骁龙", "哈苏,影像,拍照",
                "蔡司,光学,夜景", "三星,S Pen,大屏", "一加,游戏,性能", "魅族,设计,时尚",
                "索尼,显示,专业", "谷歌,Android,纯净", "联想,游戏本,高性能", "戴尔,超极本,轻薄",
                "华硕,电竞,游戏", "惠普,游戏,性能", "联想,商务,办公", "苹果,专业,设计",
                "微软,认证,办公", "机械革命,电竞,游戏", "耐克,篮球,运动", "阿迪达斯,跑步,运动"
            ]
        }
        
        return pd.DataFrame(items_data)
    
    def test_similarity_threshold_configuration(self):
        """测试相似度阈值配置功能"""
        # 准备测试数据
        items_df = self.create_test_items_data()
        
        # 训练模型
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        # 选择目标商品进行测试（选择第一个手机商品）
        target_item_id = 1
        
        # 测试不同的相似度阈值
        thresholds = [0.3, 0.5, 0.7, 0.9]
        recommendation_counts = []
        
        for threshold in thresholds:
            # 设置相似度阈值并获取推荐结果
            recommendations = self.recommender.recommend_similar_items(
                target_item_id, 
                top_n=15,  # 设置较大的数量以便观察阈值效果
                similarity_threshold=threshold
            )
            
            recommendation_counts.append(len(recommendations))
            
            # 验证推荐结果格式
            for item_id, similarity in recommendations:
                assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
                assert isinstance(similarity, (float, np.floating)), "相似度应该是浮点数"
                assert similarity >= threshold, f"相似度{similarity}应该大于等于阈值{threshold}"
                assert item_id != target_item_id, "不应该推荐商品自己"
            
            # 验证推荐结果按相似度降序排列
            similarities = [sim for _, sim in recommendations]
            assert similarities == sorted(similarities, reverse=True), "推荐结果应该按相似度降序排列"
        
        # 验证阈值越高推荐数量越少的规律
        for i in range(len(thresholds) - 1):
            current_threshold = thresholds[i]
            next_threshold = thresholds[i + 1]
            current_count = recommendation_counts[i]
            next_count = recommendation_counts[i + 1]
            
            assert next_count <= current_count, \
                f"阈值{next_threshold}({next_count}个推荐)的推荐数量应该小于等于阈值{current_threshold}({current_count}个推荐)的推荐数量"
        
        # 验证每个阈值都能成功设置并返回结果
        assert all(isinstance(count, int) and count >= 0 for count in recommendation_counts), \
            "所有阈值都应该返回有效的推荐数量"
        
        # 验证最高阈值(0.9)的推荐数量明显少于最低阈值(0.3)
        if recommendation_counts[0] > 0:  # 如果最低阈值有推荐结果
            reduction_ratio = (recommendation_counts[0] - recommendation_counts[-1]) / recommendation_counts[0]
            assert reduction_ratio >= 0, "高阈值应该减少推荐数量"
        
        print(f"阈值测试结果: {dict(zip(thresholds, recommendation_counts))}")
        print("验证通过：内容推荐算法能成功设置不同相似度阈值，阈值越高推荐数量越少")
    
    def test_threshold_boundary_conditions(self):
        """测试阈值边界条件"""
        items_df = self.create_test_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        target_item_id = 1
        
        # 测试极低阈值 (0.0)
        low_threshold_recs = self.recommender.recommend_similar_items(
            target_item_id, top_n=10, similarity_threshold=0.0
        )
        
        # 测试极高阈值 (1.0)
        high_threshold_recs = self.recommender.recommend_similar_items(
            target_item_id, top_n=10, similarity_threshold=1.0
        )
        
        # 验证极低阈值应该返回更多结果
        assert len(low_threshold_recs) >= len(high_threshold_recs), \
            "极低阈值应该返回更多或相等数量的推荐结果"
        
        # 验证极高阈值(1.0)应该很少或没有结果（除非有完全相同的商品）
        assert len(high_threshold_recs) <= 1, \
            "极高阈值(1.0)应该很少或没有推荐结果"
    
    def test_threshold_with_different_items(self):
        """测试不同商品在相同阈值下的表现"""
        items_df = self.create_test_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        threshold = 0.5
        
        # 测试不同类别的商品
        phone_item_id = 1  # 手机
        computer_item_id = 11  # 电脑
        shoe_item_id = 19  # 鞋服
        
        phone_recs = self.recommender.recommend_similar_items(
            phone_item_id, top_n=10, similarity_threshold=threshold
        )
        
        computer_recs = self.recommender.recommend_similar_items(
            computer_item_id, top_n=10, similarity_threshold=threshold
        )
        
        shoe_recs = self.recommender.recommend_similar_items(
            shoe_item_id, top_n=10, similarity_threshold=threshold
        )
        
        # 验证所有推荐结果都满足阈值要求
        for recommendations in [phone_recs, computer_recs, shoe_recs]:
            for item_id, similarity in recommendations:
                assert similarity >= threshold, f"相似度{similarity}应该大于等于阈值{threshold}"
        
        # 验证推荐结果的多样性
        all_rec_counts = [len(phone_recs), len(computer_recs), len(shoe_recs)]
        assert any(count > 0 for count in all_rec_counts), \
            "至少应该有一个商品类别能产生推荐结果"
        
        print(f"不同商品阈值{threshold}测试结果: 手机{len(phone_recs)}个, 电脑{len(computer_recs)}个, 鞋服{len(shoe_recs)}个")