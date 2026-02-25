#!/usr/bin/env python3
"""
Markdown报告生成测试脚本
测试 [2.3.2c 完整报告导出 (Markdown)] 功能
"""

import subprocess
import os
import sys
from pathlib import Path

def test_markdown_report_generation():
    """测试Markdown报告生成功能"""
    print("🧪 开始测试Markdown报告生成功能...")
    
    # 1. 执行Markdown报告生成命令
    cmd = [
        "python", "-m", "src.main", "report", "generate-full",
        "--data-path", "evaluation/sample_data.csv",
        "--format", "markdown",
        "--output-path", "evaluation/full_report.md"
    ]
    
    print(f"📋 执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return False
        
        print("✅ 命令执行成功")
        print(f"输出: {result.stdout}")
        
        # 2. 检查期望的输出文件是否存在
        output_file = "evaluation/full_report.md"
        expected_file = "evaluation/expected_full_report.md"
        
        if not os.path.exists(output_file):
            print(f"❌ 输出文件不存在: {output_file}")
            return False
        print(f"✅ 输出文件存在: {output_file}")
        
        if not os.path.exists(expected_file):
            print(f"❌ 期望文件不存在: {expected_file}")
            return False
        print(f"✅ 期望文件存在: {expected_file}")
        
        # 3. 验证文件大小不为零
        output_size = os.path.getsize(output_file)
        expected_size = os.path.getsize(expected_file)
        
        if output_size == 0:
            print(f"❌ 输出文件大小为零: {output_file}")
            return False
        print(f"✅ 输出文件大小: {output_size} 字节")
        
        if expected_size == 0:
            print(f"❌ 期望文件大小为零: {expected_file}")
            return False
        print(f"✅ 期望文件大小: {expected_size} 字节")
        
        # 4. 验证文件格式（检查Markdown文件扩展名）
        if not output_file.endswith('.md'):
            print(f"❌ 输出文件不是Markdown格式: {output_file}")
            return False
        print(f"✅ 输出文件是Markdown格式")
        
        # 5. 验证文件内容
        if not validate_markdown_content(output_file, expected_file):
            return False
        
        print("🎉 所有测试通过！Markdown报告生成功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False

def validate_markdown_content(output_file, expected_file):
    """验证Markdown文件内容"""
    print(f"🔍 验证Markdown文件内容...")
    
    try:
        # 读取输出文件
        with open(output_file, 'r', encoding='utf-8') as f:
            output_content = f.read()
        
        # 读取期望文件
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_content = f.read()
        
        # 检查内容是否完全一致
        if output_content == expected_content:
            print("✅ 文件内容与期望输出完全一致")
            return True
        
        # 如果不完全一致，进行详细比较
        print("⚠️  文件内容存在差异，进行详细分析...")
        
        output_lines = output_content.split('\n')
        expected_lines = expected_content.split('\n')
        
        print(f"✅ 输出文件行数: {len(output_lines)}")
        print(f"✅ 期望文件行数: {len(expected_lines)}")
        
        # 检查关键章节是否存在
        required_sections = [
            "# 高尔夫旅游者消费行为分析报告",
            "## 执行摘要",
            "## 数据概览",
            "## 描述性统计分析",
            "### 数值型字段统计",
            "### 分类型字段分布",
            "## 分析结论",
            "## 营销建议"
        ]
        
        for section in required_sections:
            if section in output_content:
                print(f"✅ 包含必需章节: {section}")
            else:
                print(f"❌ 缺少必需章节: {section}")
                return False
        
        # 检查表格格式
        table_headers = [
            "| 字段 | 均值 | 标准差 | 最小值 | 最大值 | 中位数 |",
            "| 类别 | 数量 | 占比 |"
        ]
        
        for header in table_headers:
            if header in output_content:
                print(f"✅ 包含表格格式: {header}")
            else:
                print(f"❌ 缺少表格格式: {header}")
                return False
        
        # 检查数据内容（关键统计数据）
        key_data_points = [
            "本次分析共包含 **10** 条有效记录",
            "涵盖 **11** 个维度的信息",
            "| price_influence | 3.00 | 1.49 | 1 | 5 | 3.00 |",
            "| 男 | 5 | 50.0% |",
            "| 女 | 5 | 50.0% |"
        ]
        
        for data_point in key_data_points:
            if data_point in output_content:
                print(f"✅ 包含关键数据: {data_point}")
            else:
                print(f"❌ 缺少关键数据: {data_point}")
                return False
        
        print("✅ 文件内容验证通过（结构和关键数据正确）")
        return True
        
    except Exception as e:
        print(f"❌ 文件内容验证失败: {e}")
        return False

if __name__ == "__main__":
    success = test_markdown_report_generation()
    sys.exit(0 if success else 1)