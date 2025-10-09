#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试2.6.1核心操作日志记录
"""

import subprocess
import sys
import os

def test_operation_log():
    """测试操作日志记录"""
    print("=" * 60)
    print("2.6.1 核心操作日志-完整记录 测试")
    print("=" * 60)
    
    # 输入序列：数据管理(1) → 初始化示例数据(3) → 确认(y) → 返回(0) → 退出(0)
    inputs = "1\n3\ny\n0\n0\n"
    
    print(f"输入序列: {repr(inputs)}")
    print("解释: 数据管理 → 初始化示例数据 → 确认 → 返回 → 退出")
    
    try:
        # 执行测试
        result = subprocess.run(
            ['python', 'main.py'],
            input=inputs,
            text=True,
            capture_output=True,
            cwd='../src',
            timeout=60,
            encoding='utf-8',
            errors='ignore'
        )
        
        print(f"退出码: {result.returncode}")
        
        # 检查是否有无效选择错误
        has_invalid_choice = "无效选择" in result.stdout
        has_normal_exit = "感谢使用推荐系统" in result.stdout
        
        print(f"是否有'无效选择'错误: {'是' if has_invalid_choice else '否'}")
        print(f"程序正常退出: {'是' if has_normal_exit else '否'}")
        
        # 显示关键输出
        if result.stdout:
            print("\n关键输出片段:")
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['数据管理', '初始化', '示例数据', '确认', '返回']):
                    print(f"  {line}")
        
        # 检查日志文件
        log_path = '../src/logs/system.log'
        if os.path.exists(log_path):
            print(f"\n检查日志文件: {log_path}")
            
            # 读取最新的日志条目
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                
            # 查找今天的日志
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            recent_logs = []
            for line in log_content.split('\n'):
                if today in line and any(keyword in line for keyword in ['初始化', '创建', '加载']):
                    recent_logs.append(line)
            
            print(f"找到今日相关日志: {len(recent_logs)} 条")
            if recent_logs:
                print("最新日志样本:")
                for log in recent_logs[-5:]:  # 显示最新5条
                    print(f"  {log}")
                
                # 检查是否包含测试要求的4类信息
                has_time = any('2025-' in log for log in recent_logs)
                has_operation = any('INFO' in log for log in recent_logs)
                has_params = any('创建' in log or '加载' in log for log in recent_logs)
                has_results = any('完成' in log or '条记录' in log for log in recent_logs)
                
                print(f"\n日志内容检查:")
                print(f"  包含操作时间: {'是' if has_time else '否'}")
                print(f"  包含操作类型: {'是' if has_operation else '否'}")
                print(f"  包含输入参数: {'是' if has_params else '否'}")
                print(f"  包含处理结果: {'是' if has_results else '否'}")
                
                criteria_met = sum([has_time, has_operation, has_params, has_results])
                print(f"  满足条件: {criteria_met}/4项")
                
            return not has_invalid_choice and has_normal_exit and len(recent_logs) > 0
        else:
            print(f"日志文件不存在: {log_path}")
            return False
            
    except Exception as e:
        print(f"测试执行失败: {e}")
        return False

if __name__ == "__main__":
    success = test_operation_log()
    print(f"\n测试结果: {'通过' if success else '失败'}")
    sys.exit(0 if success else 1)