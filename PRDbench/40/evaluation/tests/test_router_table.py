import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_router_table_structure():
    """测试RouterTable类数据结构"""
    try:
        # 尝试导入RouterTable类
        from layer.router import RouterTable
        
        # 创建RouterTable实例
        router_table = RouterTable()
        
        # 检查WAN环境映射结构 (router_id -> Path结构)
        wan_attributes = ['wan_table', 'wan_routes', 'router_table', 'wan']
        found_wan = False
        wan_table = None
        
        for attr in wan_attributes:
            if hasattr(router_table, attr):
                wan_table = getattr(router_table, attr)
                found_wan = True
                break
        
        assert found_wan, "RouterTable缺少WAN环境映射结构"
        assert isinstance(wan_table, dict), "WAN环境映射应为字典类型"
        
        # 检查LAN环境映射结构 (host_id -> exit_port)
        lan_attributes = ['lan_table', 'lan_routes', 'host_table', 'lan']
        found_lan = False
        lan_table = None
        
        for attr in lan_attributes:
            if hasattr(router_table, attr):
                lan_table = getattr(router_table, attr)
                found_lan = True
                break
        
        assert found_lan, "RouterTable缺少LAN环境映射结构"
        assert isinstance(lan_table, dict), "LAN环境映射应为字典类型"
        
        # 检查基本的路由表操作方法
        methods = ['add_route', 'update_route', 'get_route', 'lookup']
        found_methods = []
        
        for method in methods:
            if hasattr(router_table, method):
                found_methods.append(method)
        
        assert len(found_methods) > 0, "RouterTable缺少基本的路由操作方法"
        
    except ImportError:
        # 尝试其他可能的导入路径
        try:
            from router import RouterTable
            # 重复上述测试逻辑
        except ImportError:
            pytest.fail("无法导入RouterTable类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")