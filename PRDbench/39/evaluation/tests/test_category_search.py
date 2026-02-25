"""
分类搜索功能测试
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
    return engine

def test_category_search_strictness(search_engine):
    """
    测试按子分类搜索时，结果是否严格匹配。
    """
    # 执行分类搜索
    results = search_engine.search_by_category(
        category="Restaurants",
        subcategory="Chinese",
        limit=20
    )

    # 断言结果不为空
    assert results is not None, "搜索结果不应为None"
    assert 'businesses' in results, "搜索结果应包含 'businesses' 键"
    
    businesses = results['businesses']
    
    # 断言返回了商家
    assert len(businesses) > 0, "应至少返回一个商家"

    # 改进后的断言：检查每个返回的商家是否都包含“Chinese”分类
    for business in businesses:
        categories = business.get('categories', '')
        assert 'chinese' in categories.lower(),             f"商家 '{business.get('name')}' (ID: {business.get('business_id')}) 的分类 '{categories}' 中不包含 'chinese'"
