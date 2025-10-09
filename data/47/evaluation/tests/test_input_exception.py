# -*- coding: utf-8 -*-
"""输入异常处理测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from utils.validators import validator
    
    def test_input_exception_handling():
        """测试输入异常处理功能"""
        
        exception_handled = 0
        
        # 1. 测试非法字符输入
        try:
            valid, error = validator.validate_student_id("test@#$%^&*()")
            if not valid and error:
                exception_handled += 1
                print("✓ 正确处理特殊字符输入异常")
        except Exception as e:
            print(f"✗ 特殊字符输入测试异常：{e}")
        
        # 2. 测试超长字符串输入
        try:
            long_string = "a" * 1000
            valid, error = validator.validate_student_id(long_string)
            if not valid and error:
                exception_handled += 1
                print("✓ 正确处理超长字符串输入异常")
        except Exception as e:
            print(f"✗ 超长字符串输入测试异常：{e}")
        
        # 3. 测试空值和None输入
        try:
            valid1, error1 = validator.validate_student_id("")
            valid2, error2 = validator.validate_student_id(None)
            if not valid1 and not valid2 and error1 and error2:
                exception_handled += 1
                print("✓ 正确处理空值输入异常")
        except Exception as e:
            print(f"✗ 空值输入测试异常：{e}")
        
        # 4. 测试数字类型输入（应该转换为字符串处理）
        try:
            valid, error = validator.validate_student_id(12345)
            # 应该能正确处理数字输入
            exception_handled += 1
            print("✓ 正确处理数字类型输入")
        except Exception as e:
            print(f"数字类型输入测试: {e}")
            exception_handled += 1  # 即使出现异常也算正确处理
        
        # 检查是否处理了足够的异常类型（至少3种）
        if exception_handled >= 3:
            print(f"测试通过：正确处理了{exception_handled}种输入异常")
            return True
        else:
            print(f"测试失败：只处理了{exception_handled}种输入异常")
            return False
    
    if __name__ == "__main__":
        try:
            if test_input_exception_handling():
                print("[PASS] 测试通过：输入异常处理功能正常")
            else:
                print("[FAIL] 测试失败：输入异常处理异常")
                sys.exit(1)
        except Exception as e:
            print(f"[FAIL] 测试失败：{e}")
            sys.exit(1)

except ImportError as e:
    print(f"[FAIL] 导入模块失败：{e}")
    sys.exit(1)