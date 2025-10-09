#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为2.3.5b报告对比功能准备测试数据
确保有足够的历史报告进行对比测试
"""

import sys
import os
import time
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch
from io import StringIO
from models.database import SessionLocal
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService
from services.report_service import ReportService
from models.schemas import CompanyCreateSchema

def setup_test_company_and_reports():
    """设置测试企业并生成多个历史报告"""
    print("为2.3.5b报告对比功能准备测试数据...")
    
    db = SessionLocal()
    company_service = CompanyService()
    diagnosis_service = DiagnosisService()
    report_service = ReportService()
    
    try:
        # 准备企业基础数据
        company_name = "创新科技公司"
        
        # 删除可能存在的同名企业
        existing = company_service.get_company_by_name(db, company_name)
        if existing:
            company_service.delete_company(db, existing.id)
            print(f"删除现有企业: {company_name}")
        
        # 创建第一版企业信息
        company_data_v1 = {
            'name': company_name,
            'establishment_date': datetime(2020, 1, 15),
            'registered_capital': 1000.0,
            'company_type': '有限责任公司',
            'main_business': '软件开发与技术服务',
            'industry': '信息传输、软件和信息技术服务业',
            'employee_count': 80,
            'annual_revenue': 2000.0,
            'annual_profit': 300.0,
            'asset_liability_ratio': 0.4,
            'patent_count': 3,
            'copyright_count': 2,
            'rd_investment': 200.0,
            'rd_revenue_ratio': 0.1,
            'rd_personnel_ratio': 0.3,
            'innovation_achievements': '开发了多个创新软件产品',
            'internal_control_score': 3,
            'financial_standard_score': 3,
            'compliance_training_score': 3,
            'employment_compliance_score': 3
        }
        
        # 创建第一个企业版本
        schema_v1 = CompanyCreateSchema(**company_data_v1)
        company_v1 = company_service.create_company(db, schema_v1)
        print(f"创建第一版企业信息: {company_v1.name} (ID: {company_v1.id})")
        
        # 生成第一份诊断报告
        diagnosis_result_v1 = diagnosis_service.diagnose_company(db, company_v1)
        report_v1 = report_service.generate_full_report(company_v1, diagnosis_result_v1)
        print(f"生成第一份报告: {report_v1}")
        
        # 等待一秒确保时间戳不同
        time.sleep(1)
        
        # 更新企业信息（改善各项指标）
        update_data_v2 = {
            'annual_revenue': 3000.0,  # 营收增长
            'annual_profit': 500.0,    # 利润增长
            'asset_liability_ratio': 0.3,  # 负债率降低
            'patent_count': 8,         # 专利增加
            'copyright_count': 5,      # 著作权增加
            'rd_investment': 400.0,    # 研发投入增加
            'rd_personnel_ratio': 0.4, # 研发人员比例提升
            'internal_control_score': 4,  # 内控评分提升
            'financial_standard_score': 4,  # 财务规范提升
            'compliance_training_score': 4,  # 合规培训提升
            'employment_compliance_score': 4   # 用工合规提升
        }
        
        # 重新计算研发投入占营收比
        update_data_v2['rd_revenue_ratio'] = update_data_v2['rd_investment'] / update_data_v2['annual_revenue']
        
        # 更新企业信息
        company_v2 = company_service.update_company(db, company_v1.id, update_data_v2)
        print(f"更新企业信息: {company_v2.name}")
        
        # 生成第二份诊断报告
        diagnosis_result_v2 = diagnosis_service.diagnose_company(db, company_v2)
        report_v2 = report_service.generate_full_report(company_v2, diagnosis_result_v2)
        print(f"生成第二份报告: {report_v2}")
        
        # 等待一秒
        time.sleep(1)
        
        # 再次更新企业信息（进一步改善）
        update_data_v3 = {
            'annual_revenue': 4500.0,  # 营收进一步增长
            'annual_profit': 800.0,    # 利润大幅增长
            'asset_liability_ratio': 0.25,  # 负债率进一步降低
            'patent_count': 12,        # 专利大幅增加
            'copyright_count': 8,      # 著作权增加
            'rd_investment': 600.0,    # 研发投入增加
            'rd_personnel_ratio': 0.45, # 研发人员比例进一步提升
            'internal_control_score': 5,  # 内控评分达到优秀
            'financial_standard_score': 5,  # 财务规范达到优秀
            'compliance_training_score': 5,  # 合规培训达到优秀
            'employment_compliance_score': 5   # 用工合规达到优秀
        }
        
        # 重新计算研发投入占营收比
        update_data_v3['rd_revenue_ratio'] = update_data_v3['rd_investment'] / update_data_v3['annual_revenue']
        
        # 再次更新企业信息
        company_v3 = company_service.update_company(db, company_v2.id, update_data_v3)
        print(f"再次更新企业信息: {company_v3.name}")
        
        # 生成第三份诊断报告
        diagnosis_result_v3 = diagnosis_service.diagnose_company(db, company_v3)
        report_v3 = report_service.generate_full_report(company_v3, diagnosis_result_v3)
        print(f"生成第三份报告: {report_v3}")
        
        print(f"\n成功为企业 '{company_name}' 生成了3份历史报告")
        print("现在可以执行2.3.5a和2.3.5b测试点")
        
        return True
        
    except Exception as e:
        print(f"准备测试数据失败: {e}")
        return False
    finally:
        db.close()

def test_report_list():
    """测试报告列表功能"""
    print("\n测试2.3.5a历史报告管理 - 报告归档...")
    
    # 这里可以调用实际的报告列表命令
    import subprocess
    try:
        result = subprocess.run(
            ['python', 'main.py', 'report', 'list'],
            cwd='../src',
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print("报告列表输出:")
        print(result.stdout)
        
        if "创新科技公司" in result.stdout and "报告文件" in result.stdout:
            print("测试通过：历史报告归档功能正常")
            return True
        else:
            print("测试失败：未找到预期的报告列表内容")
            return False
            
    except Exception as e:
        print(f"测试报告列表失败: {e}")
        return False

def test_report_comparison():
    """测试报告对比功能"""
    print("\n测试2.3.5b历史报告管理 - 报告对比...")
    
    # 这里可以调用实际的报告对比命令
    import subprocess
    try:
        result = subprocess.run(
            ['python', 'main.py', 'diagnosis', 'compare', '--name', '创新科技公司'],
            cwd='../src',
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print("报告对比输出:")
        print(result.stdout)
        
        if "对比" in result.stdout and "变化" in result.stdout:
            print("测试通过：报告对比功能有效")
            return True
        else:
            print("测试失败：未找到预期的对比结果")
            return False
            
    except Exception as e:
        print(f"测试报告对比失败: {e}")
        return False

if __name__ == "__main__":
    # 准备测试数据
    if setup_test_company_and_reports():
        # 测试报告归档
        test_report_list()
        
        # 测试报告对比
        test_report_comparison()
    else:
        print("测试数据准备失败，无法执行后续测试")