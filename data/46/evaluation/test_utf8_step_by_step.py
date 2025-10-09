#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-8环境下逐步测试
"""
import pytest
import sys
import os
from pathlib import Path

def test_step1_basic():
    """基础测试"""
    assert True
    print("✓ Step 1: Basic test passed")

def test_step2_import_path():
    """测试路径导入"""
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent / "src"
    sys.path.insert(0, str(src_dir))
    
    assert str(src_dir) in sys.path
    print("✓ Step 2: Path import passed")

def test_step3_config_manager():
    """测试ConfigManager导入"""
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent / "src"
    sys.path.insert(0, str(src_dir))
    
    from credit_assessment.utils.config_manager import ConfigManager
    config = ConfigManager()
    
    assert config is not None
    print("✓ Step 3: ConfigManager import passed")

def test_step4_data_manager():
    """测试DataManager导入和使用"""
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent / "src"
    sys.path.insert(0, str(src_dir))
    
    from credit_assessment.utils.config_manager import ConfigManager
    from credit_assessment.data.data_manager import DataManager
    
    config = ConfigManager()
    data_manager = DataManager(config)
    
    assert data_manager is not None
    print("✓ Step 4: DataManager creation passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])