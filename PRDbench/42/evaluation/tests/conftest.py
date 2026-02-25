#!/usr/bin/env python3
"""
pytest配置文件
"""

import pytest
import sys
import os
import tempfile
import shutil

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

@pytest.fixture(scope="session")
def temp_db():
    """创建临时数据库"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    yield db_path
    
    # 清理临时文件
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_app_config():
    """模拟应用配置"""
    return {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    }

# 设置测试环境变量
os.environ['FLASK_ENV'] = 'testing'