import sys
import os
import pytest

# 将 src 目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager

@pytest.fixture(scope="function")
def data_manager():
    """提供一个临时的、隔离的 DataManager 实例用于测试。"""
    test_data_file = "test_asset_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # 添加一个默认分类和用户
    dm.add_category("默认分类", 1)
    dm.add_user("asset_admin", "password", 1, roles=["ASSET"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_add_asset(data_manager):
    """测试添加资产 (Metric: 2.4.1a)"""
    asset = data_manager.add_asset("测试电脑", 5000, 2, "asset_admin")
    assert asset is not None
    assert data_manager.get_asset(asset.id) is not None
    assert data_manager.get_asset(asset.id).name == "测试电脑"

def test_query_asset(data_manager):
    """测试查询资产 (Metric: 2.4.1b)"""
    asset = data_manager.add_asset("笔记本", 6000, 2, "asset_admin")
    
    found_asset = data_manager.get_asset(asset.id)
    assert found_asset is not None
    assert found_asset.name == "笔记本"

def test_edit_asset(data_manager):
    """测试编辑资产 (Metric: 2.4.1c)"""
    asset = data_manager.add_asset("旧显示器", 1000, 2, "asset_admin")
    
    data_manager.update_asset(asset.id, name="新显示器", value=1200)
    
    edited_asset = data_manager.get_asset(asset.id)
    assert edited_asset.name == "新显示器"
    assert edited_asset.value == 1200

def test_delete_asset(data_manager):
    """测试删除资产 (Metric: 2.4.1d)"""
    asset = data_manager.add_asset("待删除打印机", 1500, 2, "asset_admin")
    asset_id = asset.id
    
    assert data_manager.get_asset(asset_id) is not None
    
    data_manager.delete_asset(asset_id)
    assert data_manager.get_asset(asset_id) is None

def test_retire_asset(data_manager):
    """测试清退资产 (Metric: 2.4.4)"""
    asset = data_manager.add_asset("服务器", 20000, 2, "asset_admin")
    
    # 在CLI中，这将是一个单独的函数，这里我们直接调用update_asset来模拟
    data_manager.update_asset(asset.id, status='RETIRED')
    
    retired_asset = data_manager.get_asset(asset.id)
    assert retired_asset.status == 'RETIRED'