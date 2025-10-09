#!/usr/bin/env python3
"""
测试样本多维度筛选功能
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse
from app.utils.data_processor import DataProcessor

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def sample_data(app):
    """创建测试样本数据"""
    with app.app_context():
        # 创建测试企业
        company1 = Company(name="测试企业A", industry="技术")
        company2 = Company(name="测试企业B", industry="金融")
        db.session.add_all([company1, company2])
        db.session.commit()
        
        # 创建测试问卷
        survey1 = Survey(title="测试问卷A", company_id=company1.id, created_by=1)
        survey2 = Survey(title="测试问卷B", company_id=company2.id, created_by=1)
        db.session.add_all([survey1, survey2])
        db.session.commit()
        
        # 创建测试回答数据
        responses = [
            # 企业A数据
            SurveyResponse(survey_id=survey1.id, respondent_name="张三", department="技术部", 
                         position="经理", management_level="中级", leadership_score=4.0),
            SurveyResponse(survey_id=survey1.id, respondent_name="李四", department="市场部", 
                         position="主管", management_level="初级", leadership_score=3.5),
            SurveyResponse(survey_id=survey1.id, respondent_name="王五", department="技术部", 
                         position="总监", management_level="高级", leadership_score=4.5),
            
            # 企业B数据
            SurveyResponse(survey_id=survey2.id, respondent_name="赵六", department="财务部", 
                         position="经理", management_level="中级", leadership_score=3.8),
            SurveyResponse(survey_id=survey2.id, respondent_name="钱七", department="人事部", 
                         position="主管", management_level="初级", leadership_score=3.2),
        ]
        
        db.session.add_all(responses)
        db.session.commit()
        
        return {
            'companies': [company1, company2],
            'surveys': [survey1, survey2],
            'responses': responses
        }

def test_multi_dimension_filtering(app, sample_data):
    """测试多维度样本筛选功能"""
    with app.app_context():
        data_processor = DataProcessor()
        
        # 重新查询企业对象以避免DetachedInstanceError
        company_a = Company.query.filter_by(name="测试企业A").first()
        
        # 测试按企业筛选
        company_a_responses = SurveyResponse.query.join(Survey)\
                                                 .filter(Survey.company_id == company_a.id)\
                                                 .all()
        assert len(company_a_responses) == 3
        
        # 测试按部门筛选
        tech_responses = SurveyResponse.query.filter_by(department="技术部").all()
        assert len(tech_responses) == 2
        
        # 测试按管理层级筛选
        senior_responses = SurveyResponse.query.filter_by(management_level="高级").all()
        assert len(senior_responses) == 1
        assert senior_responses[0].respondent_name == "王五"
        
        # 测试组合筛选：企业A + 技术部
        combined_responses = SurveyResponse.query.join(Survey)\
                                                .filter(Survey.company_id == company_a.id)\
                                                .filter(SurveyResponse.department == "技术部")\
                                                .all()
        assert len(combined_responses) == 2
        
        # 验证筛选结果的正确性
        names = [r.respondent_name for r in combined_responses]
        assert "张三" in names
        assert "王五" in names
        
        print("✅ 多维度样本筛选功能测试通过")

if __name__ == "__main__":
    pytest.main([__file__])