#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证诊断记录数据库连接和内容
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal, DATABASE_URL
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService

def verify_database_records():
    """验证数据库中的诊断记录"""
    print(f"数据库URL: {DATABASE_URL}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查数据库文件是否存在
    db_paths_to_check = [
        "src/data/sme_financing.db",
        "data/sme_financing.db", 
        "../src/data/sme_financing.db"
    ]
    
    for path in db_paths_to_check:
        if os.path.exists(path):
            print(f"找到数据库文件: {path} (大小: {os.path.getsize(path)} 字节)")
    
    try:
        db = SessionLocal()
        company_service = CompanyService()
        diagnosis_service = DiagnosisService()
        
        # 检查企业
        companies = company_service.get_all_companies(db)
        print(f"\n数据库中的企业数量: {len(companies)}")
        for company in companies:
            print(f"  - {company.name} (ID: {company.id})")
            
            # 检查该企业的诊断记录
            reports = diagnosis_service.get_company_reports(db, company.id)
            print(f"    诊断记录数: {len(reports)}")
            
            for i, report in enumerate(reports, 1):
                create_time = report.created_at.strftime('%Y-%m-%d %H:%M:%S')
                print(f"      {i}. {create_time} - 评分: {report.overall_score:.1f}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"验证数据库记录失败: {e}")
        return False

if __name__ == "__main__":
    verify_database_records()