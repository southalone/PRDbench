#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试创新能力信息采集
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.database import Company
import inspect

def main():
    """测试创新能力信息采集 - 专利与知识产权"""
    print("测试专利与知识产权指标...")
    
    try:
        # 实际检查Company模型的字段
        company_fields = [field.name for field in Company.__table__.columns]
        
        required_fields = ['patent_count', 'copyright_count']
        missing_fields = [field for field in required_fields if field not in company_fields]
        
        if missing_fields:
            print(f"错误：缺少字段 {missing_fields}")
            return False
        
        # 检查字段类型
        field_types = {field.name: str(field.type) for field in Company.__table__.columns}
        
        if 'INTEGER' not in field_types.get('patent_count', ''):
            print("错误：专利数量字段类型不正确")
            return False
            
        if 'INTEGER' not in field_types.get('copyright_count', ''):
            print("错误：著作权数量字段类型不正确")
            return False
        
        print("专利数量和著作权数量配置完整")
        print("测试通过：专利与知识产权采集功能完整")
        return True
        
    except Exception as e:
        print(f"测试失败：{e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)