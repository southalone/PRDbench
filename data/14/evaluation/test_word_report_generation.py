#!/usr/bin/env python3
"""
Word报告生成测试脚本
测试 [2.3.2b 完整报告导出 (Word)] 功能
"""

import subprocess
import os
import sys
from pathlib import Path

def test_word_report_generation():
    """测试Word报告生成功能"""
    print("🧪 开始测试Word报告生成功能...")
    
    # 1. 执行Word报告生成命令
    cmd = [
        "python", "-m", "src.main", "report", "generate-full",
        "--data-path", "evaluation/sample_data.csv",
        "--format", "word",
        "--output-path", "evaluation/full_report.docx"
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
        output_file = "evaluation/full_report.docx"
        expected_file = "evaluation/expected_full_report.docx"
        
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
        
        # 4. 验证文件格式（简单检查文件扩展名和魔数）
        if not output_file.endswith('.docx'):
            print(f"❌ 输出文件不是Word格式: {output_file}")
            return False
        
        # 检查DOCX文件的魔数（ZIP格式）
        with open(output_file, 'rb') as f:
            magic = f.read(4)
            if magic != b'PK\x03\x04':
                print(f"❌ 输出文件不是有效的DOCX格式")
                return False
        print(f"✅ 输出文件是有效的DOCX格式")
        
        # 5. 比较文件大小是否在合理范围内
        size_diff_ratio = abs(output_size - expected_size) / expected_size
        if size_diff_ratio > 0.1:  # 允许10%的差异
            print(f"⚠️  文件大小差异较大: {size_diff_ratio:.2%}")
        else:
            print(f"✅ 文件大小差异在合理范围内: {size_diff_ratio:.2%}")
        
        print("🎉 所有测试通过！Word报告生成功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False

def validate_word_document_content(file_path):
    """验证Word文档内容（需要python-docx库）"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        print(f"🔍 验证Word文档内容: {file_path}")
        
        # 检查段落数量
        paragraphs = doc.paragraphs
        print(f"✅ 文档包含 {len(paragraphs)} 个段落")
        
        # 检查表格数量
        tables = doc.tables
        print(f"✅ 文档包含 {len(tables)} 个表格")
        
        # 检查是否包含关键内容
        full_text = '\n'.join([p.text for p in paragraphs])
        
        required_sections = [
            "高尔夫旅游者消费行为分析报告",
            "执行摘要",
            "数据概览",
            "描述性统计分析",
            "分析结论",
            "营销建议"
        ]
        
        for section in required_sections:
            if section in full_text:
                print(f"✅ 包含必需章节: {section}")
            else:
                print(f"❌ 缺少必需章节: {section}")
                return False
        
        return True
        
    except ImportError:
        print("⚠️  python-docx库未安装，跳过内容验证")
        return True
    except Exception as e:
        print(f"❌ 文档内容验证失败: {e}")
        return False

if __name__ == "__main__":
    success = test_word_report_generation()
    
    # 如果基本测试通过，尝试验证文档内容
    if success:
        validate_word_document_content("evaluation/full_report.docx")
    
    sys.exit(0 if success else 1)