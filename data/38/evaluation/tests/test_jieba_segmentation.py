# -*- coding: utf-8 -*-
import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from text_mining import TextMining

class TestJiebaSegmentation:
    """jieba分词处理-属性词识别测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.text_mining = TextMining()
    
    def test_jieba_segmentation_attribute_recognition(self):
        """测试jieba分词和属性词识别"""
        # 测试文本包含明显的属性词
        test_text = "这个手机性能很好，外观漂亮，价格实惠，质量不错，功能强大"
        
        # 执行分词
        words = self.text_mining.segment_text(test_text)
        
        # 断言：分词结果不为空
        assert len(words) > 0, "分词结果不应为空"
        
        # 断言：能识别出属性相关词汇
        attribute_words_found = []
        for category, keywords in self.text_mining.attribute_keywords.items():
            for keyword in keywords:
                if keyword in words or any(keyword in word for word in words):
                    attribute_words_found.append(keyword)
        
        # 断言：至少识别出3个属性词
        assert len(attribute_words_found) >= 3, f"应识别出至少3个属性词，实际识别：{attribute_words_found}"
        
        # 断言：分词使用了jieba（验证分词质量）
        assert '性能' in words, "应该正确识别'性能'属性词"
        assert '外观' in words or '漂亮' in words, "应该正确识别外观相关属性词"
        assert '价格' in words or '实惠' in words, "应该正确识别价格相关属性词"
        
        return True