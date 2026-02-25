#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试关键的file_comparison用例
验证之前的修复是否有效
"""

import sys
import os
import subprocess
import tempfile

def test_single_case(case_name, inputs, description):
    """测试单个用例"""
    print(f"\n{'='*60}")
    print(f"测试: {case_name}")
    print(f"描述: {description}")
    print(f"输入序列: {inputs}")
    print('='*60)
    
    # 将输入转换为实际的换行符
    input_text = inputs.replace('\\n', '\n')
    
    try:
        # 使用subprocess直接执行
        result = subprocess.run(
            ['python', 'main.py'],
            input=input_text,
            text=True,
            capture_output=True,
            cwd='../src',
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        print(f"退出码: {result.returncode}")
        
        # 检查关键指标
        output = result.stdout + result.stderr
        
        has_invalid_choice = "无效选择" in output
        has_normal_exit = "感谢使用推荐系统" in output
        has_menu_display = "主菜单" in output
        has_algorithm_menu = "算法评估" in output
        
        print(f"包含菜单显示: {'是' if has_menu_display else '否'}")
        print(f"包含算法评估菜单: {'是' if has_algorithm_menu else '否'}")
        print(f"是否有无效选择错误: {'是' if has_invalid_choice else '否'}")
        print(f"程序正常退出: {'是' if has_normal_exit else '否'}")
        
        # 显示部分输出
        if len(output) > 0:
            preview = output[:500] + ("..." if len(output) > 500 else "")
            print(f"\n输出预览:\n{preview}")
        
        # 判断测试结果
        if has_invalid_choice:
            result_status = "失败 - 仍有无效选择错误"
            return False
        elif has_normal_exit:
            result_status = "成功 - 程序正常完成"
            return True
        else:
            result_status = "警告 - 程序未正常结束"
            return False
        
    except subprocess.TimeoutExpired:
        result_status = "失败 - 测试超时"
        return False
    except Exception as e:
        result_status = f"失败 - 执行错误: {e}"
        return False
    
    finally:
        print(f"\n结果: {result_status}")

def main():
    """主测试函数"""
    print("File Comparison 关键用例直接测试")
    print("="*80)
    
    # 需要测试的关键用例
    test_cases = [
        {
            'name': '2.3.4 稀疏矩阵处理',
            'inputs': '5\\n4\\n0\\n0',
            'description': '算法评估 -> 运行算法比较 -> 属性效用推荐 -> 返回 -> 退出'
        },
        {
            'name': '2.5.2 图表生成',
            'inputs': '5\\n5\\n1\\n0\\n0',
            'description': '算法评估 -> 运行算法比较 -> 全部算法 -> 返回 -> 退出'
        },
        {
            'name': '2.5.3 决策复杂度',
            'inputs': '2\\n1\\n1\\n1\\n5\\ny\\n0\\n0',
            'description': '推荐功能 -> 为用户生成推荐 -> 用户ID=1 -> 算法=1 -> 推荐数=5 -> 确认 -> 返回 -> 退出'
        },
        {
            'name': '2.6.2 权限管理',
            'inputs': '7\\n3\\n1\\n0\\n0',
            'description': '系统管理 -> 查看日志 -> 选择系统日志 -> 返回 -> 退出'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        success = test_single_case(
            test_case['name'],
            test_case['inputs'], 
            test_case['description']
        )
        results.append((test_case['name'], success))
    
    # 汇总结果
    print(f"\n{'='*80}")
    print("测试结果汇总")
    print('='*80)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    for name, success in results:
        status = "[通过]" if success else "[失败]"
        print(f"{status} {name}")
    
    print(f"\n总计: {total} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if failed == 0:
        print("\n所有关键用例测试通过！修复成功！")
        return True
    else:
        print(f"\n仍有 {failed} 个用例失败，需要进一步调试。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)