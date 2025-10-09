"""
个性化推荐功能测试
"""
import sys
import os
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from locallens.core.config import Config
from locallens.core.database import DatabaseManager
from locallens.search.engine import SearchEngine

@pytest.fixture(scope="module")
def search_engine():
    """初始化并返回一个SearchEngine实例"""
    config = Config()
    db_manager = DatabaseManager(config.database_path)
    engine = SearchEngine(config, db_manager)
    # 确保加载了商家数据
    engine._get_businesses()
    # 确保db_manager被设置到ranking_engine
    engine.ranking_engine.set_database_manager(db_manager)
    return engine

def test_recommendation_relevance(search_engine):
    """
    测试为登录用户生成的推荐是否合理。
    """
    # 使用一个有足够评论历史的用户进行测试
    user_id = "HFECrzYDpgbS5EmTBtj2zQ" 
    
    # 1. 获取用户的画像和分类偏好
    user_profile = search_engine.ranking_engine._get_user_profile(user_id)
    assert user_profile is not None, f"无法加载用户 '{user_id}' 的画像"
    
    category_prefs = user_profile.get('category_preferences', {})

    # 2. 获取推荐结果
    recommendations = search_engine.get_recommendations(
        user_id=user_id,
        limit=10
    )

    # 3. 断言推荐结果不为空
    assert recommendations is not None, "推荐结果不应为None"
    assert 'businesses' in recommendations, "推荐结果应包含 'businesses' 键"
    
    recommended_businesses = recommendations['businesses']
    assert len(recommended_businesses) > 0, "应至少返回一个推荐商家"

    # 4. 验证推荐结果的质量
    if category_prefs:
        # 如果用户有分类偏好，验证推荐的相关性
        preferred_categories = set(category_prefs.keys())
    
        # 至少有一部分推荐应该匹配用户偏好
        matching_count = 0
        for business in recommended_businesses:
            business_categories_str = business.get('categories', '').lower()
            business_categories = {cat.strip() for cat in business_categories_str.split(',')}
        
            # 检查商家分类与用户偏好分类是否有交集
            if not preferred_categories.isdisjoint(business_categories):
                matching_count += 1

        match_ratio = matching_count / len(recommended_businesses)
        print(f"用户 {user_id} 有 {len(category_prefs)} 个分类偏好")
        print(f"推荐匹配率: {match_ratio:.2f} ({matching_count}/{len(recommended_businesses)})")

        # 如果用户有分类偏好，至少30%的推荐应该匹配
        assert match_ratio >= 0.3, f"推荐相关性过低：{matching_count}/{len(recommended_businesses)} = {match_ratio:.2f}"
    else:
        # 如果用户没有分类偏好，验证推荐基于质量
        print(f"用户 {user_id} 没有分类偏好，验证推荐质量")

        # 验证推荐的商家质量（评分应该合理）
        total_stars = sum(b.get('stars', 0) for b in recommended_businesses)
        avg_stars = total_stars / len(recommended_businesses)
        assert avg_stars >= 2.0, f"推荐商家平均评分过低: {avg_stars:.2f}"

        print(f"推荐商家平均评分: {avg_stars:.2f}")

    # 5. 验证推荐结果有推荐得分
    for business in recommended_businesses:
        assert 'recommendation_score' in business, f"商家 '{business.get('name')}' 缺少推荐得分"
        assert business['recommendation_score'] > 0, f"商家 '{business.get('name')}' 推荐得分应大于0"
