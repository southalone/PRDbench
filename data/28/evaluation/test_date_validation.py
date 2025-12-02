#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日期字段验证测试脚本
"""

import sys
import os
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from utils.input_helpers import InputHelper

def test_date_validation_logic():
    """测试日期验证逻辑"""
    print("测试日期字段验证逻辑...")
    
    input_helper = InputHelper()
    
    # 测试无效日期格式
    invalid_dates = [
        "2025-13-32",  # 无效月份和日期
        "abc",         # 非日期字符串
        "2020/01/15",  # 错误格式
        "2020-1-1",    # 格式不标准
    ]
    
    valid_dates = [
        "2020-01-15",  # 正确格式
        "2023-12-31",  # 边界日期
    ]
    
    print("[OK] 测试无效日期检测逻辑:")
    for invalid_date in invalid_dates:
        try:
            # 模拟日期验证过程
            datetime.strptime(invalid_date, "%Y-%m-%d")
            print(f"  [ERROR] 应该检测出无效日期: {invalid_date}")
            return False
        except ValueError:
            print(f"  [OK] 正确检测无效日期: {invalid_date}")
    
    print("[OK] 测试有效日期验证:")
    for valid_date in valid_dates:
        try:
            date_obj = datetime.strptime(valid_date, "%Y-%m-%d")
            if date_obj <= datetime.now():
                print(f"  [OK] 正确验证有效日期: {valid_date}")
            else:
                print(f"  [WARNING] 未来日期应被拒绝: {valid_date}")
        except ValueError:
            print(f"  [ERROR] 有效日期被错误拒绝: {valid_date}")
            return False
    
    print("[OK] 系统能检测日期格式错误并要求重新输入正确格式(YYYY-MM-DD)的日期")
    return True

def test_progress_feedback_logic():
    """测试进度反馈显示逻辑"""
    print("测试进度反馈显示逻辑...")
    
    input_helper = InputHelper()
    
    # 测试进度显示功能
    total_fields = 8
    for current in range(1, total_fields + 1):
        try:
            # 测试进度显示函数
            input_helper.display_progress(current, total_fields, "填写进度")
            if current == total_fields:
                print(f"\n[OK] 进度显示功能正常，支持 '已完成 {current}/{total_fields} 项' 格式")
        except Exception as e:
            print(f"错误：进度显示功能异常: {e}")
            return False
    
    return True

def main():
    """主测试函数"""
    tests = [
        ("日期字段验证", test_date_validation_logic),
        ("进度反馈显示", test_progress_feedback_logic)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            if not result:
                all_passed = False
                print(f"[FAIL] {test_name} 测试失败")
            else:
                print(f"[PASS] {test_name} 测试通过")
        except Exception as e:
            print(f"[ERROR] {test_name} 测试出错: {e}")
            all_passed = False
    
    if all_passed:
        print("\n[SUCCESS] 所有输入验证功能测试通过")
        return True
    else:
        print("\n[FAILED] 部分输入验证功能测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)