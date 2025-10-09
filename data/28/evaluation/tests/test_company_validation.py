# -*- coding: utf-8 -*-
"""
企业数据验证单元测试
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from services.company_service import CompanyService


class TestCompanyValidation:
    """企业数据验证测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.company_service = CompanyService()
        
        # 基础有效数据
        self.valid_data = {
            'name': '测试企业',
            'establishment_date': '2020-01-01',
            'registered_capital': 100,
            'company_type': '有限责任公司',
            'main_business': '软件开发', 
            'industry': '软件和信息技术服务业',
            'employee_count': 50,
            'annual_revenue': 1000,
            'annual_profit': 100,
            'asset_liability_ratio': 0.6,
            'internal_control_score': 4,
            'financial_standard_score': 4,
            'compliance_training_score': 3,
            'employment_compliance_score': 4
        }
    
    def test_valid_numeric_fields(self):
        """测试有效数值字段验证"""
        is_valid, message = self.company_service.validate_company_data(self.valid_data)
        assert is_valid == True
        assert message == "验证通过"
    
    def test_negative_registered_capital(self):
        """测试注册资本为负数"""
        invalid_data = self.valid_data.copy()
        invalid_data['registered_capital'] = -100
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "registered_capital 不能为负数" in message
    
    def test_negative_employee_count(self):
        """测试员工数量为负数"""
        invalid_data = self.valid_data.copy()
        invalid_data['employee_count'] = -5
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "employee_count 不能为负数" in message
    
    def test_negative_annual_revenue(self):
        """测试年度营收为负数"""
        invalid_data = self.valid_data.copy()
        invalid_data['annual_revenue'] = -1000
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "annual_revenue 不能为负数" in message
    
    def test_negative_annual_profit(self):
        """测试年度利润为负数"""
        invalid_data = self.valid_data.copy()
        invalid_data['annual_profit'] = -100
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "annual_profit 不能为负数" in message
    
    def test_invalid_ratio_field_above_one(self):
        """测试资产负债率大于1"""
        invalid_data = self.valid_data.copy()
        invalid_data['asset_liability_ratio'] = 1.5
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "asset_liability_ratio 必须在0-1之间" in message
    
    def test_invalid_ratio_field_below_zero(self):
        """测试资产负债率小于0"""
        invalid_data = self.valid_data.copy()
        invalid_data['asset_liability_ratio'] = -0.1
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "asset_liability_ratio 必须在0-1之间" in message
    
    def test_invalid_score_field_above_five(self):
        """测试评分字段大于5"""
        invalid_data = self.valid_data.copy()
        invalid_data['internal_control_score'] = 6
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "internal_control_score 必须在1-5之间" in message
    
    def test_invalid_score_field_below_one(self):
        """测试评分字段小于1"""
        invalid_data = self.valid_data.copy()
        invalid_data['financial_standard_score'] = 0
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "financial_standard_score 必须在1-5之间" in message
    
    def test_missing_required_field(self):
        """测试缺少必填字段"""
        invalid_data = self.valid_data.copy()
        del invalid_data['name']
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "必填字段 name 不能为空" in message
    
    def test_empty_string_field(self):
        """测试空字符串字段"""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = '   '
        is_valid, message = self.company_service.validate_company_data(invalid_data)
        assert is_valid == False
        assert "字段 name 不能为空字符串" in message


if __name__ == "__main__":
    pytest.main([__file__])