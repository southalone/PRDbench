import sys
import os
import pytest

# 将 src 目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager

@pytest.fixture(scope="function")
def data_manager_for_permission():
    """为权限测试提供一个特定的 DataManager 实例。"""
    test_data_file = "test_permission_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data() # 这会创建'公司'根部门 (ID=1)
    
    # 创建两个新部门
    dept_a = dm.add_department("部门A", 1)
    dept_b = dm.add_department("部门B", 1)
    
    # 创建两个用户，分别属于不同部门
    dm.add_user("user_a", "pass_a", dept_a.id, roles=["STAFF"])
    dm.add_user("user_b", "pass_b", dept_b.id, roles=["STAFF"])
    
    # 创建两个资产，分别属于不同部门的用户
    dm.add_asset("资产A", 100, 2, "user_a") # 假设分类ID为2
    dm.add_asset("资产B", 200, 2, "user_b")
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_department_data_isolation(data_manager_for_permission):
    """
    测试部门数据隔离 (Metric: 2.7.1)
    - 验证一个部门的用户只能看到自己名下的资产。
    """
    dm = data_manager_for_permission
    
    # 获取属于 UserA 的资产
    assets_for_user_a = dm.get_assets_by_owner("user_a")
    assert len(assets_for_user_a) == 1
    assert assets_for_user_a[0].name == "资产A"
    
    # 获取属于 UserB 的资产
    assets_for_user_b = dm.get_assets_by_owner("user_b")
    assert len(assets_for_user_b) == 1
    assert assets_for_user_b[0].name == "资产B"
    
    # 验证 UserA 看不到 UserB 的资产
    for asset in assets_for_user_a:
        assert asset.owner_username != "user_b"
        
    # 验证 UserB 看不到 UserA 的资产
    for asset in assets_for_user_b:
        assert asset.owner_username != "user_a"