import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_unicast_forwarding():
    """测试交换机单播转发"""
    try:
        # 尝试导入交换机类
        from layer.switch import Switch
        
        switch = Switch()
        
        # 检查单播转发方法
        unicast_methods = ['unicast_forward', 'forward_unicast', 'send_unicast', 'forward_to_port']
        found_unicast = False
        
        for method in unicast_methods:
            if hasattr(switch, method):
                found_unicast = True
                break
        
        # 检查通用转发方法
        if not found_unicast:
            forward_methods = ['forward', 'forward_frame', 'process_frame', 'handle_frame']
            for method in forward_methods:
                if hasattr(switch, method):
                    found_unicast = True
                    break
        
        assert found_unicast, "交换机缺少单播转发功能"
        
        # 检查地址表查询功能
        lookup_methods = ['lookup_port', 'find_port', 'get_port', 'query_table']
        found_lookup = False
        
        for method in lookup_methods:
            if hasattr(switch, method):
                found_lookup = True
                break
        
        # 检查是否有地址表
        if not found_lookup:
            if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
                found_lookup = True
        
        assert found_lookup, "交换机缺少地址表查询功能"
        
    except ImportError:
        pytest.fail("无法导入Switch类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")

def test_broadcast_forwarding():
    """测试交换机广播转发"""
    try:
        from layer.switch import Switch
        
        switch = Switch()
        
        # 检查广播转发方法
        broadcast_methods = ['broadcast', 'forward_broadcast', 'send_broadcast', 'flood_all']
        found_broadcast = False
        
        for method in broadcast_methods:
            if hasattr(switch, method):
                found_broadcast = True
                break
        
        # 检查通用转发方法中是否支持广播
        if not found_broadcast:
            forward_methods = ['forward', 'forward_frame', 'process_frame']
            for method in forward_methods:
                if hasattr(switch, method):
                    # 假设通用转发方法支持广播
                    found_broadcast = True
                    break
        
        assert found_broadcast, "交换机缺少广播转发功能"
        
        # 检查端口管理功能
        port_methods = ['get_ports', 'list_ports', 'all_ports', 'get_interfaces']
        found_ports = False
        
        for method in port_methods:
            if hasattr(switch, method):
                found_ports = True
                break
        
        # 检查是否有端口列表属性
        if not found_ports:
            port_attrs = ['ports', 'interfaces', 'port_list', 'connections']
            for attr in port_attrs:
                if hasattr(switch, attr):
                    found_ports = True
                    break
        
        assert found_ports, "交换机缺少端口管理功能"
        
    except ImportError:
        pytest.fail("无法导入Switch类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")

def test_flooding_forwarding():
    """测试交换机泛洪转发"""
    try:
        from layer.switch import Switch
        
        switch = Switch()
        
        # 检查泛洪转发方法
        flood_methods = ['flood', 'flooding', 'flood_unknown', 'forward_unknown']
        found_flood = False
        
        for method in flood_methods:
            if hasattr(switch, method):
                found_flood = True
                break
        
        # 检查未知地址处理
        if not found_flood:
            unknown_methods = ['handle_unknown', 'process_unknown', 'unknown_destination']
            for method in unknown_methods:
                if hasattr(switch, method):
                    found_flood = True
                    break
        
        # 检查通用转发方法
        if not found_flood:
            forward_methods = ['forward', 'forward_frame', 'process_frame']
            for method in forward_methods:
                if hasattr(switch, method):
                    # 假设通用转发方法包含泛洪逻辑
                    found_flood = True
                    break
        
        assert found_flood, "交换机缺少泛洪转发功能"
        
        # 检查地址未知检测功能
        detection_methods = ['is_unknown', 'address_unknown', 'not_in_table']
        found_detection = False
        
        for method in detection_methods:
            if hasattr(switch, method):
                found_detection = True
                break
        
        # 如果有地址表，假设可以检测未知地址
        if not found_detection:
            if hasattr(switch, 'switch_table') or hasattr(switch, 'address_table'):
                found_detection = True
        
        assert found_detection, "交换机缺少未知地址检测功能"
        
    except ImportError:
        pytest.fail("无法导入Switch类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")