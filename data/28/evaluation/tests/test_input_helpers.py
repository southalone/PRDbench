# -*- coding: utf-8 -*-
"""
输入辅助工具单元测试
"""

import pytest
import sys
import os
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from utils.input_helpers import InputHelper


class TestInputHelper:
    """输入辅助工具测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.input_helper = InputHelper()
    
    def test_format_currency_default_unit(self):
        """测试货币格式化 - 默认单位"""
        result = self.input_helper.format_currency(1000.0)
        assert result == "1,000.00万元"
    
    def test_format_currency_custom_unit(self):
        """测试货币格式化 - 自定义单位"""
        result = self.input_helper.format_currency(5000.0, "元")
        assert result == "5,000.00元"
    
    def test_format_currency_small_amount(self):
        """测试货币格式化 - 小金额"""
        result = self.input_helper.format_currency(123.45)
        assert result == "123.45万元"
    
    def test_format_currency_zero(self):
        """测试货币格式化 - 零金额"""
        result = self.input_helper.format_currency(0.0)
        assert result == "0.00万元"
    
    def test_format_currency_negative(self):
        """测试货币格式化 - 负数"""
        result = self.input_helper.format_currency(-1000.0)
        assert result == "-1,000.00万元"
    
    def test_format_currency_large_amount(self):
        """测试货币格式化 - 大金额"""
        result = self.input_helper.format_currency(1234567.89)
        assert result == "1,234,567.89万元"
    
    def test_format_percentage_normal(self):
        """测试百分比格式化 - 正常比例"""
        result = self.input_helper.format_percentage(0.15)
        assert result == "15.0%"
    
    def test_format_percentage_zero(self):
        """测试百分比格式化 - 零比例"""
        result = self.input_helper.format_percentage(0.0)
        assert result == "0.0%"
    
    def test_format_percentage_one(self):
        """测试百分比格式化 - 100%"""
        result = self.input_helper.format_percentage(1.0)
        assert result == "100.0%"
    
    def test_format_percentage_greater_than_one(self):
        """测试百分比格式化 - 大于100%"""
        result = self.input_helper.format_percentage(1.5)
        assert result == "150.0%"
    
    def test_format_percentage_small_decimal(self):
        """测试百分比格式化 - 小数点"""
        result = self.input_helper.format_percentage(0.123456)
        assert result == "12.3%"
    
    def test_truncate_text_short_text(self):
        """测试文本截断 - 短文本"""
        text = "短文本"
        result = self.input_helper.truncate_text(text, 10)
        assert result == "短文本"
    
    def test_truncate_text_exact_length(self):
        """测试文本截断 - 精确长度"""
        text = "恰好十个字符文本内容"
        result = self.input_helper.truncate_text(text, 10)
        assert result == "恰好十个字符文本内容"
    
    def test_truncate_text_long_text(self):
        """测试文本截断 - 长文本"""
        text = "这是一个很长的文本内容，需要被截断处理"
        result = self.input_helper.truncate_text(text, 10)
        assert result == "这是一个很长的..."
        assert len(result) == 10
    
    def test_truncate_text_english(self):
        """测试文本截断 - 英文文本"""
        text = "This is a very long English text that needs to be truncated"
        result = self.input_helper.truncate_text(text, 20)
        assert result == "This is a very lo..."
        assert len(result) == 20
    
    def test_truncate_text_mixed_language(self):
        """测试文本截断 - 中英文混合"""
        text = "这是中英文mixed text很长的内容"
        result = self.input_helper.truncate_text(text, 15)
        assert result == "这是中英文mixed t..."
        assert len(result) == 15
    
    def test_truncate_text_empty_string(self):
        """测试文本截断 - 空字符串"""
        result = self.input_helper.truncate_text("", 10)
        assert result == ""
    
    def test_truncate_text_custom_max_length(self):
        """测试文本截断 - 自定义最大长度"""
        text = "测试自定义长度截断功能的文本内容"
        result = self.input_helper.truncate_text(text, 8)
        assert result == "测试自定义..."
        assert len(result) == 8
    
    def test_truncate_text_very_short_limit(self):
        """测试文本截断 - 极短限制"""
        text = "测试文本"
        result = self.input_helper.truncate_text(text, 3)
        assert result == "..."
        assert len(result) == 3
    
    def test_truncate_text_boundary_cases(self):
        """测试文本截断 - 边界情况"""
        # 长度为4的情况（正好等于...的长度加1）
        text = "测试边界情况文本"
        result = self.input_helper.truncate_text(text, 4)
        assert result == "测..."
        assert len(result) == 4
    
    def test_format_functions_with_none_input(self):
        """测试格式化函数处理None输入"""
        # 这些函数通常不应该接收None，但测试异常处理
        with pytest.raises((TypeError, AttributeError)):
            self.input_helper.truncate_text(None, 10)
    
    def test_format_currency_precision(self):
        """测试货币格式化精度"""
        # 测试保留两位小数
        result1 = self.input_helper.format_currency(123.4)
        assert result1 == "123.40万元"
        
        result2 = self.input_helper.format_currency(123.456789)
        assert result2 == "123.46万元"  # 四舍五入
    
    def test_format_percentage_precision(self):
        """测试百分比格式化精度"""
        # 测试保留一位小数
        result1 = self.input_helper.format_percentage(0.123)
        assert result1 == "12.3%"
        
        result2 = self.input_helper.format_percentage(0.12789)
        assert result2 == "12.8%"  # 四舍五入


if __name__ == "__main__":
    pytest.main([__file__])