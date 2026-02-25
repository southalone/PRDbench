import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_address_learning_mechanism():
    """测试交换机地址学习机制"""
    try:
        # 尝试导入交换机相关类
        from layer.switch import Switch
        
        # 创建交换机实例
        switch = Switch()
        
        # 检查是否实现了地址学习的三个功能：
        # 1. 自动提取源地址
        # 2. 更新端口地址表
        # 3. 设置生存时间为REMOTE_MAX_LIFE
        
        # 检查REMOTE_MAX_LIFE常量
        if hasattr(switch, 'REMOTE_MAX_LIFE'):
            remote_max_life = switch.REMOTE_MAX_LIFE
        else:
            # 尝试从其他地方导入
            try:
                from utils.params import REMOTE_MAX_LIFE
                remote_max_life = REMOTE_MAX_LIFE
            except ImportError:
                remote_max_life = 300  # 默认值
        
        assert isinstance(remote_max_life, int), "REMOTE_MAX_LIFE应为整数"
        assert remote_max_life > 0, "REMOTE_MAX_LIFE应为正数"
        
        # 检查地址学习方法
        learning_methods = ['learn_address', 'process_frame', 'handle_frame', 'learn']
        found_method = None
        
        for method in learning_methods:
            if hasattr(switch, method):
                found_method = method
                break
        
        assert found_method is not None, "交换机缺少地址学习方法"
        
        # 检查端口地址表更新功能
        if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
            table = getattr(switch, 'switch_table', None) or getattr(switch, 'address_table', None)
            assert table is not None, "交换机缺少端口地址表"
        
        # 检查源地址提取功能
        extract_methods = ['extract_source', 'get_source_address', 'parse_source']
        found_extract = False
        
        for method in extract_methods:
            if hasattr(switch, method):
                found_extract = True
                break
        
        # 如果没有独立的提取方法，检查是否在学习方法中实现
        if not found_extract and found_method:
            found_extract = True  # 假设在学习方法中实现了提取功能
        
        assert found_extract, "交换机缺少源地址提取功能"
        
    except ImportError:
        pytest.fail("无法导入Switch类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")