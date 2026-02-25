import sys
import os
import pytest

# 将 src 目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, UserPermission

@pytest.fixture(scope="function")
def data_manager():
    """提供一个临时的、隔离的 DataManager 实例用于测试。"""
    test_data_file = "test_category_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # 添加测试用户
    dm.add_user("asset_user", "password123", 1, roles=["ASSET"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_create_root_asset_category(data_manager):
    """测试创建根资产分类 (Metric: 2.3.1a)"""
    # 创建一个新的根资产分类
    root_category = data_manager.add_category("RootCategory")
    
    assert root_category is not None
    assert root_category.name == "RootCategory"
    assert root_category.parent_id is None
    
    # 验证分类已保存到数据管理器中
    saved_category = data_manager.get_category(root_category.id)
    assert saved_category is not None
    assert saved_category.name == "RootCategory"

def test_create_child_asset_category(data_manager):
    """测试创建子资产分类 (Metric: 2.3.1b)"""
    # 先创建一个根分类
    root_category = data_manager.add_category("RootCategory")
    
    # 创建子分类
    child_category = data_manager.add_category("ChildCategory", parent_id=root_category.id)
    
    assert child_category is not None
    assert child_category.name == "ChildCategory"
    assert child_category.parent_id == root_category.id
    
    # 验证父子关系
    saved_child = data_manager.get_category(child_category.id)
    assert saved_child.parent_id == root_category.id
    
    # 验证分类树结构
    category_tree = data_manager.get_category_tree(root_category.id)
    assert category_tree is not None
    assert category_tree['name'] == "RootCategory"
    assert len(category_tree['children']) == 1
    assert category_tree['children'][0]['name'] == "ChildCategory"

def test_create_custom_attribute(data_manager):
    """测试创建自定义属性 (Metric: 2.3.2a)"""
    # 添加自定义属性
    data_manager.custom_attrs.add("Brand")
    data_manager.save_data()
    
    # 验证属性已添加
    assert "Brand" in data_manager.custom_attrs
    
    # 重新加载数据验证持久化
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    
    assert "Brand" in reloaded_dm.custom_attrs

def test_add_custom_attribute_to_asset(data_manager):
    """测试为资产添加自定义属性值 (Metric: 2.3.2b)"""
    # 先创建一个资产分类和资产
    category = data_manager.add_category("电脑设备")
    asset = data_manager.add_asset("测试电脑", 5000, category.id, "asset_user")
    
    # 添加自定义属性
    data_manager.custom_attrs.add("Brand")
    
    # 为资产设置自定义属性值
    asset.custom_attrs["Brand"] = "Dell"
    data_manager.save_data()
    
    # 验证属性值已设置
    saved_asset = data_manager.get_asset(asset.id)
    assert "Brand" in saved_asset.custom_attrs
    assert saved_asset.custom_attrs["Brand"] == "Dell"
    
    # 重新加载数据验证持久化
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    
    reloaded_asset = reloaded_dm.get_asset(asset.id)
    assert "Brand" in reloaded_asset.custom_attrs
    assert reloaded_asset.custom_attrs["Brand"] == "Dell"

def test_asset_category_tree_structure(data_manager):
    """测试资产分类树结构的完整性"""
    # 创建多层分类结构
    root = data_manager.add_category("设备")
    it_equipment = data_manager.add_category("IT设备", parent_id=root.id)
    office_equipment = data_manager.add_category("办公设备", parent_id=root.id)
    computers = data_manager.add_category("计算机", parent_id=it_equipment.id)
    servers = data_manager.add_category("服务器", parent_id=it_equipment.id)
    
    # 验证树结构
    tree = data_manager.get_category_tree(root.id)
    assert tree['name'] == "设备"
    assert len(tree['children']) == 2
    
    # 验证IT设备的子分类
    it_tree = next(child for child in tree['children'] if child['name'] == "IT设备")
    assert len(it_tree['children']) == 2
    
    category_names = [child['name'] for child in it_tree['children']]
    assert "计算机" in category_names
    assert "服务器" in category_names

def test_get_assets_by_category(data_manager):
    """测试根据分类获取资产"""
    # 创建分类和资产
    category = data_manager.add_category("笔记本电脑")
    asset1 = data_manager.add_asset("ThinkPad", 8000, category.id, "asset_user")
    asset2 = data_manager.add_asset("MacBook", 12000, category.id, "asset_user")
    
    # 创建另一个分类的资产
    other_category = data_manager.add_category("打印机")
    asset3 = data_manager.add_asset("HP打印机", 2000, other_category.id, "asset_user")
    
    # 获取笔记本电脑分类的资产
    laptop_assets = data_manager.get_assets_by_category(category.id)
    assert len(laptop_assets) == 2
    
    asset_names = [asset.name for asset in laptop_assets]
    assert "ThinkPad" in asset_names
    assert "MacBook" in asset_names
    assert "HP打印机" not in asset_names

def test_multiple_custom_attributes(data_manager):
    """测试多个自定义属性"""
    # 添加多个自定义属性
    attributes = ["Brand", "Model", "SerialNumber", "PurchaseDate"]
    for attr in attributes:
        data_manager.custom_attrs.add(attr)
    
    # 创建资产并设置多个属性
    category = data_manager.add_category("服务器")
    asset = data_manager.add_asset("Web服务器", 15000, category.id, "asset_user")
    
    asset.custom_attrs.update({
        "Brand": "Dell",
        "Model": "PowerEdge R740",
        "SerialNumber": "ABC123456",
        "PurchaseDate": "2024-01-15"
    })
    data_manager.save_data()
    
    # 验证所有属性都已正确设置
    saved_asset = data_manager.get_asset(asset.id)
    assert saved_asset.custom_attrs["Brand"] == "Dell"
    assert saved_asset.custom_attrs["Model"] == "PowerEdge R740"
    assert saved_asset.custom_attrs["SerialNumber"] == "ABC123456"
    assert saved_asset.custom_attrs["PurchaseDate"] == "2024-01-15"