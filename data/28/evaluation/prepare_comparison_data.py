#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为现有企业准备对比测试数据
通过真实业务流程产生不同时期的诊断记录
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService
from services.report_service import ReportService

def prepare_comparison_data_for_existing_company():
    """为现有的创新科技公司准备对比数据"""
    print("为现有企业准备对比测试数据...")
    
    company_service = CompanyService()
    diagnosis_service = DiagnosisService()
    report_service = ReportService()
    
    try:
        db = SessionLocal()
        
        # 获取现有企业
        company = company_service.get_company_by_name(db, "创新科技公司")
        if not company:
            print("[FAIL] 未找到创新科技公司")
            return False
        
        print(f"找到企业: {company.name}")
        print(f"当前状态 - 员工: {company.employee_count}, 营收: {company.annual_revenue}万元, 专利: {company.patent_count}项")
        
        # 模拟企业发展过程，先"退回"到早期状态，然后逐步发展
        
        # 第一步：模拟早期状态（降低各项指标）
        print("\n=== 模拟企业早期发展状态 ===")
        early_stage_data = {
            'employee_count': 30,             # 早期员工较少
            'annual_revenue': 800.0,          # 早期营收较低
            'annual_profit': 100.0,           # 早期利润较少
            'asset_liability_ratio': 0.6,     # 早期负债率较高
            'patent_count': 2,                # 早期专利较少
            'copyright_count': 1,             # 早期著作权较少
            'rd_investment': 120.0,           # 早期研发投入较少
            'rd_revenue_ratio': 0.15,         # 早期研发投入比例
            'rd_personnel_ratio': 0.25,       # 早期研发人员比例
            'innovation_achievements': '开发了初步的软件产品',
            'internal_control_score': 3,      # 早期管理规范性一般
            'financial_standard_score': 3,
            'compliance_training_score': 3,
            'employment_compliance_score': 3
        }
        
        company_service.update_company(db, company.id, early_stage_data)
        updated_company = company_service.get_company_by_name(db, "创新科技公司")
        
        # 对早期状态进行诊断
        diagnosis_early = diagnosis_service.diagnose_company(db, updated_company)
        report_early = report_service.generate_full_report(updated_company, diagnosis_early)
        print(f"早期状态诊断完成，综合评分: {diagnosis_early.overall_score:.1f}")
        
        time.sleep(2)  # 确保时间戳不同
        
        # 第二步：模拟中期发展状态
        print("\n=== 模拟企业中期发展状态 ===")
        mid_stage_data = {
            'employee_count': 55,             # 中期员工增长
            'annual_revenue': 1400.0,         # 中期营收增长
            'annual_profit': 210.0,           # 中期利润提升
            'asset_liability_ratio': 0.45,    # 中期负债率改善
            'patent_count': 5,                # 中期专利增加
            'copyright_count': 3,             # 中期著作权增加
            'rd_investment': 250.0,           # 中期研发投入增加
            'rd_revenue_ratio': 0.18,         # 中期研发投入比例提升
            'rd_personnel_ratio': 0.32,       # 中期研发人员比例提升
            'innovation_achievements': '开发了多个市场认可的创新产品',
            'internal_control_score': 4,      # 中期管理规范性提升
            'financial_standard_score': 3,
            'compliance_training_score': 3,
            'employment_compliance_score': 4
        }
        
        company_service.update_company(db, company.id, mid_stage_data)
        updated_company = company_service.get_company_by_name(db, "创新科技公司")
        
        # 对中期状态进行诊断
        diagnosis_mid = diagnosis_service.diagnose_company(db, updated_company)
        report_mid = report_service.generate_full_report(updated_company, diagnosis_mid)
        print(f"中期状态诊断完成，综合评分: {diagnosis_mid.overall_score:.1f}")
        
        time.sleep(2)
        
        # 第三步：恢复到当前最佳状态
        print("\n=== 恢复到当前最佳状态 ===")
        current_best_data = {
            'employee_count': 80,             # 当前员工水平
            'annual_revenue': 2000.0,         # 当前营收水平
            'annual_profit': 400.0,           # 当前利润水平
            'asset_liability_ratio': 0.3,     # 当前负债率
            'patent_count': 8,                # 当前专利数量
            'copyright_count': 5,             # 当前著作权数量
            'rd_investment': 400.0,           # 当前研发投入
            'rd_revenue_ratio': 0.2,          # 当前研发投入比例
            'rd_personnel_ratio': 0.4,        # 当前研发人员比例
            'innovation_achievements': '开发了行业领先的创新产品，拥有核心技术优势',
            'internal_control_score': 4,      # 当前内控水平
            'financial_standard_score': 4,    # 当前财务规范水平
            'compliance_training_score': 4,   # 当前合规水平
            'employment_compliance_score': 4  # 当前用工合规水平
        }
        
        company_service.update_company(db, company.id, current_best_data)
        updated_company = company_service.get_company_by_name(db, "创新科技公司")
        
        # 对当前状态进行诊断
        diagnosis_current = diagnosis_service.diagnose_company(db, updated_company)
        report_current = report_service.generate_full_report(updated_company, diagnosis_current)
        print(f"当前状态诊断完成，综合评分: {diagnosis_current.overall_score:.1f}")
        
        print(f"\n[PASS] 成功为创新科技公司准备对比数据")
        print(f"发展轨迹: 早期({diagnosis_early.overall_score:.1f}) → 中期({diagnosis_mid.overall_score:.1f}) → 当前({diagnosis_current.overall_score:.1f})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"[FAIL] 准备对比数据失败: {e}")
        return False

if __name__ == "__main__":
    success = prepare_comparison_data_for_existing_company()
    if success:
        print("\n对比数据准备完成，现在可以测试2.3.5b报告对比功能")
    else:
        print("\n对比数据准备失败")
    exit(0 if success else 1)