# -*- coding: utf-8 -*-
"""
诊断评分计算单元测试
"""

import pytest
import sys
import os
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from services.diagnosis_service import DiagnosisService
from models.database import Company


class TestDiagnosisCalculation:
    """诊断评分计算测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.diagnosis_service = DiagnosisService()
        
        # 创建测试用的企业对象
        self.test_company = Company(
            id=1,
            name="测试企业",
            establishment_date=datetime.strptime("2020-01-01", "%Y-%m-%d").date(),
            registered_capital=1000,
            company_type="有限责任公司",
            main_business="软件开发",
            industry="软件和信息技术服务业",
            employee_count=100,
            annual_revenue=5000,
            annual_profit=500,
            asset_liability_ratio=0.4,
            patent_count=5,
            copyright_count=3,
            rd_investment=750,
            rd_revenue_ratio=0.15,
            rd_personnel_ratio=0.3,
            innovation_achievements="获得多项软件著作权",
            internal_control_score=4,
            financial_standard_score=4,
            compliance_training_score=3,
            employment_compliance_score=4,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_funding_gap_score_excellent(self):
        """测试资金缺口评分 - 优秀情况"""
        # 设置优秀的财务状况
        company = self.test_company
        company.asset_liability_ratio = 0.3  # 低负债率
        company.annual_profit = 1000  # 高利润
        company.annual_revenue = 5000
        
        score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert score >= 4.0
        assert score <= 5.0
    
    def test_funding_gap_score_poor(self):
        """测试资金缺口评分 - 较差情况"""
        company = self.test_company
        company.asset_liability_ratio = 0.9  # 高负债率
        company.annual_profit = -100  # 亏损
        
        score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert score <= 2.0
        assert score >= 1.0
    
    def test_debt_capacity_score_excellent(self):
        """测试偿债能力评分 - 优秀情况"""
        company = self.test_company
        company.asset_liability_ratio = 0.2  # 低负债率
        company.annual_profit = 800  # 高利润
        company.annual_revenue = 5000
        company.registered_capital = 500  # 充足资本
        
        score = self.diagnosis_service._calculate_debt_capacity_score(company)
        assert score >= 4.0
        assert score <= 5.0
    
    def test_debt_capacity_score_poor(self):
        """测试偿债能力评分 - 较差情况"""
        company = self.test_company
        company.asset_liability_ratio = 0.8  # 高负债率
        company.annual_profit = -200  # 亏损
        company.registered_capital = 50  # 资本不足
        
        score = self.diagnosis_service._calculate_debt_capacity_score(company)
        assert score <= 2.5
        assert score >= 1.0
    
    def test_innovation_score_excellent(self):
        """测试创新能力评分 - 优秀情况"""
        company = self.test_company
        company.patent_count = 15  # 大量专利
        company.copyright_count = 8
        company.rd_revenue_ratio = 0.20  # 高研发投入比
        company.rd_personnel_ratio = 0.4  # 高研发人员比
        company.innovation_achievements = "多项重大技术突破"
        
        score = self.diagnosis_service._calculate_innovation_score(company)
        assert score >= 4.5
        assert score <= 5.0
    
    def test_innovation_score_poor(self):
        """测试创新能力评分 - 较差情况"""
        company = self.test_company
        company.patent_count = 0  # 无专利
        company.copyright_count = 0
        company.rd_revenue_ratio = 0.01  # 低研发投入
        company.rd_personnel_ratio = 0.05  # 低研发人员比
        company.innovation_achievements = None
        
        score = self.diagnosis_service._calculate_innovation_score(company)
        assert score <= 2.0
        assert score >= 1.0
    
    def test_management_score_calculation(self):
        """测试管理规范性评分计算"""
        company = self.test_company
        company.internal_control_score = 4
        company.financial_standard_score = 3
        company.compliance_training_score = 5
        company.employment_compliance_score = 2
        
        score = self.diagnosis_service._calculate_management_score(company)
        expected_score = (4 + 3 + 5 + 2) / 4
        assert score == expected_score
        assert score == 3.5
    
    def test_score_boundaries(self):
        """测试评分边界值"""
        company = self.test_company
        
        # 测试最低分
        company.asset_liability_ratio = 1.0
        company.annual_profit = -1000
        funding_score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert funding_score >= 1.0
        
        # 测试最高分
        company.asset_liability_ratio = 0.1
        company.annual_profit = 2000
        funding_score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert funding_score <= 5.0
    
    def test_innovation_score_incremental(self):
        """测试创新能力评分递增逻辑"""
        company = self.test_company
        
        # 基础分数
        company.patent_count = 0
        company.copyright_count = 0
        company.rd_revenue_ratio = 0.0
        company.rd_personnel_ratio = 0.0
        company.innovation_achievements = None
        base_score = self.diagnosis_service._calculate_innovation_score(company)
        assert base_score == 1.0
        
        # 增加专利后分数应提高
        company.patent_count = 3
        company.copyright_count = 2
        higher_score = self.diagnosis_service._calculate_innovation_score(company)
        assert higher_score > base_score
        
        # 增加研发投入后分数应进一步提高
        company.rd_revenue_ratio = 0.12
        even_higher_score = self.diagnosis_service._calculate_innovation_score(company)
        assert even_higher_score > higher_score


if __name__ == "__main__":
    pytest.main([__file__])