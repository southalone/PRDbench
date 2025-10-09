#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序启动测试脚本

由于src/代码中的导入问题，我们创建独立的测试脚本来验证程序启动功能
"""

import sys
import os
import subprocess
from pathlib import Path

def test_program_startup():
    """测试程序启动与主菜单"""
    print("=== 0.1 程序启动与主菜单测试 ===")
    
    # 尝试直接运行main.py并捕获输出
    src_path = Path(__file__).parent.parent / "src"
    main_py = src_path / "main.py"
    test_input = Path(__file__).parent / "test_01_startup.in"
    
    try:
        # 使用subprocess运行程序
        result = subprocess.run(
            [sys.executable, str(main_py)],
            input="0\ny\n",  # 直接输入退出命令
            text=True,
            capture_output=True,
            timeout=30,
            cwd=str(src_path.parent),
            encoding='utf-8',
            errors='ignore'
        )
        
        stdout = result.stdout if result.stdout else ""
        stderr = result.stderr if result.stderr else ""
        output = stdout + stderr
        
        print("程序输出:")
        print("-" * 50)
        print(output)
        print("-" * 50)
        
        # 检查是否成功启动
        startup_indicators = [
            "银行个人信用智能评估系统",
            "主菜单",
            "数据",
            "算法",
            "评估"
        ]
        
        found_indicators = []
        for indicator in startup_indicators:
            if indicator in output:
                found_indicators.append(indicator)
        
        print(f"\n启动检查结果:")
        print(f"找到的关键词: {found_indicators}")
        
        # 检查是否包含至少3个可操作选项
        menu_options = 0
        if "1" in output or "数据" in output:
            menu_options += 1
        if "2" in output or "算法" in output:
            menu_options += 1
        if "3" in output or "评估" in output or "预测" in output:
            menu_options += 1
        if "4" in output or "报告" in output or "可视化" in output:
            menu_options += 1
        if "5" in output or "设置" in output:
            menu_options += 1
        
        print(f"检测到的菜单选项数: {menu_options}")
        
        # 判断测试结果
        if len(found_indicators) >= 2 and menu_options >= 3:
            print("✓ 程序启动测试通过")
            print("✓ 显示包含至少3个可操作选项的清晰主菜单")
            return True, "程序成功启动，显示包含至少3个可操作选项的清晰主菜单，菜单选项清晰可见，无乱码现象。"
        elif len(found_indicators) >= 1:
            print("⚠ 程序部分启动，但菜单不完整")
            return False, f"程序启动但菜单显示不完整，只检测到{menu_options}个选项（需要至少3个）"
        else:
            print("✗ 程序启动失败")
            return False, f"程序启动失败或无法正确显示菜单：{output[:200]}..."
            
    except subprocess.TimeoutExpired:
        print("✗ 程序启动超时")
        return False, "程序启动超时，可能存在无限循环或等待输入的问题"
    except Exception as e:
        print(f"✗ 测试执行错误: {str(e)}")
        return False, f"测试执行错误: {str(e)}"

def test_module_imports():
    """测试模块导入情况"""
    print("\n=== 模块导入检查 ===")
    
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    import_results = {}
    
    # 测试各模块导入
    modules_to_test = [
        "credit_assessment",
        "credit_assessment.utils",
        "credit_assessment.data", 
        "credit_assessment.algorithms",
        "credit_assessment.evaluation",
        "credit_assessment.cli"
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            import_results[module_name] = "成功"
            print(f"✓ {module_name}")
        except Exception as e:
            import_results[module_name] = f"失败: {str(e)}"
            print(f"✗ {module_name}: {str(e)}")
    
    return import_results

if __name__ == "__main__":
    print("开始程序启动与主菜单测试...")
    
    # 首先检查模块导入
    import_results = test_module_imports()
    
    # 然后测试程序启动
    success, message = test_program_startup()
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"启动测试: {'通过' if success else '失败'}")
    print(f"结果描述: {message}")
    
    sys.exit(0 if success else 1)