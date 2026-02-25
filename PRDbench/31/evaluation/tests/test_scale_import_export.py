"""
量表导入导出功能测试
"""
import pytest
import sys
import json
import pandas as pd
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

@pytest.fixture
def test_scale_json_file():
    """创建测试用的JSON量表文件"""
    test_data = {
        "name": "JSON测试量表",
        "description": "从JSON导入的测试量表",
        "version": "1.0",
        "config": {
            "scoring_method": "likert_7",
            "dimensions": ["维度1", "维度2"],
            "scoring_range": [1, 7],
            "higher_better": True
        },
        "items": [
            {
                "item_number": 1,
                "content": "测试条目1",
                "dimension": "维度1",
                "is_reverse": False
            },
            {
                "item_number": 2,
                "content": "测试条目2",
                "dimension": "维度2",
                "is_reverse": True
            }
        ]
    }
    
    test_file = Path("evaluation/temp_test_scale.json")
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    yield test_file
    
    # 清理
    if test_file.exists():
        test_file.unlink()

@pytest.fixture
def test_scale_csv_file():
    """创建测试用的CSV量表文件"""
    test_data = {
        'item_number': [1, 2, 3],
        'content': ['CSV测试条目1', 'CSV测试条目2', 'CSV测试条目3'],
        'dimension': ['维度A', '维度B', '维度A'],
        'is_reverse': [False, True, False]
    }
    
    test_file = Path("evaluation/temp_test_scale.csv")
    df = pd.DataFrame(test_data)
    df.to_csv(test_file, index=False, encoding='utf-8')
    
    yield test_file
    
    # 清理
    if test_file.exists():
        test_file.unlink()

def test_import_scale_json(scale_manager, test_scale_json_file):
    """测试从JSON文件导入量表"""
    # 执行导入
    scale = scale_manager.import_scale_from_json(test_scale_json_file)
    
    # 断言
    assert scale is not None, "JSON量表导入失败"
    assert scale.name == "JSON测试量表", f"量表名称不匹配，期望: JSON测试量表, 实际: {scale.name}"
    assert scale.description == "从JSON导入的测试量表", "量表描述不匹配"
    assert len(scale.items) == 2, f"条目数量不匹配，期望: 2, 实际: {len(scale.items)}"
    
    # 验证条目内容
    items = sorted(scale.items, key=lambda x: x.item_number)
    assert items[0].content == "测试条目1", "第一个条目内容不匹配"
    assert items[0].dimension == "维度1", "第一个条目维度不匹配"
    assert items[0].is_reverse == False, "第一个条目反向计分设置不匹配"
    
    assert items[1].content == "测试条目2", "第二个条目内容不匹配"
    assert items[1].dimension == "维度2", "第二个条目维度不匹配"
    assert items[1].is_reverse == True, "第二个条目反向计分设置不匹配"
    
    # 验证配置
    expected_config = {
        "scoring_method": "likert_7",
        "dimensions": ["维度1", "维度2"],
        "scoring_range": [1, 7],
        "higher_better": True
    }
    assert scale.config == expected_config, "量表配置不匹配"

def test_import_scale_csv(scale_manager, test_scale_csv_file):
    """测试从CSV文件导入量表"""
    # 执行导入
    scale = scale_manager.import_scale_from_csv(test_scale_csv_file)
    
    # 断言
    assert scale is not None, "CSV量表导入失败"
    assert len(scale.items) == 3, f"条目数量不匹配，期望: 3, 实际: {len(scale.items)}"
    
    # 验证条目内容
    items = sorted(scale.items, key=lambda x: x.item_number)
    assert items[0].content == "CSV测试条目1", "第一个条目内容不匹配"
    assert items[1].content == "CSV测试条目2", "第二个条目内容不匹配"
    assert items[2].content == "CSV测试条目3", "第三个条目内容不匹配"
    
    # 验证维度
    assert items[0].dimension == "维度A", "第一个条目维度不匹配"
    assert items[1].dimension == "维度B", "第二个条目维度不匹配"
    assert items[2].dimension == "维度A", "第三个条目维度不匹配"
    
    # 验证反向计分
    assert items[0].is_reverse == False, "第一个条目反向计分设置不匹配"
    assert items[1].is_reverse == True, "第二个条目反向计分设置不匹配"
    assert items[2].is_reverse == False, "第三个条目反向计分设置不匹配"

def test_export_scale_csv(scale_manager):
    """测试导出量表为CSV格式"""
    # 创建测试量表
    items = [
        {'item_number': 1, 'content': '导出测试条目1', 'dimension': '维度X', 'is_reverse': False},
        {'item_number': 2, 'content': '导出测试条目2', 'dimension': '维度Y', 'is_reverse': True}
    ]
    
    scale = scale_manager.create_scale(
        name="导出测试量表",
        description="用于测试导出功能",
        items=items
    )
    
    # 执行导出
    output_path = Path("evaluation/temp_exported_scale.csv")
    success = scale_manager.export_scale_to_csv(scale.id, output_path)
    
    try:
        # 断言
        assert success == True, "CSV导出失败"
        assert output_path.exists(), "导出的CSV文件不存在"
        
        # 验证导出内容
        df = pd.read_csv(output_path)
        assert len(df) == 2, f"导出的条目数量不匹配，期望: 2, 实际: {len(df)}"
        assert 'item_number' in df.columns, "缺少item_number列"
        assert 'content' in df.columns, "缺少content列"
        assert 'dimension' in df.columns, "缺少dimension列"
        assert 'is_reverse' in df.columns, "缺少is_reverse列"
        
        # 验证具体内容
        assert df.iloc[0]['content'] == '导出测试条目1', "第一个条目内容不匹配"
        assert df.iloc[1]['content'] == '导出测试条目2', "第二个条目内容不匹配"
        
    finally:
        # 清理
        if output_path.exists():
            output_path.unlink()

def test_export_scale_json(scale_manager):
    """测试导出量表为JSON格式"""
    # 创建测试量表
    items = [
        {'item_number': 1, 'content': 'JSON导出测试条目1', 'dimension': '维度A', 'is_reverse': False},
        {'item_number': 2, 'content': 'JSON导出测试条目2', 'dimension': '维度B', 'is_reverse': True}
    ]
    
    config = {
        'scoring_method': 'likert_5',
        'dimensions': ['维度A', '维度B']
    }
    
    scale = scale_manager.create_scale(
        name="JSON导出测试量表",
        description="用于测试JSON导出功能",
        items=items,
        config=config
    )
    
    # 执行导出
    output_path = Path("evaluation/temp_exported_scale.json")
    success = scale_manager.export_scale_to_json(scale.id, output_path)
    
    try:
        # 断言
        assert success == True, "JSON导出失败"
        assert output_path.exists(), "导出的JSON文件不存在"
        
        # 验证导出内容
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['name'] == "JSON导出测试量表", "导出的量表名称不匹配"
        assert data['description'] == "用于测试JSON导出功能", "导出的量表描述不匹配"
        assert len(data['items']) == 2, f"导出的条目数量不匹配，期望: 2, 实际: {len(data['items'])}"
        assert data['config'] == config, "导出的配置不匹配"
        
        # 验证条目内容
        items_data = sorted(data['items'], key=lambda x: x['item_number'])
        assert items_data[0]['content'] == 'JSON导出测试条目1', "第一个条目内容不匹配"
        assert items_data[1]['content'] == 'JSON导出测试条目2', "第二个条目内容不匹配"
        
    finally:
        # 清理
        if output_path.exists():
            output_path.unlink()

def test_scale_list_and_retrieval(scale_manager):
    """测试量表列表和检索功能"""
    # 创建多个测试量表
    scale1 = scale_manager.create_scale(name="列表测试量表1", description="第一个测试量表")
    scale2 = scale_manager.create_scale(name="列表测试量表2", description="第二个测试量表")
    
    # 测试列表功能
    scales = scale_manager.list_scales()
    assert len(scales) >= 2, f"量表数量不足，期望至少2个，实际: {len(scales)}"
    
    # 测试按名称检索
    retrieved_scale1 = scale_manager.get_scale_by_name("列表测试量表1")
    assert retrieved_scale1 is not None, "按名称检索量表失败"
    assert retrieved_scale1.id == scale1.id, "检索到的量表ID不匹配"
    
    # 测试按ID检索
    retrieved_scale2 = scale_manager.get_scale(scale2.id)
    assert retrieved_scale2 is not None, "按ID检索量表失败"
    assert retrieved_scale2.name == "列表测试量表2", "检索到的量表名称不匹配"