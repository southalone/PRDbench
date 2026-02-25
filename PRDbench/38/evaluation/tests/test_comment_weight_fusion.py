# -*- coding: utf-8 -*-
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from text_mining import TextMining

def test_comment_weight_fusion():
    """测试评论权重融合和偏好向量更新"""
    text_mining = TextMining()
    
    # 测试评论数据
    user_comments = ["性能很好，外观漂亮", "价格实惠，质量不错"]
    
    # 执行权重融合
    # 模拟评论数据框
    import pandas as pd
    reviews_df = pd.DataFrame({
        'user_id': [1, 1],
        'review_text': user_comments,
        'product_id': [1, 2]
    })
    
    # 执行权重融合
    preference_update = text_mining.build_user_preference_from_reviews(1, reviews_df)
    
    # 断言：权重更新合理
    assert preference_update is not None, "应该能更新用户偏好"
