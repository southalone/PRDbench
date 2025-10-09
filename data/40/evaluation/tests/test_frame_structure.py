import sys
import os
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_frame_fields_completeness():
    """测试帧结构字段完整性"""
    try:
        # 尝试导入帧相关模块
        from utils.frame import Frame
        
        # 检查帧结构是否包含必需的字段
        required_fields = [
            'frame_delimiter',  # 帧定位符(8位)
            'source_port',      # 源端口(16位)
            'session_state',    # 会话状态(2位)
            'ack_flag',         # 应答标志(1位)
            'sequence_number',  # 序列号(1位)
            'data_segment',     # 数据段(32位)
            'dest_port',        # 目的端口(16位)
            'crc_checksum'      # CRC校验(16位)
        ]
        
        # 检查Frame类是否存在这些字段
        frame_instance = Frame()
        missing_fields = []
        
        for field in required_fields:
            if not hasattr(frame_instance, field):
                missing_fields.append(field)
        
        assert len(missing_fields) == 0, f"缺少字段: {missing_fields}"
        
        # 检查位数设置
        bit_sizes = {
            'frame_delimiter': 8,
            'source_port': 16,
            'session_state': 2,
            'ack_flag': 1,
            'sequence_number': 1,
            'data_segment': 32,
            'dest_port': 16,
            'crc_checksum': 16
        }
        
        for field, expected_bits in bit_sizes.items():
            if hasattr(frame_instance, f"{field}_bits"):
                actual_bits = getattr(frame_instance, f"{field}_bits")
                assert actual_bits == expected_bits, f"{field}位数错误: 期望{expected_bits}, 实际{actual_bits}"
        
    except ImportError as e:
        pytest.fail("无法导入Frame类")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")
    
    print("帧结构字段完整性测试通过")

if __name__ == "__main__":
    try:
        test_frame_fields_completeness()
        print("所有测试通过")
    except Exception as e:
        print(f"测试执行失败: {str(e)}")
        exit(1)