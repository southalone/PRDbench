#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试按年份区分的诊断记录和2.3.5b报告对比功能
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService
from services.report_service import ReportService
from models.schemas import CompanyCreateSchema
from datetime import datetime

def create_yearly_diagnosis_records():
    """创建企业在不同年份的诊断记录"""
    print("创建企业不同年份的诊断记录...")
    
    company_service = CompanyService()
    diagnosis_service = DiagnosisService()
    report_service = ReportService()
    
    try:
        # 创建或获取测试企业
        db = SessionLocal()
        company_name = "年度发展科技公司"
        
        # 删除现有企业重新创建
        existing = company_service.get_company_by_name(db, company_name)
        if existing:
            company_service.delete_company(db, existing.id)
        
        # 创建企业基础信息（当前状态）
        company_data = {
            'name': company_name,
            'establishment_date': datetime(2020, 6, 1),
            'registered_capital': 1000.0,
            'company_type': '有限责任公司',
            'main_business': '软件开发与技术服务',
            'industry': '信息传输、软件和信息技术服务业',
            'employee_count': 50,      # 当前员工数
            'annual_revenue': 1500.0,  # 当前营收
            'annual_profit': 200.0,    # 当前利润
            'asset_liability_ratio': 0.4,  # 当前资产负债率
            'patent_count': 5,         # 当前专利数
            'copyright_count': 3,      # 当前著作权数
            'rd_investment': 300.0,    # 当前研发投入
            'rd_revenue_ratio': 0.2,   # 研发投入占营收比重
            'rd_personnel_ratio': 0.3, # 研发人员占比
            'innovation_achievements': '开发了创新软件产品',
            'internal_control_score': 4,    # 当前内控评分
            'financial_standard_score': 4,  # 当前财务规范评分
            'compliance_training_score': 3, # 当前合规培训评分
            'employment_compliance_score': 4 # 当前用工合规评分
        }
        
        schema = CompanyCreateSchema(**company_data)
        company = company_service.create_company(db, schema)
        print(f"创建企业: {company.name}")
        db.close()
        
        # 模拟2022年的诊断（企业发展初期）
        print("\n=== 2022年诊断 ===")
        db_2022 = SessionLocal()
        company_2022 = company_service.get_company_by_name(db_2022, company_name)
        
        # 更新企业数据为2022年状态（相对较弱）
        updates_2022 = {
            'employee_count': 25,       # 员工较少
            'annual_revenue': 600.0,    # 营收较低
            'annual_profit': 60.0,      # 利润较低
            'asset_liability_ratio': 0.6,  # 负债率较高
            'patent_count': 1,          # 专利较少
            'copyright_count': 1,       # 著作权较少
            'rd_investment': 90.0,      # 研发投入较少
            'rd_revenue_ratio': 0.15,   # 研发投入比例
            'internal_control_score': 2,    # 内控评分较低
            'financial_standard_score': 2,  # 财务规范较低
            'compliance_training_score': 2, # 合规较低
            'employment_compliance_score': 2 # 用工合规较低
        }
        
        company_service.update_company(db_2022, company_2022.id, updates_2022)
        updated_company_2022 = company_service.get_company_by_name(db_2022, company_name)
        
        diagnosis_2022 = diagnosis_service.diagnose_company(db_2022, updated_company_2022, 2022)
        print(f"2022年诊断完成，综合评分: {diagnosis_2022.overall_score:.1f}")
        db_2022.close()
        
        time.sleep(1)
        
        # 模拟2023年的诊断（企业发展中期）
        print("\n=== 2023年诊断 ===")
        db_2023 = SessionLocal()
        company_2023 = company_service.get_company_by_name(db_2023, company_name)
        
        # 更新企业数据为2023年状态（有所发展）
        updates_2023 = {
            'employee_count': 35,       # 员工增加
            'annual_revenue': 1000.0,   # 营收增长
            'annual_profit': 130.0,     # 利润提升
            'asset_liability_ratio': 0.5,  # 负债率改善
            'patent_count': 3,          # 专利增加
            'copyright_count': 2,       # 著作权增加
            'rd_investment': 180.0,     # 研发投入增加
            'rd_revenue_ratio': 0.18,   # 研发投入比例提升
            'internal_control_score': 3,    # 内控评分提升
            'financial_standard_score': 3,  # 财务规范提升
            'compliance_training_score': 3, # 合规提升
            'employment_compliance_score': 3 # 用工合规提升
        }
        
        company_service.update_company(db_2023, company_2023.id, updates_2023)
        updated_company_2023 = company_service.get_company_by_name(db_2023, company_name)
        
        diagnosis_2023 = diagnosis_service.diagnose_company(db_2023, updated_company_2023, 2023)
        print(f"2023年诊断完成，综合评分: {diagnosis_2023.overall_score:.1f}")
        db_2023.close()
        
        time.sleep(1)
        
        # 模拟2024年的诊断（企业成熟期）
        print("\n=== 2024年诊断 ===")
        db_2024 = SessionLocal()
        company_2024 = company_service.get_company_by_name(db_2024, company_name)
        
        # 更新企业数据为2024年状态（当前最佳状态）
        updates_2024 = {
            'employee_count': 50,       # 员工达到当前水平
            'annual_revenue': 1500.0,   # 营收达到当前水平
            'annual_profit': 200.0,     # 利润达到当前水平
            'asset_liability_ratio': 0.4,  # 负债率优化
            'patent_count': 5,          # 专利达到当前水平
            'copyright_count': 3,       # 著作权达到当前水平
            'rd_investment': 300.0,     # 研发投入达到当前水平
            'rd_revenue_ratio': 0.2,    # 研发投入比例优化
            'internal_control_score': 4,    # 内控评分达到优秀
            'financial_standard_score': 4,  # 财务规范优秀
            'compliance_training_score': 3, # 合规良好
            'employment_compliance_score': 4 # 用工合规优秀
        }
        
        company_service.update_company(db_2024, company_2024.id, updates_2024)
        updated_company_2024 = company_service.get_company_by_name(db_2024, company_name)
        
        diagnosis_2024 = diagnosis_service.diagnose_company(db_2024, updated_company_2024, 2024)
        print(f"2024年诊断完成，综合评分: {diagnosis_2024.overall_score:.1f}")
        db_2024.close()
        
        print(f"\n[PASS] 成功创建3个年份的诊断记录")
        print(f"发展轨迹: 2022年({diagnosis_2022.overall_score:.1f}) → 2023年({diagnosis_2023.overall_score:.1f}) → 2024年({diagnosis_2024.overall_score:.1f})")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 创建年度诊断记录失败: {e}")
        return False

def test_yearly_comparison():
    """测试年度对比分析"""
    print("\n测试企业年度发展对比分析...")
    
    try:
        db = SessionLocal()
        company_service = CompanyService()
        diagnosis_service = DiagnosisService()
        
        company = company_service.get_company_by_name(db, "年度发展科技公司")
        if not company:
            print("[FAIL] 未找到测试企业")
            return False
        
        # 获取诊断历史（按年份排序）
        reports = diagnosis_service.get_company_reports(db, company.id)
        
        if len(reports) < 2:
            print(f"[FAIL] 企业年度诊断记录不足，当前记录数: {len(reports)}")
            return False
        
        print(f"[INFO] 找到 {len(reports)} 条年度诊断记录")
        
        # 按年份排序，找到最早和最新的记录
        reports_by_year = sorted(reports, key=lambda r: r.report_year)
        earliest_report = reports_by_year[0]  # 最早年份
        latest_report = reports_by_year[-1]   # 最新年份
        
        print("\n" + "=" * 80)
        print("企业年度发展对比分析")
        print("=" * 80)
        
        print(f"{'评价维度':<15} {f'{earliest_report.report_year}年':<20} {f'{latest_report.report_year}年':<20} {'年度变化':<15}")
        print("-" * 80)
        
        dimensions = [
            ("资金缺口评估", earliest_report.funding_gap_score, latest_report.funding_gap_score),
            ("偿债能力评估", earliest_report.debt_capacity_score, latest_report.debt_capacity_score),
            ("创新能力评估", earliest_report.innovation_score, latest_report.innovation_score),
            ("管理规范性评估", earliest_report.management_score, latest_report.management_score),
            ("综合评分", earliest_report.overall_score, latest_report.overall_score)
        ]
        
        significant_growth = False
        for name, score1, score2 in dimensions:
            change = score2 - score1
            change_str = f"{change:+.1f}"
            if change > 0.5:
                change_str += " 显著提升"
                significant_growth = True
            elif change > 0.2:
                change_str += " 明显提升"
                significant_growth = True
            elif change > 0:
                change_str += " 有所提升"
            elif change < -0.2:
                change_str += " 明显下降"
            elif change < 0:
                change_str += " 略有下降"
            else:
                change_str = "0.0 保持稳定"
            
            print(f"{name:<15} {score1:<20.1f} {score2:<20.1f} {change_str:<15}")
        
        print("-" * 80)
        
        # 年度发展评价
        years_span = latest_report.report_year - earliest_report.report_year
        overall_change = latest_report.overall_score - earliest_report.overall_score
        
        if overall_change > 1.0:
            print(f"年度发展评价: {years_span}年间企业实现跨越式发展，融资能力大幅提升")
        elif overall_change > 0.5:
            print(f"年度发展评价: {years_span}年间企业发展良好，融资能力显著提升")
        elif overall_change > 0.2:
            print(f"年度发展评价: {years_span}年间企业稳步发展，融资能力有所提升")
        else:
            print(f"年度发展评价: {years_span}年间企业发展相对平稳")
        
        if significant_growth:
            print("\n[PASS] 测试通过：年度对比分析功能有效")
            print("  - 成功显示企业不同年份的发展对比")
            print("  - 各维度评分变化清晰，体现年度发展轨迹")
            print("  - 提供年度发展评价和趋势分析")
            return True
        else:
            print("\n[FAIL] 测试失败：未发现明显的年度发展变化")
            return False
            
    except Exception as e:
        print(f"[FAIL] 测试执行出错: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # 1. 创建不同年份的诊断记录
    if create_yearly_diagnosis_records():
        # 2. 测试年度对比分析
        success = test_yearly_comparison()
        exit(0 if success else 1)
    else:
        print("年度诊断记录创建失败")
        exit(1)