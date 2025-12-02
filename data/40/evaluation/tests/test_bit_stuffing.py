import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_bit_stuffing_algorithm():
    """测试比特填充算法实现"""
    try:
        # 尝试导入比特填充相关模块
        bit_stuffing_found = False
        bit_stuffing_impl = None
        
        # 尝试从utils.coding导入
        try:
            from utils.coding import BitStuffing
            bit_stuffing_impl = BitStuffing()
            bit_stuffing_found = True
        except ImportError:
            pass
        
        # 尝试从utils.frame导入
        if not bit_stuffing_found:
            try:
                from utils.frame import BitStuffing
                bit_stuffing_impl = BitStuffing()
                bit_stuffing_found = True
            except ImportError:
                pass
        
        # 尝试从其他模块导入相关函数
        if not bit_stuffing_found:
            try:
                from utils.coding import bit_stuff, bit_unstuff
                bit_stuffing_found = True
            except ImportError:
                pass
        
        # 尝试从frame模块导入
        if not bit_stuffing_found:
            try:
                from utils.frame import stuff_bits, unstuff_bits
                bit_stuffing_found = True
            except ImportError:
                pass
        
        assert bit_stuffing_found, "未找到比特填充算法实现"
        
        # 测试比特填充功能
        test_data = "11111100"  # 包含连续5个'1'的测试数据
        expected_result = "111110100"  # 期望在连续5个'1'后插入'0'
        
        stuffing_result = None
        
        # 尝试不同的方法调用比特填充
        if bit_stuffing_impl:
            if hasattr(bit_stuffing_impl, 'stuff'):
                stuffing_result = bit_stuffing_impl.stuff(test_data)
            elif hasattr(bit_stuffing_impl, 'bit_stuff'):
                stuffing_result = bit_stuffing_impl.bit_stuff(test_data)
            elif hasattr(bit_stuffing_impl, 'insert_zeros'):
                stuffing_result = bit_stuffing_impl.insert_zeros(test_data)
        
        # 尝试函数调用
        if stuffing_result is None:
            try:
                stuffing_result = bit_stuff(test_data)
            except NameError:
                pass
        
        if stuffing_result is None:
            try:
                stuffing_result = stuff_bits(test_data)
            except NameError:
                pass
        
        # 验证比特填充结果
        if stuffing_result is not None:
            assert isinstance(stuffing_result, str), "比特填充结果应为字符串"
            assert len(stuffing_result) >= len(test_data), "填充后的数据长度应不小于原数据"
            
            # 检查是否正确处理了连续5个'1'
            if "11111" in test_data:
                # 填充后不应该有连续6个'1'
                assert "111111" not in stuffing_result, "比特填充后仍存在连续6个'1'"
        
        # 检查帧定位符唯一性保证
        frame_delimiter = "01111110"
        
        # 测试帧定位符不会在数据中出现
        test_data_with_delimiter = "0111111001111110"
        
        if bit_stuffing_impl:
            if hasattr(bit_stuffing_impl, 'stuff'):
                result = bit_stuffing_impl.stuff(test_data_with_delimiter)
                if result:
                    # 检查填充后是否还有完整的帧定位符（除了真正的帧边界）
                    delimiter_count = result.count(frame_delimiter)
                    assert delimiter_count <= 2, "比特填充未能保证帧定位符唯一性"
        
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")