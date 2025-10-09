#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入测试脚本

验证开发部门修复后的LoggerMixin导入问题是否已解决
"""

import sys
import os
from pathlib import Path

# 添加src路径到系统路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """测试所有关键模块的导入"""
    print("=== 导入修复验证测试 ===")
    
    import_results = {}
    
    # 测试各模块导入
    modules_to_test = [
        ("credit_assessment", "主模块"),
        ("credit_assessment.utils", "工具模块"),
        ("credit_assessment.utils.logger", "日志模块"),
        ("credit_assessment.data", "数据管理模块"),
        ("credit_assessment.algorithms", "算法模块"),
        ("credit_assessment.evaluation", "评估模块"),
        ("credit_assessment.cli", "命令行界面模块")
    ]
    
    all_success = True
    
    for module_name, module_desc in modules_to_test:
        try:
            __import__(module_name)
            import_results[module_name] = "成功"
            print(f"✓ {module_desc}: {module_name}")
        except Exception as e:
            import_results[module_name] = f"失败: {str(e)}"
            print(f"✗ {module_desc}: {module_name}")
            print(f"  错误详情: {str(e)}")
            all_success = False
    
    # 特别测试LoggerMixin导入
    print("\n=== LoggerMixin导入专项测试 ===")
    try:
        from credit_assessment.utils import LoggerMixin, OperationLogger
        print("✓ LoggerMixin导入成功")
        print("✓ OperationLogger导入成功")
        
        # 测试LoggerMixin实例化
        class TestClass(LoggerMixin):
            pass
        
        test_obj = TestClass()
        logger = test_obj.logger
        print("✓ LoggerMixin实例化成功")
        
        # 测试OperationLogger实例化
        op_logger = OperationLogger("test")
        print("✓ OperationLogger实例化成功")
        
    except Exception as e:
        print(f"✗ LoggerMixin导入失败: {str(e)}")
        all_success = False
    
    # 测试完整CLI导入链
    print("\n=== CLI导入链测试 ===")
    try:
        from credit_assessment.cli import CreditAssessmentCLI
        cli = CreditAssessmentCLI()
        print("✓ CreditAssessmentCLI创建成功")
        
    except Exception as e:
        print(f"✗ CLI导入链失败: {str(e)}")
        all_success = False
    
    print("\n" + "="*50)
    if all_success:
        print("🎉 所有导入测试通过！LoggerMixin问题已修复！")
        print("✓ 系统现在可以正常启动")
        return True
    else:
        print("❌ 仍存在导入问题，需要进一步修复")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)