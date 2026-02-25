"""
量表创建功能测试
"""
import pytest
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scale_manager import ScaleManager
from models import create_tables

@pytest.fixture
def scale_manager():
    """创建量表管理器实例"""
    create_tables()
    return ScaleManager()

def test_create_scale_basic_info(scale_manager):
    """测试量表基本信息创建"""
    # 准备测试数据
    scale_name = "测试量表"
    scale_description = "这是一个测试量表"
    scale_version = "1.0"
    
    # 执行创建操作
    scale = scale_manager.create_scale(
        name=scale_name,
        description=scale_description,
        version=scale_version
    )
    
    # 断言
    assert scale is not None, "量表创建失败"
    assert scale.name == scale_name, f"量表名称不匹配，期望: {scale_name}, 实际: {scale.name}"
    assert scale.description == scale_description, f"量表描述不匹配"
    assert scale.version == scale_version, f"量表版本不匹配"
    assert scale.id is not None, "量表ID应该不为空"
    
    # 验证量表可以被检索
    retrieved_scale = scale_manager.get_scale(scale.id)
    assert retrieved_scale is not None, "无法检索创建的量表"
    assert retrieved_scale.name == scale_name, "检索的量表名称不匹配"

def test_create_scale_with_items(scale_manager):
    """测试创建包含条目的量表"""
    # 准备测试数据
    scale_name = "带条目的测试量表"
    scale_description = "包含多个条目的测试量表"
    
    items = [
        {
            'item_number': 1,
            'content': '我能够长时间集中注意力',
            'dimension': '注意持续',
            'is_reverse': False
        },
        {
            'item_number': 2,
            'content': '我很容易分心',
            'dimension': '注意集中',
            'is_reverse': True
        },
        {
            'item_number': 3,
            'content': '我能够控制注意力',
            'dimension': '注意控制',
            'is_reverse': False
        }
    ]
    
    config = {
        'scoring_method': 'likert_7',
        'dimensions': ['注意持续', '注意集中', '注意控制'],
        'scoring_range': [1, 7],
        'higher_better': True
    }
    
    # 执行创建操作
    scale = scale_manager.create_scale(
        name=scale_name,
        description=scale_description,
        items=items,
        config=config
    )
    
    # 断言
    assert scale is not None, "量表创建失败"
    assert scale.name == scale_name, "量表名称不匹配"
    assert len(scale.items) == 3, f"条目数量不匹配，期望: 3, 实际: {len(scale.items)}"
    
    # 验证条目内容
    scale_items = sorted(scale.items, key=lambda x: x.item_number)
    
    for i, expected_item in enumerate(items):
        actual_item = scale_items[i]
        assert actual_item.item_number == expected_item['item_number'], f"条目{i+1}编号不匹配"
        assert actual_item.content == expected_item['content'], f"条目{i+1}内容不匹配"
        assert actual_item.dimension == expected_item['dimension'], f"条目{i+1}维度不匹配"
        assert actual_item.is_reverse == expected_item['is_reverse'], f"条目{i+1}反向计分设置不匹配"
    
    # 验证配置
    assert scale.config == config, "量表配置不匹配"

def test_scale_validation():
    """测试量表数据验证"""
    scale_manager_instance = ScaleManager()
    
    # 测试空名称
    with pytest.raises(Exception):
        scale_manager_instance.create_scale(name="", description="测试")
    
    # 测试重复名称
    scale_manager_instance.create_scale(name="重复测试量表", description="第一个")
    
    # 创建同名量表应该成功（系统允许同名量表）
    scale2 = scale_manager_instance.create_scale(name="重复测试量表", description="第二个")
    assert scale2 is not None, "同名量表创建应该成功"

def test_scale_statistics(scale_manager):
    """测试量表统计信息"""
    # 创建测试量表
    items = [
        {'item_number': 1, 'content': '测试条目1', 'dimension': '维度1', 'is_reverse': False},
        {'item_number': 2, 'content': '测试条目2', 'dimension': '维度1', 'is_reverse': True},
        {'item_number': 3, 'content': '测试条目3', 'dimension': '维度2', 'is_reverse': False}
    ]
    
    scale = scale_manager.create_scale(
        name="统计测试量表",
        description="用于测试统计功能",
        items=items
    )
    
    # 获取统计信息
    stats = scale_manager.get_scale_statistics(scale.id)
    
    # 断言
    assert stats is not None, "统计信息获取失败"
    assert stats['scale_name'] == "统计测试量表", "量表名称不匹配"
    assert stats['total_items'] == 3, f"条目数量不匹配，期望: 3, 实际: {stats['total_items']}"
    assert len(stats['dimensions']) == 2, f"维度数量不匹配，期望: 2, 实际: {len(stats['dimensions'])}"
    assert stats['reverse_items'] == 1, f"反向条目数量不匹配，期望: 1, 实际: {stats['reverse_items']}"
    assert 'created_at' in stats, "缺少创建时间信息"
    assert 'updated_at' in stats, "缺少更新时间信息"