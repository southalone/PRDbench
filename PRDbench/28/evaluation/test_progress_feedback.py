#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.1.3进度反馈显示功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch
from io import StringIO
from cli.company_cli import add_company
from models.database import SessionLocal, Company
from services.company_service import CompanyService

def test_progress_feedback():
    """测试进度反馈显示功能"""
    print("测试2.1.3进度反馈显示...")
    
    # 准备测试输入数据
    test_inputs = [
        "测试进度企业2",  # 企业名称（避免重名）
        "2021-03-15",    # 成立时间
        "200",           # 注册资本
        "1",             # 企业类型选择
        "软件开发服务",   # 主营业务
        "1",             # 所属行业选择
        "50",            # 员工总数
        "1000",          # 年度营收
        "150",           # 年度利润
        "0.4",           # 资产负债率
        "y",             # 是否填写创新能力
        "5",             # 专利数量
        "3",             # 著作权数量
        "250",           # 研发投入
        "0.3",           # 研发人员占比
        "优秀的软件产品", # 创新成果描述
        "y",             # 是否进行管理规范性评价
        "4",             # 内部控制评分
        "4",             # 财务规范评分
        "3",             # 合规培训评分
        "4",             # 用工合规评分
        "n",             # 是否有融资历史
        "y"              # 确认添加
    ]
    
    # 创建输入流
    input_stream = StringIO('\n'.join(test_inputs))
    
    # 捕获输出
    output_stream = StringIO()
    
    try:
        with patch('builtins.input', lambda prompt='': input_stream.readline().strip()):
            with patch('sys.stdout', output_stream):
                # 删除可能存在的同名企业
                db = SessionLocal()
                company_service = CompanyService()
                existing = company_service.get_company_by_name(db, "测试进度企业2")
                if existing:
                    company_service.delete_company(db, existing.id)
                db.close()
                
                # 执行添加企业命令
                add_company()
        
        # 检查输出中的进度信息
        output = output_stream.getvalue()
        print("输出内容:")
        print(output)
        
        # 验证进度反馈是否存在
        progress_indicators = [
            "进度：1/8",
            "进度：2/8", 
            "进度：3/8",
            "进度：4/8",
            "进度：5/8",
            "进度：6/8",
            "进度：7/8",
            "进度：8/8"
        ]
        
        found_progress = []
        for indicator in progress_indicators:
            if indicator in output:
                found_progress.append(indicator)
        
        print(f"\n找到的进度指示器: {found_progress}")
        
        if len(found_progress) >= 6:  # 至少找到6个进度指示器
            print("测试通过：进度反馈显示功能正常")
            return True
        else:
            print(f"测试失败：只找到 {len(found_progress)} 个进度指示器，预期至少6个")
            return False
            
    except Exception as e:
        print(f"测试执行出错: {e}")
        return False

if __name__ == "__main__":
    test_progress_feedback()