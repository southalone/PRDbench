import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'code'))

def test_frame_builder_parser_existence():
    """测试FrameBuilder和FrameParser类是否存在"""
    try:
        # 尝试导入FrameBuilder和FrameParser类
        from utils.frame import FrameBuilder, FrameParser
        
        # 检查FrameBuilder类的方法
        builder_methods = ['build', 'construct', 'create_frame']
        builder_instance = FrameBuilder()
        
        builder_found_methods = []
        for method in builder_methods:
            if hasattr(builder_instance, method):
                builder_found_methods.append(method)
        
        assert len(builder_found_methods) > 0, "FrameBuilder类缺少构建方法"
        
        # 检查FrameParser类的方法
        parser_methods = ['parse', 'decode', 'validate', 'extract']
        parser_instance = FrameParser()
        
        parser_found_methods = []
        for method in parser_methods:
            if hasattr(parser_instance, method):
                parser_found_methods.append(method)
        
        assert len(parser_found_methods) > 0, "FrameParser类缺少解析方法"
        
        # 验证类的基本功能
        assert callable(getattr(builder_instance, builder_found_methods[0])), "FrameBuilder方法不可调用"
        assert callable(getattr(parser_instance, parser_found_methods[0])), "FrameParser方法不可调用"
        
    except ImportError as e:
        pytest.fail(f"无法导入FrameBuilder或FrameParser类: {str(e)}")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")