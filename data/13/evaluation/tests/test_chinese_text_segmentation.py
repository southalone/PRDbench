import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import ContentBasedRecommender
from data_old.preprocessor import DataPreprocessor


class TestChineseTextSegmentation:
    """中文分词处理单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.content_recommender = ContentBasedRecommender()
        self.preprocessor = DataPreprocessor()
        
    def create_chinese_text_data(self):
        """创建包含中文文本的测试数据"""
        chinese_texts = [
            "苹果iPhone 14 Pro智能手机 256GB 深空黑色",
            "华为Mate50 Pro 5G手机 鸿蒙系统 拍照神器",
            "小米13 Ultra徕卡相机 骁龙8Gen2处理器",
            "OPPO Find X6 Pro 哈苏影像旗舰拍照手机",
            "vivo X90 Pro+ 蔡司光学镜头 极夜人像",
            "三星Galaxy S23 Ultra 5G 智能S Pen手写笔",
            "一加11 骁龙8Gen2 2K 120Hz曲面屏幕",
            "魅族20 Pro 无界设计 星纪魅族双品牌",
            "索尼Xperia 1 V 4K HDR OLED显示屏",
            "谷歌Pixel 7 Pro 原生Android系统体验",
            "联想拯救者Y9000P 游戏笔记本电脑",
            "戴尔XPS 13 Plus 超极本轻薄便携",
            "华硕ROG 玩家国度 电竞游戏本",
            "惠普暗影精灵8 高性能游戏笔记本",
            "ThinkPad X1 Carbon 商务办公本",
            "MacBook Pro 14英寸 M2芯片专业版",
            "Surface Laptop 5 微软官方认证",
            "机械革命 蛟龙16K 电竞游戏本",
            "炫龙 毁灭者DD2 高端游戏笔记本",
            "神舟战神 Z8-CU7NS 性价比游戏本",
            "耐克Air Jordan 1 经典复古篮球鞋",
            "阿迪达斯Ultraboost 22 跑步运动鞋",
            "新百伦990v5 美产限量版复古跑鞋",
            "匡威All Star 经典帆布鞋潮流单品",
            "万斯Old Skool 滑板鞋街头潮牌",
            "彪马Suede Classic 复古板鞋经典款",
            "安踏KT7 汤普森签名篮球战靴",
            "李宁韦德之道10 专业篮球鞋",
            "361度 国际线专业跑步鞋",
            "特步 竞速160X 马拉松跑鞋",
            "美的变频空调 1.5匹 节能静音",
            "格力品悦 壁挂式家用冷暖空调",
            "海尔统帅 智能WiFi控制空调",
            "奥克斯 金典系列 变频冷暖空调",
            "TCL 卧室空调 快速制冷制热",
            "海信 舒适家 智能变频空调",
            "长虹 悦享系列 节能环保空调",
            "志高 云空调 手机APP远程控制",
            "科龙 悦雅系列 静音舒适空调",
            "春兰 经典款 传统机械式空调",
            "西门子 滚筒洗衣机 10KG大容量",
            "海尔 波轮洗衣机 全自动家用",
            "小天鹅 比佛利 高端洗护一体机",
            "美的 洗烘一体机 智能投放",
            "松下 罗密欧系列 日式精工",
            "LG 蒸汽洗衣机 除菌护理功能",
            "博世 欧洲进口 滚筒洗衣机",
            "惠而浦 美式 大容量洗衣机",
            "三洋 波轮洗衣机 经济实用型",
            "统帅 海尔子品牌 性价比洗衣机"
        ]
        
        items_df = pd.DataFrame({
            'item_id': range(1, len(chinese_texts) + 1),
            'title': chinese_texts,
            'description': [f"这是{text}的详细描述" for text in chinese_texts],
            'category': ['手机', '手机', '手机', '手机', '手机', '手机', '手机', '手机', '手机', '手机',
                        '电脑', '电脑', '电脑', '电脑', '电脑', '电脑', '电脑', '电脑', '电脑', '电脑',
                        '鞋服', '鞋服', '鞋服', '鞋服', '鞋服', '鞋服', '鞋服', '鞋服', '鞋服', '鞋服',
                        '家电', '家电', '家电', '家电', '家电', '家电', '家电', '家电', '家电', '家电',
                        '家电', '家电', '家电', '家电', '家电', '家电', '家电', '家电', '家电', '家电']
        })
        
        return items_df
    
    def test_chinese_text_segmentation(self):
        """测试中文分词功能"""
        # 准备测试数据
        items_df = self.create_chinese_text_data()
        
        # 测试基于内容推荐的中文分词
        text_columns = ['title', 'description']
        combined_texts = self.content_recommender._combine_text_features(items_df, text_columns)
        
        # 验证分词结果
        assert len(combined_texts) == len(items_df), "分词结果数量应该与输入数据相同"
        
        # 验证分词质量：检查是否包含合理的词汇分隔
        sample_text = combined_texts[0]  # 第一个商品的分词结果
        assert ' ' in sample_text, "分词结果应该包含空格分隔的词汇"
        
        # 验证关键词识别准确性
        phone_texts = combined_texts[:10]  # 手机类商品
        phone_keywords = ['iPhone', '华为', '小米', 'OPPO', 'vivo', '手机', '智能', '相机']
        
        # 计算每个文本至少包含一个相关关键词的比例
        texts_with_keywords = 0
        for text in phone_texts:
            has_keyword = any(keyword in text for keyword in phone_keywords)
            if has_keyword:
                texts_with_keywords += 1
        
        accuracy = texts_with_keywords / len(phone_texts) if phone_texts else 0
        assert accuracy >= 0.6, f"分词准确率应该≥60%，实际为{accuracy:.2%}"
        
        # 验证不同类别商品的分词差异性
        categories = ['手机', '电脑', '鞋服', '家电']
        category_texts = {}
        
        for i, category in enumerate(categories):
            start_idx = i * 10
            end_idx = (i + 1) * 10
            category_texts[category] = combined_texts[start_idx:end_idx]
        
        # 验证每个类别都有特定的关键词
        category_keywords = {
            '手机': ['手机', '智能', '相机', '处理器', '拍照'],
            '电脑': ['电脑', '笔记本', '游戏', '处理器', 'CPU'],
            '鞋服': ['鞋', '跑步', '篮球', '运动', '潮流'],
            '家电': ['空调', '洗衣机', '变频', '智能', '节能']
        }
        
        for category, texts in category_texts.items():
            keywords = category_keywords[category]
            found_in_category = 0
            for text in texts:
                for keyword in keywords:
                    if keyword in text:
                        found_in_category += 1
                        break
            
            category_accuracy = found_in_category / len(texts)
            assert category_accuracy >= 0.5, f"{category}类别关键词识别率应该≥50%，实际为{category_accuracy:.2%}"
    
    def test_preprocessor_text_segmentation(self):
        """测试数据预处理器的中文分词"""
        # 测试数据
        test_df = pd.DataFrame({
            'item_id': [1, 2, 3],
            'title': [
                "华为Mate50 Pro 智能手机",
                "苹果MacBook Pro 笔记本电脑", 
                "耐克Air Jordan 篮球鞋"
            ],
            'description': [
                "这是一款高端智能手机产品",
                "专业级笔记本电脑设备",
                "经典复古篮球运动鞋"
            ]
        })
        
        # 执行文本特征处理
        result_df = self.preprocessor.process_text_features(test_df, ['title', 'description'])
        
        # 验证分词列被创建
        assert 'title_segmented' in result_df.columns, "应该创建title_segmented列"
        assert 'description_segmented' in result_df.columns, "应该创建description_segmented列"
        
        # 验证分词结果包含空格分隔的词汇
        for idx, row in result_df.iterrows():
            assert ' ' in row['title_segmented'], f"第{idx}行标题分词结果应该包含空格"
            assert ' ' in row['description_segmented'], f"第{idx}行描述分词结果应该包含空格"
        
        # 验证清理后的文本列
        assert 'title_cleaned' in result_df.columns, "应该创建title_cleaned列"
        assert 'description_cleaned' in result_df.columns, "应该创建description_cleaned列"
    
    def test_segmentation_edge_cases(self):
        """测试分词的边界情况"""
        # 测试空文本
        empty_result = self.preprocessor._segment_chinese_text("")
        assert empty_result == "", "空文本分词应该返回空字符串"
        
        # 测试None值
        none_result = self.preprocessor._segment_chinese_text(None)
        assert none_result == "", "None值分词应该返回空字符串"
        
        # 测试只有英文的文本
        english_text = "iPhone 14 Pro Max"
        english_result = self.preprocessor._segment_chinese_text(english_text)
        assert len(english_result.split()) >= 3, "英文文本也应该被正确分词"
        
        # 测试中英文混合文本
        mixed_text = "华为Mate50 Pro智能手机"
        mixed_result = self.preprocessor._segment_chinese_text(mixed_text)
        assert '华为' in mixed_result, "中英文混合文本应该正确识别中文部分"
        assert 'Mate50' in mixed_result, "中英文混合文本应该保留英文部分"
    
    def test_text_cleaning(self):
        """测试文本清理功能"""
        # 测试包含特殊字符的文本
        dirty_text = "华为Mate50!@#$%^&*()Pro智能手机【官方正品】"
        cleaned_result = self.preprocessor._clean_text(dirty_text)
        
        # 验证特殊字符被移除
        special_chars = "!@#$%^&*()【】"
        for char in special_chars:
            assert char not in cleaned_result, f"特殊字符'{char}'应该被移除"
        
        # 验证中文、英文、数字被保留
        assert '华为' in cleaned_result, "中文应该被保留"
        assert 'Mate50' in cleaned_result, "英文和数字应该被保留"
        assert 'Pro' in cleaned_result, "英文应该被保留"