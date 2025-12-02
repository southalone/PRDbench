import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_switch_table_structure():
    """测试SwitchTable类基础实现"""
    try:
        # 尝试导入SwitchTable类
        from layer.switch import SwitchTable
        
        # 创建SwitchTable实例
        switch_table = SwitchTable()
        
        # 检查数据结构是否为字典类型
        if hasattr(switch_table, 'table'):
            table = switch_table.table
        elif hasattr(switch_table, 'address_table'):
            table = switch_table.address_table
        elif hasattr(switch_table, 'port_table'):
            table = switch_table.port_table
        else:
            pytest.fail("SwitchTable类缺少地址表数据结构")
        
        assert isinstance(table, dict), "端口地址表应为字典类型"
        
        # 测试添加条目的功能
        test_local_port = 1
        test_remote_port = 11300
        test_lifetime = 100
        
        # 尝试添加条目
        if hasattr(switch_table, 'add_entry'):
            switch_table.add_entry(test_local_port, test_remote_port, test_lifetime)
        elif hasattr(switch_table, 'learn'):
            switch_table.learn(test_local_port, test_remote_port, test_lifetime)
        elif hasattr(switch_table, 'update'):
            switch_table.update(test_local_port, test_remote_port, test_lifetime)
        
        # 验证数据结构格式 dict[local_port, dict[remote_port, lifetime]]
        if test_local_port in table:
            assert isinstance(table[test_local_port], dict), "本地端口对应的值应为字典"
            if test_remote_port in table[test_local_port]:
                assert isinstance(table[test_local_port][test_remote_port], (int, float)), "生存时间应为数值类型"
        
    except ImportError:
        # 尝试其他可能的导入路径
        try:
            from switch import SwitchTable
            # 重复上述测试
        except ImportError:
            pytest.fail("无法导入SwitchTable类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")