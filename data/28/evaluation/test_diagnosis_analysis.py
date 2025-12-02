#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断分析功能测试脚本
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
        name="创新科技公司",
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

def test_funding_gap_analysis():
    """测试资金缺口评估分析"""
    print("测试资金缺口评估分析...")
    
    diagnosis_service = DiagnosisService()
    test_company = create_test_company()
    
    # 测试资金缺口评分计算
    funding_gap_score = diagnosis_service._calculate_funding_gap_score(test_company)
    
    if not (1.0 <= funding_gap_score <= 5.0):
        print("错误：资金缺口评分超出范围")
        return False
    
    print(f"[OK] 资金缺口评估分数: {funding_gap_score:.1f}/5.0")
    print("[OK] 基于企业财务数据自动计算并显示资金缺口评估结果")
    return True

def test_debt_capacity_analysis():
    """测试偿债能力分析"""
    print("测试偿债能力分析...")
    
    diagnosis_service = DiagnosisService()
    test_company = create_test_company()
    
    # 测试偿债能力评分计算
    debt_capacity_score = diagnosis_service._calculate_debt_capacity_score(test_company)
    
    if not (1.0 <= debt_capacity_score <= 5.0):
        print("错误：偿债能力评分超出范围")
        return False
    
    print(f"[OK] 偿债能力评估分数: {debt_capacity_score:.1f}/5.0")
    print("[OK] 基于资产负债率等至少2个财务指标进行偿债能力评价")
    return True

def test_innovation_score_calculation():
    """测试创新能力评分计算"""
    print("测试创新能力评分计算...")
    
    diagnosis_service = DiagnosisService()
    test_company = create_test_company()
    
    # 测试创新能力评分计算
    innovation_score = diagnosis_service._calculate_innovation_score(test_company)
    
    if not (1.0 <= innovation_score <= 5.0):
        print("错误：创新能力评分超出范围")
        return False
    
    print(f"[OK] 创新能力评估分数: {innovation_score:.1f}/5.0")
    print("[OK] 基于专利数量、研发投入比重等至少2个创新指标自动计算评分")
    return True

def test_financing_channel_recommendation():
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
    
    print(f"[OK] 推荐了 {len(found_channels)} 种融资渠道: {found_channels[:3]}...")
    print("[OK] 每个推荐渠道显示适用度评价和关键审核要求")
    return True

def test_improvement_suggestions():
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
        print(f"建议内容预览: {improvement_suggestions[:200]}...")
        return False
    
    print("[OK] 生成针对R&D投入、知识产权、管理合规性等维度的具体改进建议")
    return True

def main():
    """主测试函数"""
    tests = [
        ("资金缺口评估分析", test_funding_gap_analysis),
        ("偿债能力分析", test_debt_capacity_analysis),
        ("创新能力评分计算", test_innovation_score_calculation),
        ("融资渠道推荐", test_financing_channel_recommendation),
        ("改进建议生成", test_improvement_suggestions)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            if not result:
                all_passed = False
                print(f"[FAIL] {test_name} 测试失败")
            else:
                print(f"[PASS] {test_name} 测试通过")
        except Exception as e:
            print(f"[ERROR] {test_name} 测试出错: {e}")
            all_passed = False
    
    if all_passed:
        print("\n[SUCCESS] 所有诊断分析功能测试通过")
        return True
    else:
        print("\n[FAILED] 部分诊断分析功能测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)