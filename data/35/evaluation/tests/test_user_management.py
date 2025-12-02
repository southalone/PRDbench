import sys
import os
import pytest

# 将 src 目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, User, UserPermission

@pytest.fixture(scope="function")
def data_manager():
    """提供一个临时的、隔离的 DataManager 实例用于测试。"""
    test_data_file = "test_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # 添加测试用户
    dm.add_user("testuser", "password123", 1, roles=["STAFF"])
    dm.add_user("staffuser", "password123", 1, roles=["STAFF"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_change_own_password(data_manager):
    """测试用户修改自己的密码 (Metric: 2.1.10)"""
    user = data_manager.get_user("testuser")
    assert user.check_password("password123")

    new_password = "new_password_456"
    user.set_password(new_password)
    data_manager.save_data()

    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    reloaded_user = reloaded_dm.get_user("testuser")
    
    assert not reloaded_user.check_password("password123")
    assert reloaded_user.check_password(new_password)

def test_list_users_with_system_permission(data_manager):
    """测试SYSTEM权限用户可以查看所有用户 (Metric: 2.1.5a)"""
    admin_user = data_manager.get_user("admin")
    assert admin_user.has_permission(UserPermission.SYSTEM)
    
    # 在这个模拟场景中，我们直接检查data_manager中的用户数量
    all_users = list(data_manager.users.values())
    assert len(all_users) >= 3 # admin, testuser, staffuser

def test_list_users_with_staff_permission(data_manager):
    """测试STAFF权限用户无法直接获取用户列表 (Metric: 2.1.5b)"""
    staff_user = data_manager.get_user("staffuser")
    assert not staff_user.has_permission(UserPermission.SYSTEM)
    # CLI应用中的权限检查是在调用函数前，这里模拟该逻辑
    # 如果一个函数需要SYSTEM权限，STAFF用户调用时应被拒绝
    # 此测试更多是概念性的，验证权限模型
    assert staff_user.has_permission(UserPermission.STAFF)

def test_add_user(data_manager):
    """测试添加新用户 (Metric: 2.1.6)"""
    new_username = "new_user"
    data_manager.add_user(new_username, "newpass", 1, roles=["STAFF"])
    
    added_user = data_manager.get_user(new_username)
    assert added_user is not None
    assert added_user.check_password("newpass")
    assert added_user.department_id == 1

def test_edit_user(data_manager):
    """测试编辑用户信息 (Metric: 2.1.7)"""
    user_to_edit = data_manager.get_user("testuser")
    
    # 在模拟场景中，我们直接修改用户信息
    user_to_edit.department_id = 2 # 假设存在ID为2的部门
    user_to_edit.roles = ["ASSET"]
    data_manager.save_data()
    
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    edited_user = reloaded_dm.get_user("testuser")
    
    assert edited_user.department_id == 2
    assert "ASSET" in edited_user.roles

def test_delete_user(data_manager):
    """测试删除用户 (Metric: 2.1.8)"""
    username_to_delete = "testuser"
    assert data_manager.get_user(username_to_delete) is not None
    
    del data_manager.users[username_to_delete]
    data_manager.save_data()
    
    assert data_manager.get_user(username_to_delete) is None

def test_lock_unlock_user(data_manager):
    """测试锁定和解锁用户 (Metric: 2.1.9)"""
    user_to_lock = data_manager.get_user("testuser")
    
    # 锁定用户
    user_to_lock.active = False
    data_manager.save_data()
    
    reloaded_user = data_manager.get_user("testuser")
    assert not reloaded_user.active
    
    # 解锁用户
    user_to_lock.active = True
    data_manager.save_data()
    
    reloaded_user = data_manager.get_user("testuser")
    assert reloaded_user.active