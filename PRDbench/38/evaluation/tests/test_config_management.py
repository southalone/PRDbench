# -*- coding: utf-8 -*-
import pytest
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from data_manager import DataManager

def test_config_parameter_driven():
    """测试配置文件管理和参数驱动"""
    # 创建临时配置文件
    test_config = {
        'recommendation': {'top_n': 10, 'similarity_threshold': 0.8},
        'neural_network': {'learning_rate': 0.01}
    }
    
    with open('temp_config.json', 'w') as f:
        json.dump(test_config, f)
    
    # 测试配置加载
    data_manager = DataManager('temp_config.json')
    
    # 断言：配置参数生效
    assert data_manager.config['recommendation']['top_n'] == 10, "推荐数量参数应生效"
    assert data_manager.config['recommendation']['similarity_threshold'] == 0.8, "相似度阈值参数应生效"
    assert data_manager.config['neural_network']['learning_rate'] == 0.01, "学习率参数应生效"
    
    # 清理临时文件
    os.remove('temp_config.json')
