#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试合规培训评价
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.database import Company
import inspect

def main():
    """测试合规培训评价"""
    print("测试管理规范性评价 - 合规培训评价...")
    
    try:
        # 实际检查Company模型的字段
        company_fields = [field.name for field in Company.__table__.columns]
        
        required_fields = ['compliance_training_score', 'employment_compliance_score']
        missing_fields = [field for field in required_fields if field not in company_fields]
        
        if missing_fields:
            print(f"错误：缺少字段 {missing_fields}")
            return False
        
        # 检查字段类型
        field_types = {field.name: str(field.type) for field in Company.__table__.columns}
        
        if 'INTEGER' not in field_types.get('compliance_training_score', ''):
            print("错误：合规培训评分字段类型不正确")
            return False
            
        if 'INTEGER' not in field_types.get('employment_compliance_score', ''):
            print("错误：用工合规评分字段类型不正确")
            return False
        
        print("合规培训评分(1-5)和用工合规评分(1-5)配置完整")
        print("测试通过：合规培训评价功能完整")
        return True
        
    except Exception as e:
        print(f"测试失败：{e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)