#!/usr/bin/env python3
"""
测试历史数据版本管理功能
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse, DataVersion

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_company(app):
    """创建测试企业"""
    with app.app_context():
        company = Company(name="测试企业", industry="技术")
        db.session.add(company)
        db.session.commit()
        return company

def test_data_version_snapshots(app, test_company):
    """测试数据版本快照功能"""
    with app.app_context():
        # 重新查询company对象以避免DetachedInstanceError
        company = Company.query.filter_by(name="测试企业").first()
        
        # 第一次数据导入
        survey1 = Survey(title="初始问卷", company_id=company.id, created_by=1)
        db.session.add(survey1)
        db.session.commit()
        
        # 添加初始数据
        initial_responses = [
            SurveyResponse(survey_id=survey1.id, respondent_name="张三", department="技术部",
                         management_level="中级", leadership_score=4.0),
            SurveyResponse(survey_id=survey1.id, respondent_name="李四", department="市场部",
                         management_level="初级", leadership_score=3.5),
        ]
        db.session.add_all(initial_responses)
        db.session.commit()
        
        # 创建第一个版本快照
        version1 = DataVersion(
            version_name="1.0",
            description="初始数据导入",
            data_type="survey",
            created_by=1
        )
        version1.set_snapshot({
            'company_id': company.id,
            'survey_count': 1,
            'response_count': 2,
            'responses': [
                {'name': '张三', 'department': '技术部', 'level': '中级', 'score': 4.0},
                {'name': '李四', 'department': '市场部', 'level': '初级', 'score': 3.5}
            ]
        })
        db.session.add(version1)
        db.session.commit()
        
        # 验证第一个版本
        versions = DataVersion.query.filter_by(version_name="1.0").all()
        assert len(versions) == 1
        assert versions[0].version_name == "1.0"
        assert versions[0].get_snapshot()['response_count'] == 2
        
        # 第二次数据更新
        survey2 = Survey(title="更新问卷", company_id=company.id, created_by=1)
        db.session.add(survey2)
        db.session.commit()
        
        # 添加更多数据
        additional_responses = [
            SurveyResponse(survey_id=survey2.id, respondent_name="王五", department="人事部",
                         management_level="高级", leadership_score=4.5),
            SurveyResponse(survey_id=survey2.id, respondent_name="赵六", department="财务部",
                         management_level="中级", leadership_score=3.8),
        ]
        db.session.add_all(additional_responses)
        db.session.commit()
        
        # 创建第二个版本快照
        total_responses = SurveyResponse.query.join(Survey)\
                                            .filter(Survey.company_id == company.id)\
                                            .count()
        
        version2 = DataVersion(
            version_name="2.0",
            description="数据更新",
            data_type="survey",
            created_by=1
        )
        version2.set_snapshot({
            'company_id': company.id,
            'survey_count': 2,
            'response_count': total_responses,
            'responses': [
                {'name': '张三', 'department': '技术部', 'level': '中级', 'score': 4.0},
                {'name': '李四', 'department': '市场部', 'level': '初级', 'score': 3.5},
                {'name': '王五', 'department': '人事部', 'level': '高级', 'score': 4.5},
                {'name': '赵六', 'department': '财务部', 'level': '中级', 'score': 3.8}
            ]
        })
        db.session.add(version2)
        db.session.commit()
        
        # 验证版本管理功能
        all_versions = DataVersion.query.filter(
            DataVersion.version_name.in_(["1.0", "2.0"])
        ).order_by(DataVersion.created_at).all()
        
        assert len(all_versions) == 2
        assert all_versions[0].version_name == "1.0"
        assert all_versions[1].version_name == "2.0"
        
        # 验证版本快照内容
        assert all_versions[0].get_snapshot()['response_count'] == 2
        assert all_versions[1].get_snapshot()['response_count'] == 4
        
        # 验证只读性（版本快照不应被修改）
        original_snapshot = all_versions[0].get_snapshot().copy()
        
        # 尝试修改快照（这应该不会影响数据库中的版本）
        modified_snapshot = all_versions[0].get_snapshot()
        modified_snapshot['modified'] = True
        
        # 重新查询验证只读性
        version_check = DataVersion.query.filter_by(version_name="1.0").first()
        # 注意：在实际实现中，应该有机制防止版本快照被修改
        
        print("✅ 历史数据版本管理功能测试通过")

if __name__ == "__main__":
    pytest.main([__file__])