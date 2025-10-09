#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试改进建议生成
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
        patent_count=2,  # 较低值触发改进建议
        copyright_count=1,
        rd_investment=100,
        rd_revenue_ratio=0.05,
        rd_personnel_ratio=0.15,
        innovation_achievements="少量专利",
        internal_control_score=2,  # 较低值触发改进建议
        financial_standard_score=2,
        compliance_training_score=2,
        employment_compliance_score=2,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def main():
    """测试改进建议生成"""
    print("测试改进建议生成...")
    
    diagnosis_service = DiagnosisService()
    test_company = create_test_company()
    
    # 测试改进建议生成 - 使用较低评分触发具体建议
    improvement_suggestions = diagnosis_service._generate_improvement_suggestions(
        test_company, 2.5, 2.5, 2.5, 2.5
    )
    
    if not improvement_suggestions or len(improvement_suggestions) < 50:
        print("错误：改进建议生成失败或内容过少")
        return False
    
    # 检查是否包含三个维度的建议
    keywords_found = []
    if "研发" in improvement_suggestions or "R&D" in improvement_suggestions:
        keywords_found.append("研发投入")
    if "专利" in improvement_suggestions or "知识产权" in improvement_suggestions:
        keywords_found.append("知识产权") 
    if "管理" in improvement_suggestions or "合规" in improvement_suggestions:
        keywords_found.append("管理合规性")
    
    if len(keywords_found) < 2:
        print(f"错误：改进建议覆盖维度不足，仅找到: {keywords_found}")
        return False
    
    print("生成针对R&D投入、知识产权、管理合规性等维度的具体改进建议")
    print("测试通过：改进建议生成功能有效")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)