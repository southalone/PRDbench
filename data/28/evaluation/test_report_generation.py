#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告文件生成测试脚本
"""

import os
import sys
import subprocess
import tempfile
import time

def run_command_with_input(command, input_data=None):
    """运行命令并提供输入"""
    try:
        if input_data:
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd='src'
            )
            stdout, stderr = process.communicate(input=input_data)
        else:
            process = subprocess.Popen(
                command, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd='src'
            )
            stdout, stderr = process.communicate()
        
        return process.returncode, stdout, stderr
    except Exception as e:
        return -1, "", str(e)

def main():
    """主测试流程"""
    print("开始报告文件生成测试...")
    
    # 企业创建输入数据
    company_input = """测试科技公司
2020-06-15
500
1
软件开发与技术服务
6
80
2000
300
0.45
y
8
12
300
0.25
获得多项软件著作权和实用新型专利
y
4
4
3
4
n
"""
    
    # 步骤1: 创建企业
    print("1. 创建测试企业...")
    returncode, stdout, stderr = run_command_with_input(
        "python main.py company add", 
        company_input
    )
    
    if returncode != 0:
        print(f"企业创建失败: {stderr}")
        return False
    
    print("企业创建成功")
    
    # 步骤2: 生成报告
    print("2. 生成诊断报告...")
    report_input = "y\nn\n"  # 执行诊断：是，查看报告：否
    
    returncode, stdout, stderr = run_command_with_input(
        "python main.py report generate --name 测试科技公司",
        report_input
    )
    
    if returncode != 0:
        print(f"报告生成失败: {stderr}")
        return False
    
    print("报告生成成功")
    
    # 步骤3: 检查文件是否存在
    print("3. 检查报告文件...")
    
    # 报告服务在src目录下创建reports文件夹
    os.chdir('src')
    reports_dir = "reports"
    
    if not os.path.exists(reports_dir):
        print("报告目录不存在")
        os.chdir('..')  # 返回原目录
        return False
    
    # 查找匹配的报告文件
    import glob
    pattern = os.path.join(reports_dir, "融资诊断报告_测试科技公司_*.txt")
    report_files = glob.glob(pattern)
    
    if not report_files:
        print("未找到报告文件")
        # 列出所有文件看看
        print("reports目录内容:")
        for item in os.listdir(reports_dir):
            item_path = os.path.join(reports_dir, item)
            if os.path.isfile(item_path):
                print(f"  文件: {item}")
            else:
                print(f"  目录: {item}")
        os.chdir('..')  # 返回原目录
        return False
    
    report_file = report_files[0]  # 取第一个匹配的文件
    
    # 检查文件大小
    file_size = os.path.getsize(report_file)
    if file_size == 0:
        print("报告文件为空")
        return False
    
    print(f"找到报告文件: {os.path.basename(report_file)}")
    print(f"文件大小: {file_size} 字节")
    
    # 检查文件内容结构
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的内容
        required_sections = [
            "中小企业融资智能诊断与优化建议报告",
            "一、企业画像",
            "二、融资能力评分",
            "三、基础分析",
            "四、融资建议",
            "五、改进建议",
            "六、图表分析"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"报告缺少必要章节: {missing_sections}")
            return False
        
        print("报告文件内容结构完整")
        print("测试通过：报告文件保存功能正常")
        os.chdir('..')  # 返回原目录
        return True
        
    except Exception as e:
        print(f"读取报告文件失败: {e}")
        os.chdir('..')  # 返回原目录
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)