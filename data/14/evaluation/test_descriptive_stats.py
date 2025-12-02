#!/usr/bin/env python3
"""
测试脚本：验证描述性统计分析功能
"""

import subprocess
import os
import sys
from pathlib import Path

def test_descriptive_stats():
    """测试描述性统计分析功能"""
    
    # 测试命令
    test_command = [
        "python", "-m", "src.main", "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]
    
    print("🧪 开始测试描述性统计分析...")
    print(f"📋 执行命令: {' '.join(test_command)}")
    
    try:
        # 执行命令
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=os.getcwd()
        )
        
        # 检查退出码
        if result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return False
        
        print("✅ 命令执行成功")
        print(f"📤 标准输出: {result.stdout}")
        
        # 检查输出文件是否存在
        expected_file = Path("evaluation/reports/descriptive/descriptive_stats.md")
        if not expected_file.exists():
            print(f"❌ 期望的输出文件不存在: {expected_file}")
            return False
        
        print(f"✅ 输出文件已生成: {expected_file}")
        
        # 检查文件内容
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证关键内容
        required_elements = [
            "# 描述性统计分析报告",
            "数据概览",
            "数值型字段统计",
            "均值",
            "标准差",
            "分类型字段分布",
            "占比"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ 输出文件缺少必要元素: {missing_elements}")
            return False
        
        print("✅ 输出文件包含所有必要的统计信息")
        print("🎉 描述性统计分析测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False

if __name__ == "__main__":
    success = test_descriptive_stats()
    sys.exit(0 if success else 1)