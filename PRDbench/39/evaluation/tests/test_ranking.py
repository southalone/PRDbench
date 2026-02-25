"""
排序权重和多字段匹配功能测试
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
    engine.ranking_engine.set_database_manager(db_manager)
    engine._get_businesses()
    return engine

def test_exact_name_ranking(search_engine):
    """
    测试完全匹配商家名称的搜索是否能将该商家排在首位 (Issue 4.1a)
    """
    # 这个商家在数据集中存在
    search_query = "Jersey Mike's Subs"
    results = search_engine.search(query=search_query, limit=1)
    
    assert results and results['businesses'], f"搜索 '{search_query}' 时没有返回任何结果"
    
    top_result = results['businesses'][0]
    
    assert top_result.get('name') == search_query,         f"搜索 '{search_query}' 时，首个结果应为完全匹配的商家，但返回的是 '{top_result.get('name')}'"

def test_category_ranking_relevance(search_engine):
    """
    测试分类关键词搜索结果的相关性 (Issue 4.1b)
    """
    search_query = "Pizza"
    results = search_engine.search(query=search_query, limit=10)

    assert results and results['businesses'], f"搜索 '{search_query}' 时没有返回任何结果"
    
    businesses = results['businesses']
    
    match_count = 0
    for business in businesses:
        name = business.get('name', '').lower()
        categories = business.get('categories', '').lower()
        if 'pizza' in name or 'pizza' in categories:
            match_count += 1
            
    # 断言：前10个结果中至少有8个是相关的
    assert match_count >= 8,         f"搜索 '{search_query}' 时，前10个结果中应至少有8个相关，但只找到了 {match_count} 个"

def test_address_ranking_relevance(search_engine):
    """
    测试地址关键词搜索结果的相关性 (Issue 4.1c)
    """
    # 这个地址在数据集中存在
    search_query = "McMullen Booth Rd"
    results = search_engine.search(query=search_query, limit=5)

    assert results and results['businesses'], f"搜索 '{search_query}' 时没有返回任何结果"
    
    businesses = results['businesses']
    
    for business in businesses:
        address = business.get('address', '')
        assert search_query.lower() in address.lower(),             f"搜索 '{search_query}' 时，返回的结果 '{business.get('name')}' 的地址 '{address}' 不包含该关键词"
