import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_buffer_size_constants():
    """测试缓冲区大小配置"""
    try:
        # 尝试从不同模块导入缓冲区常量
        buffer_constants = {}
        
        # 尝试从params模块导入
        try:
            from utils.params import INTER_NE_BUFSIZE, IN_NE_BUFSIZE
            buffer_constants['INTER_NE_BUFSIZE'] = INTER_NE_BUFSIZE
            buffer_constants['IN_NE_BUFSIZE'] = IN_NE_BUFSIZE
        except ImportError:
            pass
        
        # 尝试从其他可能的模块导入
        if not buffer_constants:
            try:
                from utils.config import INTER_NE_BUFSIZE, IN_NE_BUFSIZE
                buffer_constants['INTER_NE_BUFSIZE'] = INTER_NE_BUFSIZE
                buffer_constants['IN_NE_BUFSIZE'] = IN_NE_BUFSIZE
            except ImportError:
                pass
        
        # 尝试从主模块导入
        if not buffer_constants:
            try:
                import main
                if hasattr(main, 'INTER_NE_BUFSIZE'):
                    buffer_constants['INTER_NE_BUFSIZE'] = main.INTER_NE_BUFSIZE
                if hasattr(main, 'IN_NE_BUFSIZE'):
                    buffer_constants['IN_NE_BUFSIZE'] = main.IN_NE_BUFSIZE
            except ImportError:
                pass
        
        # 检查是否找到了缓冲区常量
        found_constants = len(buffer_constants)
        assert found_constants >= 1, f"至少应定义1个缓冲区大小常量，实际找到{found_constants}个"
        
        # 验证常量值
        for const_name, const_value in buffer_constants.items():
            assert isinstance(const_value, int), f"{const_name}应为整数类型"
            assert const_value > 0, f"{const_name}应为正数，实际值: {const_value}"
            assert const_value <= 65536, f"{const_name}值过大，实际值: {const_value}"
        
        # 检查是否定义了两个必需的常量
        required_constants = ['INTER_NE_BUFSIZE', 'IN_NE_BUFSIZE']
        found_required = [const for const in required_constants if const in buffer_constants]
        
        if len(found_required) == 2:
            # 验证两个缓冲区大小的合理性
            inter_size = buffer_constants['INTER_NE_BUFSIZE']
            in_size = buffer_constants['IN_NE_BUFSIZE']
            
            assert inter_size >= 512, "网元间通信缓冲区应至少512字节"
            assert in_size >= 256, "网元内通信缓冲区应至少256字节"
        
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")