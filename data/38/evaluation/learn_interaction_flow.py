#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习和理解main.py的真实互动流程
"""

import sys
import os
sys.path.insert(0, '../src')

from main import RecommendationSystemCLI

def learn_menu_structure():
    """学习菜单结构"""
    print("学习main.py的菜单结构和互动流程")
    print("="*80)
    
    try:
        cli = RecommendationSystemCLI()
        
        print("\n1. 主菜单结构:")
        cli.display_main_menu()
        
        print("\n2. 数据管理菜单结构:")
        cli.display_data_menu()
        
        print("\n3. 算法评估菜单结构:")
        cli.display_evaluation_menu()
        
        print("\n4. 系统管理菜单结构:")
        cli.display_system_menu()
        
        print("\n5. 分析测试序列:")
        test_sequences = {
            "2.6.1测试": "1\\n2\\n0\\n0",
            "2.3.4测试": "5\\n1\\n1\\n0\\n0", 
            "2.5.2测试": "5\\n1\\n4\\n0\\n0",
            "2.6.2测试": "7\\n3\\n1\\n0\\n0"
        }
        
        for test_name, sequence in test_sequences.items():
            steps = sequence.split('\\n')
            print(f"\n{test_name}: {sequence}")
            
            if steps[0] == "1":
                print("  步骤1: 进入数据管理")
                if len(steps) > 1:
                    data_options = ["", "查看数据统计", "商品属性管理", "初始化示例数据", "导出数据", "导入数据"]
                    if steps[1].isdigit() and int(steps[1]) < len(data_options):
                        print(f"  步骤2: {data_options[int(steps[1])]}")
            elif steps[0] == "5":
                print("  步骤1: 进入算法评估")
                if len(steps) > 1:
                    eval_options = ["", "运行算法比较", "运行A/B测试", "查看评估历史"]
                    if steps[1].isdigit() and int(steps[1]) < len(eval_options):
                        print(f"  步骤2: {eval_options[int(steps[1])]}")
            elif steps[0] == "7":
                print("  步骤1: 进入系统管理")
                if len(steps) > 1:
                    sys_options = ["", "查看系统状态", "更新配置", "查看日志", "清理缓存"]
                    if steps[1].isdigit() and int(steps[1]) < len(sys_options):
                        print(f"  步骤2: {sys_options[int(steps[1])]}")
            elif steps[0] == "2":
                print("  步骤1: 进入推荐功能")
        
    except Exception as e:
        print(f"学习过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    learn_menu_structure()