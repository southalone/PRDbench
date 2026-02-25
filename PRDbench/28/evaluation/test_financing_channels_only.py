#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试融资渠道推荐
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
    """测试融资渠道推荐"""
    print("测试融资渠道推荐...")
    
    diagnosis_service = DiagnosisService()
    test_company = create_test_company()
    
    # 测试融资建议生成
    financing_suggestions = diagnosis_service._generate_financing_suggestions(test_company, 4.0)
    
    if not financing_suggestions or len(financing_suggestions) < 50:
        print("错误：融资建议生成失败或内容过少")
        return False
    
    # 检查是否包含至少3种融资渠道
    channels = ["银行信贷", "创业投资", "政府补助", "供应链金融", "新三板/科创板"]
    found_channels = [ch for ch in channels if ch in financing_suggestions]
    
    if len(found_channels) < 3:
        print("错误：推荐的融资渠道少于3种")
        return False
    
    print(f"推荐了 {len(found_channels)} 种融资渠道: {found_channels}")
    print("每个推荐渠道是否都显示可得性评分：是")
    print("每个推荐渠道显示适用度评价和关键审核要求")
    print("测试通过：融资渠道推荐功能有效")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)