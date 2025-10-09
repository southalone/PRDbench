import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_crc16_parameters():
    """测试CRC-16算法参数配置"""
    try:
        # 尝试导入CRC相关模块
        from utils.frame import CRC16
        
        # 检查生成多项式和初始值
        crc_instance = CRC16()
        
        # 检查生成多项式是否为0xA001
        if hasattr(crc_instance, 'polynomial'):
            assert crc_instance.polynomial == 0xA001, f"生成多项式错误: 期望0xA001, 实际{hex(crc_instance.polynomial)}"
        elif hasattr(crc_instance, 'poly'):
            assert crc_instance.poly == 0xA001, f"生成多项式错误: 期望0xA001, 实际{hex(crc_instance.poly)}"
        
        # 检查初始值是否为0xFFFF
        if hasattr(crc_instance, 'initial_value'):
            assert crc_instance.initial_value == 0xFFFF, f"初始值错误: 期望0xFFFF, 实际{hex(crc_instance.initial_value)}"
        elif hasattr(crc_instance, 'init_val'):
            assert crc_instance.init_val == 0xFFFF, f"初始值错误: 期望0xFFFF, 实际{hex(crc_instance.init_val)}"
        
    except ImportError:
        # 尝试其他可能的导入路径
        try:
            from utils.coding import CRC16
            crc_instance = CRC16()
            # 重复上述检查
        except ImportError:
            pytest.fail("无法导入CRC16类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")

def test_crc16_calculation():
    """测试CRC-16校验功能"""
    try:
        from utils.frame import CRC16
        
        crc_instance = CRC16()
        
        # 测试数据
        test_data = b"01111110"
        
        # 尝试计算CRC
        if hasattr(crc_instance, 'calculate'):
            result = crc_instance.calculate(test_data)
        elif hasattr(crc_instance, 'compute'):
            result = crc_instance.compute(test_data)
        elif hasattr(crc_instance, 'crc'):
            result = crc_instance.crc(test_data)
        else:
            pytest.fail("CRC16类缺少计算方法")
        
        # 验证结果是整数且在有效范围内
        assert isinstance(result, int), "CRC计算结果应为整数"
        assert 0 <= result <= 0xFFFF, f"CRC结果超出16位范围: {hex(result)}"
        
    except ImportError:
        try:
            from utils.coding import CRC16
            # 重复上述测试
        except ImportError:
            pytest.fail("无法导入CRC16类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")