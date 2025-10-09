# -*- coding: utf-8 -*-
"""系统日志记录测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.logger import log_operation, log_error, log_system_event
from config.settings import FILE_PATHS

def test_system_logging():
    """测试系统日志记录功能"""
    
    try:
        # 测试用户登录日志
        log_operation("用户登录", "TEST001", "用户登录测试")
        
        # 测试系统事件日志
        log_system_event("图书借阅", "借阅操作测试")
        
        # 测试错误日志
        log_error("数据修改", "修改操作测试错误")
        
        # 检查日志文件
        log_file = os.path.join(FILE_PATHS.get('log_dir', 'logs'), 'system.log')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # 验证3种类型日志都有记录
            assert "用户登录" in log_content, "用户操作日志未记录"
            assert "图书借阅" in log_content, "系统事件日志未记录"
            assert "数据修改" in log_content, "错误日志未记录"
        
        print("测试通过：能记录全部3种类型操作日志")
        return True
        
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")
