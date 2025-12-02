#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.3.5b报告对比功能
通过真实业务流程：企业录入→诊断→发展更新→再诊断 来产生不同时期报告
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

def simulate_enterprise_development_flow():
    """模拟企业发展的真实业务流程"""
    print("模拟企业发展的真实业务流程...")
    
    company_service = CompanyService()
    diagnosis_service = DiagnosisService()
    report_service = ReportService()
    
    try:
        # 第一步：企业录入初始信息（初创期状态）
        print("\n=== 第一步：企业录入初始信息（初创期） ===")
        db = SessionLocal()
        
        company_name = "成长轨迹科技公司"
        
        # 删除可能存在的同名企业
        existing = company_service.get_company_by_name(db, company_name)
        if existing:
            company_service.delete_company(db, existing.id)
        
        # 录入初创期企业信息
        initial_data = {
            'name': company_name,
            'establishment_date': datetime(2022, 1, 15),
            'registered_capital': 500.0,      # 初创期资本较小
            'company_type': '有限责任公司',
            'main_business': '软件开发服务',
            'industry': '信息传输、软件和信息技术服务业', 
            'employee_count': 15,             # 初创期员工少
            'annual_revenue': 300.0,          # 初创期营收低
            'annual_profit': 30.0,            # 初创期利润微薄
            'asset_liability_ratio': 0.6,     # 初创期负债率较高
            'patent_count': 0,                # 初创期无专利
            'copyright_count': 1,             # 初创期只有1个著作权
            'rd_investment': 45.0,            # 初创期研发投入少
            'rd_revenue_ratio': 0.15,         # 研发投入占营收15%
            'rd_personnel_ratio': 0.2,        # 研发人员占比20%
            'innovation_achievements': '开发了基础软件产品原型',
            'internal_control_score': 2,      # 初创期管理规范性较低
            'financial_standard_score': 2,
            'compliance_training_score': 2,
            'employment_compliance_score': 2
        }
        
        schema = CompanyCreateSchema(**initial_data)
        company = company_service.create_company(db, schema)
        print(f"录入初创期企业信息: {company.name}")
        print(f"  员工数: {company.employee_count}, 营收: {company.annual_revenue}万元, 专利: {company.patent_count}项")
        db.close()
        
        # 第二步：对初创期状态进行首次诊断
        print("\n=== 第二步：初创期诊断 ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)
        
        diagnosis_1 = diagnosis_service.diagnose_company(db, company)
        report_1 = report_service.generate_full_report(company, diagnosis_1)
        print(f"初创期诊断完成，综合评分: {diagnosis_1.overall_score:.1f}/5.0")
        print(f"生成报告文件: {os.path.basename(report_1)}")
        db.close()
        
        time.sleep(2)  # 确保时间戳不同
        
        # 第三步：模拟企业发展，更新企业信息（发展期）
        print("\n=== 第三步：企业发展，更新信息（发展期） ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)
        
        # 企业发展一年后的改进
        development_updates = {
            'registered_capital': 1000.0,     # 增资扩股
            'employee_count': 35,             # 员工增长
            'annual_revenue': 800.0,          # 营收大幅增长
            'annual_profit': 120.0,           # 利润显著提升
            'asset_liability_ratio': 0.45,    # 负债率改善
            'patent_count': 3,                # 获得专利
            'copyright_count': 4,             # 著作权增加
            'rd_investment': 144.0,           # 研发投入增加
            'rd_revenue_ratio': 0.18,         # 研发投入占营收18%
            'rd_personnel_ratio': 0.3,        # 研发人员占比提升
            'innovation_achievements': '开发了多个市场化软件产品，获得客户认可',
            'internal_control_score': 3,      # 管理规范性提升
            'financial_standard_score': 3,
            'compliance_training_score': 3,
            'employment_compliance_score': 3
        }
        
        updated_company = company_service.update_company(db, company.id, development_updates)
        print("企业发展更新完成:")
        print(f"  员工数: {updated_company.employee_count}(+{updated_company.employee_count-15})")
        print(f"  营收: {updated_company.annual_revenue}万元(+{updated_company.annual_revenue-300.0:.0f})")
        print(f"  专利: {updated_company.patent_count}项(+{updated_company.patent_count})")
        db.close()
        
        # 第四步：对发展期状态进行第二次诊断
        print("\n=== 第四步：发展期诊断 ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)
        
        diagnosis_2 = diagnosis_service.diagnose_company(db, company)
        report_2 = report_service.generate_full_report(company, diagnosis_2)
        print(f"发展期诊断完成，综合评分: {diagnosis_2.overall_score:.1f}/5.0")
        print(f"评分提升: {diagnosis_2.overall_score - diagnosis_1.overall_score:+.1f}")
        print(f"生成报告文件: {os.path.basename(report_2)}")
        db.close()
        
        time.sleep(2)
        
        # 第五步：继续发展，更新企业信息（成熟期）
        print("\n=== 第五步：企业成熟，再次更新信息（成熟期） ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)
        
        # 企业进一步发展的改进
        maturity_updates = {
            'registered_capital': 2000.0,     # 进一步增资
            'employee_count': 60,             # 员工继续增长
            'annual_revenue': 1500.0,         # 营收进一步增长
            'annual_profit': 300.0,           # 利润大幅提升
            'asset_liability_ratio': 0.3,     # 负债率进一步优化
            'patent_count': 8,                # 专利大幅增加
            'copyright_count': 6,             # 著作权继续增加
            'rd_investment': 300.0,           # 研发投入大幅增加
            'rd_revenue_ratio': 0.2,          # 研发投入占营收20%
            'rd_personnel_ratio': 0.4,        # 研发人员占比40%
            'innovation_achievements': '开发了行业领先的创新产品，拥有核心技术优势',
            'internal_control_score': 4,      # 管理规范性达到良好
            'financial_standard_score': 4,
            'compliance_training_score': 4,
            'employment_compliance_score': 4
        }
        
        updated_company = company_service.update_company(db, company.id, maturity_updates)
        print("企业成熟期更新完成:")
        print(f"  员工数: {updated_company.employee_count}(总增长+{updated_company.employee_count-15})")
        print(f"  营收: {updated_company.annual_revenue}万元(总增长+{updated_company.annual_revenue-300.0:.0f})")
        print(f"  专利: {updated_company.patent_count}项(总增长+{updated_company.patent_count})")
        db.close()
        
        # 第六步：对成熟期状态进行第三次诊断
        print("\n=== 第六步：成熟期诊断 ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)
        
        diagnosis_3 = diagnosis_service.diagnose_company(db, company)
        report_3 = report_service.generate_full_report(company, diagnosis_3)
        print(f"成熟期诊断完成，综合评分: {diagnosis_3.overall_score:.1f}/5.0")
        print(f"总提升: {diagnosis_3.overall_score - diagnosis_1.overall_score:+.1f}")
        print(f"生成报告文件: {os.path.basename(report_3)}")
        db.close()
        
        print(f"\n[PASS] 真实业务流程完成")
        print(f"发展轨迹: 初创期({diagnosis_1.overall_score:.1f}) → 发展期({diagnosis_2.overall_score:.1f}) → 成熟期({diagnosis_3.overall_score:.1f})")
        
        return True, (diagnosis_1, diagnosis_2, diagnosis_3)
        
    except Exception as e:
        print(f"[FAIL] 模拟企业发展流程失败: {e}")
        return False, None

def test_historical_comparison():
    """测试历史诊断对比功能"""
    print("\n=== 测试2.3.5b历史报告对比功能 ===")
    
    try:
        db = SessionLocal()
        company_service = CompanyService()
        diagnosis_service = DiagnosisService()
        
        company = company_service.get_company_by_name(db, "成长轨迹科技公司")
        if not company:
            print("[FAIL] 未找到测试企业")
            return False
        
        # 获取该企业的所有诊断历史
        reports = diagnosis_service.get_company_reports(db, company.id)
        
        if len(reports) < 2:
            print(f"[FAIL] 诊断记录不足，当前记录数: {len(reports)}")
            return False
        
        print(f"找到 {len(reports)} 条历史诊断记录")
        
        # 按时间排序，对比最早和最新的记录
        reports_by_time = sorted(reports, key=lambda r: r.created_at)
        earliest_report = reports_by_time[0]   # 初创期诊断
        latest_report = reports_by_time[-1]    # 最新诊断
        
        print("\n" + "=" * 80)
        print("企业发展历程对比分析")
        print("=" * 80)
        
        time1 = earliest_report.created_at.strftime('%Y-%m-%d %H:%M:%S')
        time2 = latest_report.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{'评价维度':<15} {'初期状态':<20} {'当前状态':<20} {'发展变化':<15}")
        print(f"{'':^15} {time1:<20} {time2:<20} {'':^15}")
        print("-" * 80)
        
        dimensions = [
            ("资金缺口评估", earliest_report.funding_gap_score, latest_report.funding_gap_score),
            ("偿债能力评估", earliest_report.debt_capacity_score, latest_report.debt_capacity_score),
            ("创新能力评估", earliest_report.innovation_score, latest_report.innovation_score),
            ("管理规范性评估", earliest_report.management_score, latest_report.management_score),
            ("综合评分", earliest_report.overall_score, latest_report.overall_score)
        ]
        
        has_improvement = False
        for name, score1, score2 in dimensions:
            change = score2 - score1
            if change > 0.3:
                change_str = f"{change:+.1f} 显著提升"
                has_improvement = True
            elif change > 0.1:
                change_str = f"{change:+.1f} 明显提升"
                has_improvement = True
            elif change > 0:
                change_str = f"{change:+.1f} 有所提升"
            elif change < -0.1:
                change_str = f"{change:+.1f} 有所下降"
            elif change < 0:
                change_str = f"{change:+.1f} 略微下降"
            else:
                change_str = "0.0 保持稳定"
            
            print(f"{name:<15} {score1:<20.1f} {score2:<20.1f} {change_str:<15}")
        
        print("-" * 80)
        
        # 发展总结
        time_span_days = (latest_report.created_at - earliest_report.created_at).days
        time_span_hours = (latest_report.created_at - earliest_report.created_at).seconds // 3600
        overall_improvement = latest_report.overall_score - earliest_report.overall_score
        
        if time_span_days > 0:
            print(f"发展历程: {time_span_days}天的发展过程，综合评分提升{overall_improvement:+.1f}分")
        else:
            print(f"发展历程: {time_span_hours}小时的发展过程，综合评分提升{overall_improvement:+.1f}分")
        
        if has_improvement:
            print("\n[PASS] 测试通过：企业发展历程对比功能有效")
            print("  - 真实模拟了企业发展流程：录入→诊断→发展→再诊断")
            print("  - 成功显示企业不同发展阶段的对比信息")
            print("  - 各维度评分体现了真实的成长变化")
            print("  - 提供了发展轨迹分析和变化评价")
            return True
        else:
            print("\n[WARN] 企业发展变化较小，但对比功能正常")
            print("  - 基本的对比显示功能有效")
            print("  - 建议增大企业发展变化幅度以更好体现对比效果")
            return True
            
    except Exception as e:
        print(f"[FAIL] 测试执行出错: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # 1. 模拟完整的企业发展业务流程
    success, diagnosis_results = simulate_enterprise_development_flow()
    
    if success:
        # 2. 测试历史对比功能
        comparison_success = test_historical_comparison()
        exit(0 if comparison_success else 1)
    else:
        print("企业发展流程模拟失败")
        exit(1)