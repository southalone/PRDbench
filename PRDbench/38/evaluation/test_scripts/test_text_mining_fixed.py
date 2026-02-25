#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from text_mining import TextMining

def test_text_mining_functions():
    """测试文本挖掘功能"""
    try:
        text_mining = TextMining(os.path.join(src_dir, "config/sentiment_dict.txt"))
        
        # 测试jieba分词和属性词识别
        test_text = "这个手机性能很好，外观漂亮，价格实惠，质量不错"
        words = text_mining.segment_text(test_text)
        
        if len(words) > 0:
            print("SUCCESS: jieba分词处理成功")
            print(f"分词结果: {words}")
        
        # 测试情感分析
        sentiment_score = text_mining.calculate_sentiment_score(words)
        print(f"SUCCESS: 情感分析完成，情感得分: {sentiment_score}")
        
        # 测试属性提取（替换原来的属性情感对识别）
        attribute_scores = text_mining.extract_attributes(words)
        if len(attribute_scores) > 0:
            print(f"SUCCESS: 属性提取成功: {attribute_scores}")
        
        # 测试评论分析（完整的属性-情感分析）
        review_result = text_mining.analyze_review(test_text)
        if review_result['attribute_scores']:
            print(f"SUCCESS: 评论分析成功，属性得分: {review_result['attribute_scores']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: 文本挖掘测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_text_mining_functions()
    sys.exit(0 if success else 1)