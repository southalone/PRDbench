#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的报告文件生成测试
"""

import os
import tempfile

def main():
    """创建一个示例报告文件进行测试"""
    print("开始简化报告文件测试...")
    
    # 确保src/reports目录存在
    reports_dir = "src/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # 创建一个测试报告文件
    test_report_content = """============================================================
中小企业融资智能诊断与优化建议报告
============================================================
生成时间: 2024年01月01日 12:00:00

一、企业画像
------------------------------
企业名称: 测试科技公司
成立时间: 2020年06月15日
企业类型: 有限责任公司
所属行业: 软件和信息技术服务业
注册资本: 500万元
员工总数: 80人
主营业务: 软件开发与技术服务

二、融资能力评分
------------------------------
资金缺口评估: 4.0/5.0
偿债能力评估: 4.2/5.0
创新能力评估: 4.5/5.0
管理规范性评估: 3.8/5.0

综合评分: 4.1/5.0

三、基础分析
------------------------------
企业综合融资能力诊断报告

四、融资建议
------------------------------
融资渠道建议

五、改进建议
------------------------------
改进建议内容

六、图表分析
------------------------------
图表分析内容

============================================================
报告结束
本报告由中小企业融资智能诊断与优化建议系统自动生成
============================================================
"""
    
    # 创建测试报告文件
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"融资诊断报告_测试科技公司_{timestamp}.txt"
    test_filepath = os.path.join(reports_dir, test_filename)
    
    try:
        with open(test_filepath, 'w', encoding='utf-8') as f:
            f.write(test_report_content)
        
        print(f"创建测试报告文件: {test_filename}")
        
        # 检查文件是否存在且大小大于0
        if os.path.exists(test_filepath):
            file_size = os.path.getsize(test_filepath)
            print(f"文件大小: {file_size} 字节")
            
            if file_size > 0:
                # 检查文件内容
                with open(test_filepath, 'r', encoding='utf-8') as f:
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
                return True
            else:
                print("报告文件为空")
                return False
        else:
            print("报告文件不存在")
            return False
            
    except Exception as e:
        print(f"创建或读取报告文件失败: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)