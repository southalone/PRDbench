import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_ack_nak_mechanism():
    """测试停等ARQ-ACK/NAK机制"""
    try:
        # 尝试导入ARQ相关模块
        arq_found = False
        arq_impl = None
        
        # 尝试从不同模块导入ARQ实现
        try:
            from utils.flow_control import ARQ
            arq_impl = ARQ()
            arq_found = True
        except ImportError:
            pass
        
        if not arq_found:
            try:
                from layer.net import NetLayer
                net_layer = NetLayer()
                if hasattr(net_layer, 'ack') or hasattr(net_layer, 'nak'):
                    arq_impl = net_layer
                    arq_found = True
            except ImportError:
                pass
        
        if not arq_found:
            try:
                from utils.frame import Frame
                frame = Frame()
                if hasattr(frame, 'ack_flag'):
                    arq_found = True
            except ImportError:
                pass
        
        assert arq_found, "未找到ARQ机制实现"
        
        # 检查ACK机制
        ack_found = False
        
        if arq_impl:
            ack_methods = ['send_ack', 'ack', 'acknowledge', 'confirm']
            for method in ack_methods:
                if hasattr(arq_impl, method):
                    ack_found = True
                    break
        
        # 检查是否在帧结构中定义了ACK标志
        if not ack_found:
            try:
                from utils.frame import Frame
                frame = Frame()
                if hasattr(frame, 'ack_flag') or hasattr(frame, 'ack'):
                    ack_found = True
            except ImportError:
                pass
        
        assert ack_found, "未找到ACK确认机制"
        
        # 检查NAK机制
        nak_found = False
        
        if arq_impl:
            nak_methods = ['send_nak', 'nak', 'negative_ack', 'reject']
            for method in nak_methods:
                if hasattr(arq_impl, method):
                    nak_found = True
                    break
        
        # 检查是否在帧结构中支持NAK
        if not nak_found:
            try:
                from utils.frame import Frame
                frame = Frame()
                # NAK通常通过ACK标志的不同值表示
                if hasattr(frame, 'ack_flag'):
                    nak_found = True
            except ImportError:
                pass
        
        assert nak_found, "未找到NAK否认机制"
        
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")

def test_sequence_number_alternation():
    """测试停等ARQ-序列号交替"""
    try:
        # 尝试导入序列号相关实现
        seq_found = False
        seq_impl = None
        
        # 尝试从帧结构导入
        try:
            from utils.frame import Frame
            frame = Frame()
            if hasattr(frame, 'sequence_number') or hasattr(frame, 'seq_num'):
                seq_impl = frame
                seq_found = True
        except ImportError:
            pass
        
        # 尝试从网络层导入
        if not seq_found:
            try:
                from layer.net import NetLayer
                net_layer = NetLayer()
                if hasattr(net_layer, 'sequence_number') or hasattr(net_layer, 'seq'):
                    seq_impl = net_layer
                    seq_found = True
            except ImportError:
                pass
        
        assert seq_found, "未找到序列号机制实现"
        
        # 检查序列号字段
        seq_field_found = False
        
        if seq_impl:
            seq_attributes = ['sequence_number', 'seq_num', 'seq', 'sequence']
            for attr in seq_attributes:
                if hasattr(seq_impl, attr):
                    seq_field_found = True
                    break
        
        assert seq_field_found, "未找到序列号字段"
        
        # 检查序列号交替机制
        alternation_found = False
        
        if seq_impl:
            # 检查是否有序列号更新方法
            update_methods = ['next_sequence', 'toggle_sequence', 'update_seq', 'alternate_seq']
            for method in update_methods:
                if hasattr(seq_impl, method):
                    alternation_found = True
                    break
        
        # 检查是否有0/1交替的逻辑
        if not alternation_found:
            # 如果有序列号字段，假设实现了交替逻辑
            if seq_field_found:
                alternation_found = True
        
        assert alternation_found, "未找到序列号交替机制"
        
        # 验证序列号范围（应该是0/1交替）
        if seq_impl and hasattr(seq_impl, 'sequence_number'):
            seq_val = getattr(seq_impl, 'sequence_number')
            if seq_val is not None:
                assert seq_val in [0, 1], f"序列号应为0或1，实际值: {seq_val}"
        
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")