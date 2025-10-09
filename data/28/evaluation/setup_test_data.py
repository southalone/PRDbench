#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置测试数据
"""

import sys
import os
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.database import SessionLocal, init_database
from services.company_service import CompanyService
from models.schemas import CompanyCreateSchema

def setup_test_companies():
    """创建测试企业数据"""
    # 初始化数据库
    init_database()
    
    db = SessionLocal()
    company_service = CompanyService()
    
    try:
        # 检查企业是否已存在
        existing_company = company_service.get_company_by_name(db, "创新科技公司")
        if existing_company:
            print("测试企业'创新科技公司'已存在")
            return existing_company
        
        # 创建测试企业数据
        test_company_data = {
            'name': '创新科技公司',
            'establishment_date': datetime.strptime('2020-06-15', '%Y-%m-%d').date(),
            'registered_capital': 500.0,
            'company_type': '有限责任公司',
            'main_business': '软件开发与技术服务',
            'industry': '软件和信息技术服务业',
            'employee_count': 80,
            'annual_revenue': 2000.0,
            'annual_profit': 300.0,
            'asset_liability_ratio': 0.45,
            'patent_count': 8,
            'copyright_count': 12,
            'rd_investment': 300.0,
            'rd_revenue_ratio': 0.15,
            'rd_personnel_ratio': 0.25,
            'innovation_achievements': '获得多项软件著作权和技术专利',
            'internal_control_score': 4,
            'financial_standard_score': 4,
            'compliance_training_score': 3,
            'employment_compliance_score': 4,
            'last_financing_date': None,
            'last_financing_amount': None,
            'last_financing_channel': None
        }
        
        # 创建CompanyCreateSchema对象
        company_schema = CompanyCreateSchema(**test_company_data)
        
        # 创建企业
        company = company_service.create_company(db, company_schema)
        print(f"成功创建测试企业: {company.name}")
        
        return company
        
    except Exception as e:
        print(f"创建测试企业失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def setup_test_diagnosis(company):
    """为测试企业创建诊断记录"""
    if not company:
        print("企业不存在，无法创建诊断记录")
        return None
        
    db = SessionLocal()
    
    try:
        from services.diagnosis_service import DiagnosisService
        diagnosis_service = DiagnosisService()
        
        # 执行诊断
        diagnosis_result = diagnosis_service.diagnose_company(db, company)
        print(f"成功为企业'{company.name}'创建诊断记录")
        
        return diagnosis_result
        
    except Exception as e:
        print(f"创建诊断记录失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def main():
    """主函数"""
    print("开始设置测试数据...")
    
    # 创建测试企业
    company = setup_test_companies()
    
    # 创建诊断记录
    if company:
        diagnosis_result = setup_test_diagnosis(company)
        if diagnosis_result:
            print("测试数据设置完成！")
            return True
    
    print("测试数据设置失败")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)