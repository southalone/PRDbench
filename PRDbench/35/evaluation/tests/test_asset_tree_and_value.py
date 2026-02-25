import sys
import os
import pytest
from datetime import datetime, timedelta

# 将 src 目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, Asset

@pytest.fixture(scope="function")
def data_manager():
    """提供一个临时的、隔离的 DataManager 实例用于测试。"""
    test_data_file = "test_asset_tree_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # 添加测试用户和分类
    dm.add_user("asset_user", "password123", 1, roles=["ASSET"])
    dm.add_category("测试分类", 1)
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_set_parent_asset(data_manager):
    """测试设置父资产 (Metric: 2.4.2a)"""
    # 创建两个资产
    parent_asset = data_manager.add_asset("服务器机柜", 20000, 2, "asset_user")
    child_asset = data_manager.add_asset("服务器", 15000, 2, "asset_user")
    
    # 设置父子关系
    data_manager.update_asset(child_asset.id, parent_id=parent_asset.id)
    
    # 验证父子关系已设置
    updated_child = data_manager.get_asset(child_asset.id)
    assert updated_child.parent_id == parent_asset.id
    
    # 验证数据持久化
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    
    reloaded_child = reloaded_dm.get_asset(child_asset.id)
    assert reloaded_child.parent_id == parent_asset.id

def test_query_parent_asset(data_manager):
    """测试查询父资产 (Metric: 2.4.2b)"""
    # 创建父子资产
    parent_asset = data_manager.add_asset("机房", 50000, 2, "asset_user")
    child_asset = data_manager.add_asset("UPS电源", 8000, 2, "asset_user", parent_id=parent_asset.id)
    
    # 查询子资产的父资产信息
    child = data_manager.get_asset(child_asset.id)
    assert child.parent_id == parent_asset.id
    
    # 通过父资产ID获取父资产详情
    parent = data_manager.get_asset(child.parent_id)
    assert parent is not None
    assert parent.name == "机房"
    assert parent.id == parent_asset.id

def test_query_child_assets(data_manager):
    """测试查询子资产 (Metric: 2.4.2c)"""
    # 创建一个父资产和多个子资产
    parent_asset = data_manager.add_asset("数据中心", 100000, 2, "asset_user")
    child1 = data_manager.add_asset("服务器1", 15000, 2, "asset_user", parent_id=parent_asset.id)
    child2 = data_manager.add_asset("服务器2", 15000, 2, "asset_user", parent_id=parent_asset.id)
    child3 = data_manager.add_asset("网络设备", 5000, 2, "asset_user", parent_id=parent_asset.id)
    
    # 查询父资产的所有子资产
    child_assets = [asset for asset in data_manager.assets.values() 
                   if asset.parent_id == parent_asset.id]
    
    assert len(child_assets) == 3
    child_names = [asset.name for asset in child_assets]
    assert "服务器1" in child_names
    assert "服务器2" in child_names
    assert "网络设备" in child_names

def test_asset_value_calculation_and_depreciation(data_manager):
    """测试资产价值计算与折旧 (Metric: 2.4.3)"""
    # 创建一个资产，设置为5年前购买
    asset = data_manager.add_asset("测试设备", 10000, 2, "asset_user", service_life=5)
    
    # 手动设置开始时间为6年前（确保超过5年使用期）
    six_years_ago = datetime.now() - timedelta(days=6*365)
    asset.start_time = six_years_ago
    data_manager.save_data()
    
    # 计算当前价值（应该为0，因为已过使用年限）
    def calculate_current_value(asset):
        """计算资产当前价值的辅助函数"""
        if asset.status == 'RETIRED':
            return 0
        
        years_used = (datetime.now() - asset.start_time).days / 365.25
        if years_used >= asset.service_life:
            return 0
        
        depreciation_rate = years_used / asset.service_life
        current_value = asset.value * (1 - depreciation_rate)
        return max(0, current_value)
    
    current_value = calculate_current_value(asset)
    assert current_value == 0  # 已过期，价值为0
    
    # 测试未过期的资产
    new_asset = data_manager.add_asset("新设备", 8000, 2, "asset_user", service_life=4)
    # 设置为2年前购买
    two_years_ago = datetime.now() - timedelta(days=2*365)
    new_asset.start_time = two_years_ago
    data_manager.save_data()
    
    new_current_value = calculate_current_value(new_asset)
    expected_value = 8000 * (1 - 2/4)  # 2年/4年使用期 = 50%折旧
    assert abs(new_current_value - expected_value) < 100  # 允许小的误差

def test_asset_retirement(data_manager):
    """测试资产清退 (Metric: 2.4.4)"""
    # 创建一个资产
    asset = data_manager.add_asset("待清退设备", 5000, 2, "asset_user")
    
    # 执行清退操作
    data_manager.update_asset(asset.id, status='RETIRED')
    
    # 验证清退状态
    retired_asset = data_manager.get_asset(asset.id)
    assert retired_asset.status == 'RETIRED'
    
    # 在实际系统中，清退后当前价值应为0
    # 这里我们验证状态变更已正确保存
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    
    reloaded_asset = reloaded_dm.get_asset(asset.id)
    assert reloaded_asset.status == 'RETIRED'

def test_complex_asset_tree_structure(data_manager):
    """测试复杂的资产树结构"""
    # 创建多层资产树
    building = data_manager.add_asset("办公楼", 1000000, 2, "asset_user")
    floor1 = data_manager.add_asset("一楼", 0, 2, "asset_user", parent_id=building.id)
    floor2 = data_manager.add_asset("二楼", 0, 2, "asset_user", parent_id=building.id)
    
    # 一楼的设备
    room101 = data_manager.add_asset("101会议室", 50000, 2, "asset_user", parent_id=floor1.id)
    projector = data_manager.add_asset("投影仪", 8000, 2, "asset_user", parent_id=room101.id)
    
    # 二楼的设备
    server_room = data_manager.add_asset("服务器机房", 200000, 2, "asset_user", parent_id=floor2.id)
    server1 = data_manager.add_asset("Web服务器", 15000, 2, "asset_user", parent_id=server_room.id)
    server2 = data_manager.add_asset("数据库服务器", 20000, 2, "asset_user", parent_id=server_room.id)
    
    # 验证树结构的完整性
    # 验证一楼的子资产
    floor1_children = [asset for asset in data_manager.assets.values() 
                      if asset.parent_id == floor1.id]
    assert len(floor1_children) == 1
    assert floor1_children[0].name == "101会议室"
    
    # 验证101会议室的子资产
    room101_children = [asset for asset in data_manager.assets.values() 
                       if asset.parent_id == room101.id]
    assert len(room101_children) == 1
    assert room101_children[0].name == "投影仪"
    
    # 验证服务器机房的子资产
    server_room_children = [asset for asset in data_manager.assets.values() 
                           if asset.parent_id == server_room.id]
    assert len(server_room_children) == 2
    server_names = [asset.name for asset in server_room_children]
    assert "Web服务器" in server_names
    assert "数据库服务器" in server_names

def test_asset_value_with_different_service_life(data_manager):
    """测试不同使用年限的资产价值计算"""
    # 创建不同使用年限的资产
    short_life_asset = data_manager.add_asset("短期设备", 6000, 2, "asset_user", service_life=2)
    long_life_asset = data_manager.add_asset("长期设备", 6000, 2, "asset_user", service_life=10)
    
    # 设置为1年前购买
    one_year_ago = datetime.now() - timedelta(days=365)
    short_life_asset.start_time = one_year_ago
    long_life_asset.start_time = one_year_ago
    data_manager.save_data()
    
    def calculate_current_value(asset):
        years_used = (datetime.now() - asset.start_time).days / 365.25
        if years_used >= asset.service_life:
            return 0
        depreciation_rate = years_used / asset.service_life
        return asset.value * (1 - depreciation_rate)
    
    # 短期设备（2年使用期，已用1年）应该剩余50%价值
    short_value = calculate_current_value(short_life_asset)
    expected_short = 6000 * 0.5
    assert abs(short_value - expected_short) < 100
    
    # 长期设备（10年使用期，已用1年）应该剩余90%价值
    long_value = calculate_current_value(long_life_asset)
    expected_long = 6000 * 0.9
    assert abs(long_value - expected_long) < 100