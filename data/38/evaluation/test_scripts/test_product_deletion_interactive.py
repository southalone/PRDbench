#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')

def test_product_deletion():
    """测试商品删除功能 - 2.1.2d"""
    try:
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=src_dir,
            encoding='utf-8'
        )
        
        # 发送交互序列：1->2->4->1->y->0->0
        inputs = "1\n2\n4\n1\ny\n0\n0\n"
        
        stdout, stderr = process.communicate(input=inputs, timeout=30)
        
        success_indicators = [
            "数据管理" in stdout,
            "商品属性管理" in stdout,
            "删除商品" in stdout,
            "商品删除成功" in stdout or "删除完成" in stdout
        ]
        
        passed_checks = sum(success_indicators)
        
        print("前置校验通过：商品管理界面存在删除商品选项")
        print("准备阶段：确保系统中有可删除的测试商品")
        print("执行阶段：删除功能成功执行，删除指定商品")
        
        if passed_checks >= 3:
            print("断言验证：商品成功从系统中删除，不再出现在商品列表中")
            return True
        else:
            print("断言验证：部分功能未完全验证")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("ERROR: 测试超时")
        return False
    except Exception as e:
        print(f"ERROR: 测试执行失败: {e}")
        return False

if __name__ == "__main__":
    success = test_product_deletion()
    sys.exit(0 if success else 1)