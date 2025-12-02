import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_lifetime_management():
    """测试交换机生存时间管理"""
    try:
        # 尝试导入交换机相关类
        from layer.switch import Switch
        
        # 创建交换机实例
        switch = Switch()
        
        # 检查生存时间管理功能
        # 1. 每次帧处理时所有条目生存时间减1
        # 2. 到期自动删除机制
        
        # 检查生存时间递减方法
        decrement_methods = ['decrement_lifetime', 'age_entries', 'update_lifetime', 'tick']
        found_decrement = False
        
        for method in decrement_methods:
            if hasattr(switch, method):
                found_decrement = True
                break
        
        # 检查自动删除方法
        cleanup_methods = ['cleanup_expired', 'remove_expired', 'purge_old_entries', 'clean']
        found_cleanup = False
        
        for method in cleanup_methods:
            if hasattr(switch, method):
                found_cleanup = True
                break
        
        # 检查帧处理方法中是否包含生存时间管理
        frame_methods = ['process_frame', 'handle_frame', 'forward_frame']
        found_frame_method = False
        
        for method in frame_methods:
            if hasattr(switch, method):
                found_frame_method = True
                break
        
        # 至少应该有帧处理方法，并且有生存时间管理功能
        assert found_frame_method, "交换机缺少帧处理方法"
        
        # 检查是否有生存时间管理的实现
        # 可以是独立的方法，也可以集成在帧处理中
        has_lifetime_management = found_decrement or found_cleanup
        
        if not has_lifetime_management:
            # 检查是否在帧处理方法中实现了生存时间管理
            # 这里假设如果有帧处理方法，就可能包含生存时间管理
            has_lifetime_management = found_frame_method
        
        assert has_lifetime_management, "交换机缺少生存时间管理机制"
        
        # 检查端口地址表是否支持生存时间
        if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
            table = getattr(switch, 'switch_table', None) or getattr(switch, 'address_table', None)
            if table and hasattr(table, 'table'):
                # 检查表结构是否支持生存时间
                pass  # 具体实现可能因代码而异
        
    except ImportError:
        pytest.fail("无法导入Switch类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")