import sys
import os
import pytest
from datetime import datetime

# 将 src 目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager

# 简单的日志记录类，用于测试
class ChangeLog:
    """变更日志类"""
    def __init__(self, log_id, entity_type, entity_id, operation, user, timestamp, details=None):
        self.id = log_id
        self.entity_type = entity_type  # 'asset', 'user', 'department', etc.
        self.entity_id = entity_id
        self.operation = operation  # 'CREATE', 'UPDATE', 'DELETE'
        self.user = user
        self.timestamp = timestamp
        self.details = details or {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'operation': self.operation,
            'user': self.user,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
    
    @classmethod
    def from_dict(cls, data):
        log = cls(
            data['id'],
            data['entity_type'],
            data['entity_id'],
            data['operation'],
            data['user'],
            datetime.fromisoformat(data['timestamp']),
            data.get('details', {})
        )
        return log

class SystemLog:
    """系统操作日志类"""
    def __init__(self, log_id, user, operation, timestamp, details=None):
        self.id = log_id
        self.user = user
        self.operation = operation  # 'LOGIN', 'LOGOUT', 'CREATE_ASSET', etc.
        self.timestamp = timestamp
        self.details = details or {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
    
    @classmethod
    def from_dict(cls, data):
        log = cls(
            data['id'],
            data['user'],
            data['operation'],
            datetime.fromisoformat(data['timestamp']),
            data.get('details', {})
        )
        return log

# 扩展DataManager以支持日志记录
class LoggingDataManager(DataManager):
    """支持日志记录的数据管理器"""
    def __init__(self):
        super().__init__()
        self.change_logs = {}
        self.system_logs = {}
        self.next_ids.update({
            'change_log': 1,
            'system_log': 1
        })
    
    def add_change_log(self, entity_type, entity_id, operation, user, details=None):
        """添加变更日志"""
        log_id = self.get_next_id('change_log')
        log = ChangeLog(log_id, entity_type, entity_id, operation, user, datetime.now(), details)
        self.change_logs[log_id] = log
        return log
    
    def add_system_log(self, user, operation, details=None):
        """添加系统日志"""
        log_id = self.get_next_id('system_log')
        log = SystemLog(log_id, user, operation, datetime.now(), details)
        self.system_logs[log_id] = log
        return log
    
    def get_asset_change_history(self, asset_id):
        """获取资产变更历史"""
        return [log for log in self.change_logs.values() 
                if log.entity_type == 'asset' and log.entity_id == asset_id]
    
    def get_system_logs_by_user(self, user):
        """获取用户的系统操作日志"""
        return [log for log in self.system_logs.values() if log.user == user]
    
    def update_asset_with_logging(self, asset_id, user, **kwargs):
        """更新资产并记录变更日志"""
        asset = self.get_asset(asset_id)
        if not asset:
            return False
        
        # 记录变更前的值
        old_values = {}
        for key, new_value in kwargs.items():
            if hasattr(asset, key):
                old_values[key] = getattr(asset, key)
        
        # 执行更新
        success = self.update_asset(asset_id, **kwargs)
        
        if success and old_values:
            # 记录变更日志
            details = {
                'old_values': old_values,
                'new_values': kwargs
            }
            self.add_change_log('asset', asset_id, 'UPDATE', user, details)
        
        return success

@pytest.fixture(scope="function")
def logging_data_manager():
    """提供一个支持日志记录的数据管理器实例"""
    test_data_file = "test_logging_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = LoggingDataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # 添加测试用户
    dm.add_user("test_user", "password123", 1, roles=["ASSET"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_asset_change_history_recording(logging_data_manager):
    """测试资产变更历史记录 (Metric: 2.6.1)"""
    dm = logging_data_manager
    
    # 创建资产
    asset = dm.add_asset("测试电脑", 5000, 2, "test_user")
    
    # 记录创建日志
    create_log = dm.add_change_log('asset', asset.id, 'CREATE', 'test_user', 
                                  {'name': '测试电脑', 'value': 5000})
    
    # 修改资产名称
    dm.update_asset_with_logging(asset.id, 'test_user', name="新电脑", value=6000)
    
    # 再次修改资产状态
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_USE')
    
    # 获取资产变更历史
    change_history = dm.get_asset_change_history(asset.id)
    
    # 验证变更历史记录
    assert len(change_history) >= 3  # 创建 + 2次修改
    
    # 验证创建记录
    create_record = next((log for log in change_history if log.operation == 'CREATE'), None)
    assert create_record is not None
    assert create_record.user == 'test_user'
    assert create_record.entity_id == asset.id
    
    # 验证修改记录
    update_records = [log for log in change_history if log.operation == 'UPDATE']
    assert len(update_records) == 2
    
    # 验证第一次修改记录（名称和价值）
    name_update = next((log for log in update_records 
                       if 'name' in log.details.get('new_values', {})), None)
    assert name_update is not None
    assert name_update.details['old_values']['name'] == '测试电脑'
    assert name_update.details['new_values']['name'] == '新电脑'
    assert name_update.details['old_values']['value'] == 5000
    assert name_update.details['new_values']['value'] == 6000
    
    # 验证第二次修改记录（状态）
    status_update = next((log for log in update_records 
                         if 'status' in log.details.get('new_values', {})), None)
    assert status_update is not None
    assert status_update.details['old_values']['status'] == 'IDLE'
    assert status_update.details['new_values']['status'] == 'IN_USE'

def test_system_operation_logging(logging_data_manager):
    """测试系统操作日志 (Metric: 2.6.2)"""
    dm = logging_data_manager
    
    # 记录用户登录
    login_log = dm.add_system_log('test_user', 'LOGIN', {'ip': '192.168.1.100'})
    
    # 记录创建资产操作
    asset = dm.add_asset("服务器", 15000, 2, "test_user")
    create_asset_log = dm.add_system_log('test_user', 'CREATE_ASSET', 
                                        {'asset_id': asset.id, 'asset_name': '服务器'})
    
    # 记录修改用户操作
    modify_user_log = dm.add_system_log('admin', 'MODIFY_USER', 
                                       {'target_user': 'test_user', 'action': 'change_role'})
    
    # 记录用户登出
    logout_log = dm.add_system_log('test_user', 'LOGOUT')
    
    # 验证所有日志都已记录
    all_logs = list(dm.system_logs.values())
    assert len(all_logs) == 4
    
    # 验证登录日志
    assert login_log.user == 'test_user'
    assert login_log.operation == 'LOGIN'
    assert login_log.details['ip'] == '192.168.1.100'
    
    # 验证创建资产日志
    assert create_asset_log.user == 'test_user'
    assert create_asset_log.operation == 'CREATE_ASSET'
    assert create_asset_log.details['asset_name'] == '服务器'
    
    # 验证修改用户日志
    assert modify_user_log.user == 'admin'
    assert modify_user_log.operation == 'MODIFY_USER'
    assert modify_user_log.details['target_user'] == 'test_user'
    
    # 验证登出日志
    assert logout_log.user == 'test_user'
    assert logout_log.operation == 'LOGOUT'

def test_get_user_operation_logs(logging_data_manager):
    """测试获取特定用户的操作日志"""
    dm = logging_data_manager
    
    # 记录多个用户的操作
    dm.add_system_log('user1', 'LOGIN')
    dm.add_system_log('user2', 'LOGIN')
    dm.add_system_log('user1', 'CREATE_ASSET', {'asset_name': '电脑'})
    dm.add_system_log('user1', 'LOGOUT')
    dm.add_system_log('user2', 'DELETE_ASSET', {'asset_id': 123})
    
    # 获取user1的操作日志
    user1_logs = dm.get_system_logs_by_user('user1')
    assert len(user1_logs) == 3
    
    operations = [log.operation for log in user1_logs]
    assert 'LOGIN' in operations
    assert 'CREATE_ASSET' in operations
    assert 'LOGOUT' in operations
    
    # 获取user2的操作日志
    user2_logs = dm.get_system_logs_by_user('user2')
    assert len(user2_logs) == 2
    
    user2_operations = [log.operation for log in user2_logs]
    assert 'LOGIN' in user2_operations
    assert 'DELETE_ASSET' in user2_operations

def test_comprehensive_asset_lifecycle_logging(logging_data_manager):
    """测试资产完整生命周期的日志记录"""
    dm = logging_data_manager
    
    # 1. 创建资产
    asset = dm.add_asset("生命周期测试设备", 8000, 2, "test_user")
    dm.add_change_log('asset', asset.id, 'CREATE', 'test_user', 
                     {'name': '生命周期测试设备', 'value': 8000, 'status': 'IDLE'})
    dm.add_system_log('test_user', 'CREATE_ASSET', {'asset_id': asset.id})
    
    # 2. 修改资产信息
    dm.update_asset_with_logging(asset.id, 'test_user', description="添加描述信息")
    dm.add_system_log('test_user', 'UPDATE_ASSET', {'asset_id': asset.id, 'field': 'description'})
    
    # 3. 资产投入使用
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_USE')
    dm.add_system_log('test_user', 'ASSET_IN_USE', {'asset_id': asset.id})
    
    # 4. 资产维修
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_MAINTAIN')
    dm.add_system_log('test_user', 'ASSET_MAINTENANCE', {'asset_id': asset.id})
    
    # 5. 维修完成，重新投入使用
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_USE')
    dm.add_system_log('test_user', 'ASSET_MAINTENANCE_COMPLETE', {'asset_id': asset.id})
    
    # 6. 资产清退
    dm.update_asset_with_logging(asset.id, 'test_user', status='RETIRED')
    dm.add_system_log('test_user', 'ASSET_RETIRED', {'asset_id': asset.id})
    
    # 验证变更历史的完整性
    change_history = dm.get_asset_change_history(asset.id)
    assert len(change_history) == 6  # 创建 + 5次变更（包括description修改）
    
    # 验证操作顺序
    sorted_changes = sorted(change_history, key=lambda x: x.timestamp)
    operations = [log.operation for log in sorted_changes]
    assert operations[0] == 'CREATE'
    assert operations[-1] == 'UPDATE'  # 最后一次是清退操作
    
    # 验证系统日志的完整性
    user_logs = dm.get_system_logs_by_user('test_user')
    assert len(user_logs) == 6
    
    log_operations = [log.operation for log in user_logs]
    assert 'CREATE_ASSET' in log_operations
    assert 'ASSET_RETIRED' in log_operations

def test_log_timestamp_accuracy(logging_data_manager):
    """测试日志时间戳的准确性"""
    dm = logging_data_manager
    
    # 记录操作前的时间
    before_time = datetime.now()
    
    # 执行操作并记录日志
    log = dm.add_system_log('test_user', 'TEST_OPERATION')
    
    # 记录操作后的时间
    after_time = datetime.now()
    
    # 验证时间戳在合理范围内
    assert before_time <= log.timestamp <= after_time
    
    # 验证时间戳格式正确（可以序列化和反序列化）
    log_dict = log.to_dict()
    restored_log = SystemLog.from_dict(log_dict)
    assert restored_log.timestamp == log.timestamp

def test_log_details_preservation(logging_data_manager):
    """测试日志详情信息的保存"""
    dm = logging_data_manager
    
    # 创建包含复杂详情的日志
    complex_details = {
        'old_values': {'name': '旧名称', 'value': 1000, 'status': 'IDLE'},
        'new_values': {'name': '新名称', 'value': 1500, 'status': 'IN_USE'},
        'user_ip': '192.168.1.100',
        'user_agent': 'Mozilla/5.0...',
        'additional_info': {
            'reason': '设备升级',
            'approved_by': 'manager'
        }
    }
    
    log = dm.add_change_log('asset', 123, 'UPDATE', 'test_user', complex_details)
    
    # 验证详情信息完整保存
    assert log.details == complex_details
    assert log.details['old_values']['name'] == '旧名称'
    assert log.details['new_values']['value'] == 1500
    assert log.details['additional_info']['reason'] == '设备升级'
    
    # 验证序列化和反序列化后详情信息不丢失
    log_dict = log.to_dict()
    restored_log = ChangeLog.from_dict(log_dict)
    assert restored_log.details == complex_details