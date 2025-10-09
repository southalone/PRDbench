# -*- coding: utf-8 -*-
import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from text_mining import TextMining

class TestSentimentAnalysis:
    """情感分析-属性情感对识别测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.text_mining = TextMining()
    
    def test_sentiment_analysis_attribute_emotion_pairs(self):
        """测试情感分析和属性情感对识别"""
        # 准备测试评论数据
        positive_review = "这个手机性能很好，外观漂亮，价格实惠"
        negative_review = "质量不好，做工粗糙，价格太贵"
        
        # 执行分词和情感分析
        positive_words = self.text_mining.segment_text(positive_review)
        negative_words = self.text_mining.segment_text(negative_review)
        
        positive_score = self.text_mining.calculate_sentiment_score(positive_words)
        negative_score = self.text_mining.calculate_sentiment_score(negative_words)
        
        # 断言：正面评论情感得分应该为正
        assert positive_score > 0, f"正面评论情感得分应为正数，实际得分：{positive_score}"
        
        # 断言：负面评论情感得分应该为负或接近0
        assert negative_score <= 0, f"负面评论情感得分应为负数或0，实际得分：{negative_score}"
        
        # 断言：使用词典方法而非预训练模型
        assert hasattr(self.text_mining, 'sentiment_dict'), "应该使用情感词典"
        assert len(self.text_mining.sentiment_dict) > 0, "情感词典不应为空"
        
        # 验证属性情感对识别
        # 使用现有的analyze_review方法来获取属性-情感对
        analysis_result = self.text_mining.analyze_review(positive_review)
        attribute_emotion_pairs = analysis_result.get('attribute_scores', {})
        assert len(attribute_emotion_pairs) > 0, "应该能识别出属性-情感对"
        
        return True