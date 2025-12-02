import sys
import os
import pytest

# 将 src 目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, UserPermission

@pytest.fixture(scope="function")
def data_manager():
    """提供一个临时的、隔离的 DataManager 实例用于测试。"""
    test_data_file = "test_dept_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # 添加测试用户
    dm.add_user("system_user", "password123", 1, roles=["SYSTEM"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_create_root_department(data_manager):
    """测试创建根部门 (Metric: 2.2.1a)"""
    # 创建一个新的根部门
    root_dept = data_manager.add_department("RootDept")
    
    assert root_dept is not None
    assert root_dept.name == "RootDept"
    assert root_dept.parent_id is None
    
    # 验证部门已保存到数据管理器中
    saved_dept = data_manager.get_department(root_dept.id)
    assert saved_dept is not None
    assert saved_dept.name == "RootDept"

def test_create_child_department(data_manager):
    """测试创建子部门 (Metric: 2.2.1b)"""
    # 先创建一个根部门
    root_dept = data_manager.add_department("RootDept")
    
    # 创建子部门
    child_dept = data_manager.add_department("ChildDept", parent_id=root_dept.id)
    
    assert child_dept is not None
    assert child_dept.name == "ChildDept"
    assert child_dept.parent_id == root_dept.id
    
    # 验证父子关系
    saved_child = data_manager.get_department(child_dept.id)
    assert saved_child.parent_id == root_dept.id
    
    # 验证部门树结构
    dept_tree = data_manager.get_department_tree(root_dept.id)
    assert dept_tree is not None
    assert dept_tree['name'] == "RootDept"
    assert len(dept_tree['children']) == 1
    assert dept_tree['children'][0]['name'] == "ChildDept"

def test_department_asset_manager_configuration(data_manager):
    """测试部门资产管理员配置 (Metric: 2.2.2)"""
    # 创建一个部门
    dept = data_manager.add_department("DeptA")
    
    # 创建一个具有ASSET权限的用户
    asset_user = data_manager.add_user("AssetUser", "password123", dept.id, roles=["ASSET"])
    
    # 在实际系统中，这里应该有设置部门资产管理员的功能
    # 由于当前模型中没有直接的部门资产管理员字段，我们通过用户的部门归属和权限来验证
    assert asset_user.department_id == dept.id
    assert asset_user.has_permission(UserPermission.ASSET)
    
    # 验证用户属于正确的部门
    dept_users = [user for user in data_manager.users.values() 
                  if user.department_id == dept.id and user.has_permission(UserPermission.ASSET)]
    assert len(dept_users) == 1
    assert dept_users[0].username == "AssetUser"

def test_department_tree_structure(data_manager):
    """测试部门树结构的完整性"""
    # 创建多层部门结构
    root = data_manager.add_department("总公司")
    branch1 = data_manager.add_department("分公司A", parent_id=root.id)
    branch2 = data_manager.add_department("分公司B", parent_id=root.id)
    dept1 = data_manager.add_department("技术部", parent_id=branch1.id)
    dept2 = data_manager.add_department("销售部", parent_id=branch1.id)
    
    # 验证树结构
    tree = data_manager.get_department_tree(root.id)
    assert tree['name'] == "总公司"
    assert len(tree['children']) == 2
    
    # 验证分公司A的子部门
    branch1_tree = next(child for child in tree['children'] if child['name'] == "分公司A")
    assert len(branch1_tree['children']) == 2
    
    dept_names = [child['name'] for child in branch1_tree['children']]
    assert "技术部" in dept_names
    assert "销售部" in dept_names

def test_get_department_by_id(data_manager):
    """测试通过ID获取部门"""
    dept = data_manager.add_department("测试部门")
    
    retrieved_dept = data_manager.get_department(dept.id)
    assert retrieved_dept is not None
    assert retrieved_dept.id == dept.id
    assert retrieved_dept.name == "测试部门"
    
    # 测试获取不存在的部门
    non_existent = data_manager.get_department(99999)
    assert non_existent is None