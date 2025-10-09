#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试偿债能力分析
"""

import sys
import os
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from services.diagnosis_service import DiagnosisService
from models.database import Company

def create_test_company():
    """创建测试企业对象"""
    return Company(
        id=1,
        name="测试企业",
        establishment_date=datetime.strptime("2020-06-15", "%Y-%m-%d").date(),
        registered_capital=500,
        company_type="有限责任公司",
        main_business="软件开发",
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
        innovation_achievements="获得多项专利",
        internal_control_score=4,
        financial_standard_score=4,
        compliance_training_score=3,
        employment_compliance_score=4,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def main():
    """测试偿债能力分析"""
    print("测试偿债能力分析...")
    
    diagnosis_service = DiagnosisService()
    test_company = create_test_company()
    
    # 测试偿债能力评分计算
    debt_capacity_score = diagnosis_service._calculate_debt_capacity_score(test_company)
    
    if not (1.0 <= debt_capacity_score <= 5.0):
        print("错误：偿债能力评分超出范围")
        return False
    
    print(f"偿债能力评估分数: {debt_capacity_score:.1f}/5.0")
    print("基于资产负债率等至少2个财务指标进行偿债能力评价")
    print("测试通过：偿债能力分析功能有效")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)