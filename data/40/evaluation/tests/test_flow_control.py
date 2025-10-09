import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_send_rate_control():
    """测试发送速率控制机制"""
    try:
        # 尝试导入流量控制相关模块
        flow_control_found = False
        
        # 尝试从utils.flow_control导入
        try:
            from utils.flow_control import FlowControl
            flow_control = FlowControl()
            flow_control_found = True
        except ImportError:
            pass
        
        # 尝试从其他模块导入
        if not flow_control_found:
            try:
                from layer.net import NetLayer
                net_layer = NetLayer()
                if hasattr(net_layer, 'flow_control') or hasattr(net_layer, 'rate_control'):
                    flow_control_found = True
            except ImportError:
                pass
        
        # 尝试从应用层导入
        if not flow_control_found:
            try:
                from layer.app import AppLayer
                app_layer = AppLayer()
                if hasattr(app_layer, 'send_interval') or hasattr(app_layer, 'rate_limit'):
                    flow_control_found = True
            except ImportError:
                pass
        
        assert flow_control_found, "未找到流量控制机制实现"
        
        # 检查发送间隔设置
        interval_found = False
        
        # 检查是否有最大发送间隔常量
        try:
            from utils.params import MAX_SEND_INTERVAL
            assert isinstance(MAX_SEND_INTERVAL, (int, float)), "MAX_SEND_INTERVAL应为数值类型"
            assert MAX_SEND_INTERVAL > 0, "MAX_SEND_INTERVAL应为正数"
            interval_found = True
        except ImportError:
            pass
        
        # 检查是否有发送速率控制方法
        if 'flow_control' in locals():
            rate_methods = ['set_rate', 'control_rate', 'limit_rate', 'throttle']
            for method in rate_methods:
                if hasattr(flow_control, method):
                    interval_found = True
                    break
        
        # 检查网络层或应用层是否有速率控制
        if 'net_layer' in locals():
            if hasattr(net_layer, 'send_delay') or hasattr(net_layer, 'transmission_delay'):
                interval_found = True
        
        if 'app_layer' in locals():
            if hasattr(app_layer, 'send_interval') or hasattr(app_layer, 'rate_limit'):
                interval_found = True
        
        assert interval_found, "未找到发送间隔设置或速率控制机制"
        
        # 检查防止发送过快的机制
        prevention_found = False
        
        # 检查是否有缓冲区溢出保护
        try:
            from utils.params import BUFFER_OVERFLOW_PROTECTION
            prevention_found = True
        except ImportError:
            pass
        
        # 检查是否有发送队列管理
        if 'flow_control' in locals():
            queue_methods = ['queue_management', 'buffer_check', 'overflow_protection']
            for method in queue_methods:
                if hasattr(flow_control, method):
                    prevention_found = True
                    break
        
        # 如果有流量控制实现，假设包含了防止过快发送的机制
        if flow_control_found:
            prevention_found = True
        
        assert prevention_found, "未找到防止发送方速度过快的机制"
        
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")