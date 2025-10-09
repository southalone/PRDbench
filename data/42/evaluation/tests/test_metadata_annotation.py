#!/usr/bin/env python3
"""
测试样本批量元数据标注功能
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse

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
        company = Company(name="测试企业", industry="技术")
        db.session.add(company)
        db.session.commit()
        
        # 创建测试问卷
        survey = Survey(title="测试问卷", company_id=company.id, created_by=1)
        db.session.add(survey)
        db.session.commit()
        
        # 创建测试回答数据
        responses = [
            SurveyResponse(survey_id=survey.id, respondent_name="张三", department="技术部", 
                         management_level="中级", leadership_score=4.0),
            SurveyResponse(survey_id=survey.id, respondent_name="李四", department="市场部", 
                         management_level="初级", leadership_score=3.5),
            SurveyResponse(survey_id=survey.id, respondent_name="王五", department="人事部", 
                         management_level="高级", leadership_score=4.5),
        ]
        
        db.session.add_all(responses)
        db.session.commit()
        
        return {
            'company': company,
            'survey': survey,
            'responses': responses
        }

def test_batch_metadata_annotation(app, sample_data):
    """测试批量元数据标注功能"""
    with app.app_context():
        # 重新查询survey对象以避免DetachedInstanceError
        survey = Survey.query.filter_by(title="测试问卷").first()
        
        # 获取样本数据
        responses = SurveyResponse.query.filter_by(survey_id=survey.id).all()
        
        # 模拟批量添加元数据标签
        metadata_tags = {
            'data_source': '来源A',
            'data_quality': '有效',
            'batch_id': 'BATCH_001',
            'validation_status': '已验证'
        }
        
        # 为所有样本添加元数据
        for response in responses:
            # 使用raw_data字段存储元数据
            current_raw_data = response.get_raw_data() or {}
            current_raw_data.update({'metadata': metadata_tags})
            response.set_raw_data(current_raw_data)
            # 确保对象被标记为已修改
            db.session.add(response)
        
        db.session.commit()
        
        # 验证元数据标注结果
        updated_responses = SurveyResponse.query.filter_by(survey_id=survey.id).all()
        
        for response in updated_responses:
            raw_data = response.get_raw_data()
            assert 'metadata' in raw_data
            assert raw_data['metadata']['data_source'] == '来源A'
            assert raw_data['metadata']['data_quality'] == '有效'
            assert raw_data['metadata']['batch_id'] == 'BATCH_001'
            assert raw_data['metadata']['validation_status'] == '已验证'
        
        # 测试按元数据筛选
        filtered_responses = []
        for response in updated_responses:
            raw_data = response.get_raw_data()
            if raw_data.get('metadata', {}).get('data_source') == '来源A':
                filtered_responses.append(response)
        
        assert len(filtered_responses) == 3
        
        print("✅ 批量元数据标注功能测试通过")

if __name__ == "__main__":
    pytest.main([__file__])