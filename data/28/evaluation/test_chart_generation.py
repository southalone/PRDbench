#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试matplotlib图表生成功能
"""

import sys
import os
import tempfile
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from services.report_service import ReportService
from services.diagnosis_service import DiagnosisService
from models.database import Company
from models.schemas import DiagnosisResultSchema

def create_test_company():
    """创建测试企业对象"""
    return Company(
        id=1,
        name="测试科技公司",
        establishment_date=datetime.strptime("2020-06-15", "%Y-%m-%d").date(),
        registered_capital=500,
        company_type="有限责任公司",
        main_business="软件开发与技术服务",
        industry="软件和信息技术服务业",
        employee_count=80,
        annual_revenue=2000,
        annual_profit=300,
        asset_liability_ratio=0.45,
        patent_count=8,
        copyright_count=12,
        rd_investment=300,
        rd_revenue_ratio=0.15,
        rd_personnel_ratio=0.25,
        innovation_achievements="获得多项软件著作权和实用新型专利",
        internal_control_score=4,
        financial_standard_score=4,
        compliance_training_score=3,
        employment_compliance_score=4,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def create_test_diagnosis():
    """创建测试诊断结果"""
    return DiagnosisResultSchema(
        funding_gap_score=4.0,
        debt_capacity_score=4.2,
        innovation_score=4.5,
        management_score=3.8,
        overall_score=4.1,
        diagnosis_result="融资能力良好",
        financing_suggestions="推荐银行信贷和创业投资",
        improvement_suggestions="建议加强管理规范性"
    )

def main():
    """测试图表生成功能"""
    print("测试matplotlib图表生成功能...")
    
    try:
        # 检查matplotlib是否可用
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        print("matplotlib模块导入成功")
        
        # 创建报告服务实例
        report_service = ReportService()
        
        # 创建测试数据
        test_company = create_test_company()
        test_diagnosis = create_test_diagnosis()
        
        # 测试图表生成
        print("开始生成图表...")
        chart_paths = report_service._generate_charts(test_company, test_diagnosis)
        
        if not chart_paths:
            print("错误：图表生成返回空结果")
            return False
        
        print(f"成功生成 {len(chart_paths)} 个图表:")
        for chart_name, chart_path in chart_paths.items():
            if os.path.exists(chart_path):
                file_size = os.path.getsize(chart_path)
                print(f"  [OK] {chart_name}: {chart_path} ({file_size} 字节)")
            else:
                print(f"  [ERROR] {chart_name}: {chart_path} (文件不存在)")
                return False
        
        # 检查雷达图是否生成
        radar_files = [path for name, path in chart_paths.items() if "radar" in path]
        if radar_files:
            print("评分雷达图生成成功，显示各维度评分情况")
            print("测试通过：matplotlib评分雷达图生成功能正常")
            return True
        else:
            print("错误：未找到雷达图文件")
            return False
            
    except ImportError as e:
        print(f"错误：matplotlib模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"错误：图表生成过程出现异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)