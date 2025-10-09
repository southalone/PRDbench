#!/usr/bin/env python3
"""
简单的交互式计算器 - 用于测试Judge工具
"""

print("=== 简单计算器 ===")
print("请输入两个数字进行计算")

try:
    # 获取用户输入
    num1 = int(input("请输入第一个数字: "))
    num2 = int(input("请输入第二个数字: "))
    
    # 执行计算
    add_result = num1 + num2
    mul_result = num1 * num2
    
    # 输出结果
    print(f"\n计算结果:")
    print(f"{num1} + {num2} = {add_result}")
    print(f"{num1} × {num2} = {mul_result}")
    print("\n感谢使用计算器！")
    
except ValueError:
    print("错误: 请输入有效的整数")
    exit(1)
except KeyboardInterrupt:
    print("\n程序被用户中断")
    exit(1)
except Exception as e:
    print(f"未知错误: {e}")
    exit(1) 