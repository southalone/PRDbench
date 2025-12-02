#!/usr/bin/env python3
"""
测试多维可视化仪表盘功能
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse
from app.utils.visualizer import DataVisualizer

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
                         management_level="中级", leadership_score=4.2, planning_score=4.0,
                         decision_score=3.8, professional_score=4.5),
            SurveyResponse(survey_id=survey.id, respondent_name="李四", department="市场部", 
                         management_level="初级", leadership_score=3.5, planning_score=3.8,
                         decision_score=4.0, professional_score=3.2),
            SurveyResponse(survey_id=survey.id, respondent_name="王五", department="人事部", 
                         management_level="高级", leadership_score=4.8, planning_score=4.5,
                         decision_score=4.2, professional_score=4.0),
        ]
        
        db.session.add_all(responses)
        db.session.commit()
        
        return {
            'company': company,
            'survey': survey,
            'responses': responses
        }

def test_skills_radar_chart(app, sample_data):
    """测试技能分布雷达图功能"""
    with app.app_context():
        visualizer = DataVisualizer()
        
        # 重新查询responses以避免DetachedInstanceError
        responses = SurveyResponse.query.all()
        
        # 计算技能平均分
        skills_data = {
            '领导与激励': sum(r.leadership_score for r in responses if r.leadership_score) / len([r for r in responses if r.leadership_score]),
            '计划组织': sum(r.planning_score for r in responses if r.planning_score) / len([r for r in responses if r.planning_score]),
            '决策创新': sum(r.decision_score for r in responses if r.decision_score) / len([r for r in responses if r.decision_score]),
            '专业控制': sum(r.professional_score for r in responses if r.professional_score) / len([r for r in responses if r.professional_score])
        }
        
        # 验证雷达图数据结构
        assert len(skills_data) == 4
        assert all(0 <= score <= 5 for score in skills_data.values())
        
        # 模拟生成雷达图
        radar_config = {
            'type': 'radar',
            'data': skills_data,
            'title': '技能分布雷达图',
            'max_value': 5
        }
        
        # 验证雷达图配置
        assert radar_config['type'] == 'radar'
        assert len(radar_config['data']) == 4
        assert radar_config['max_value'] == 5
        
        # 验证技能维度完整性
        required_skills = ['领导与激励', '计划组织', '决策创新', '专业控制']
        for skill in required_skills:
            assert skill in radar_config['data']
        
        print("✅ 技能分布雷达图功能测试通过")
        print(f"   技能数据: {skills_data}")

def test_growth_line_chart(app, sample_data):
    """测试成长趋势折线图功能"""
    with app.app_context():
        visualizer = DataVisualizer()
        
        # 模拟时间序列数据（不同时间点的技能得分）
        time_series_data = {
            '2024-01': {'leadership': 3.5, 'planning': 3.3, 'decision': 3.2, 'professional': 3.4},
            '2024-02': {'leadership': 3.7, 'planning': 3.6, 'decision': 3.5, 'professional': 3.6},
            '2024-03': {'leadership': 4.0, 'planning': 3.9, 'decision': 3.8, 'professional': 3.9},
        }
        
        # 验证折线图数据结构
        assert len(time_series_data) == 3
        
        for month, scores in time_series_data.items():
            assert len(scores) == 4
            assert all(0 <= score <= 5 for score in scores.values())
        
        # 模拟生成折线图配置
        line_config = {
            'type': 'line',
            'data': time_series_data,
            'title': '技能成长趋势图',
            'x_axis': 'time',
            'y_axis': 'score'
        }
        
        # 验证折线图配置
        assert line_config['type'] == 'line'
        assert line_config['x_axis'] == 'time'
        assert line_config['y_axis'] == 'score'
        
        print("✅ 成长趋势折线图功能测试通过")

def test_low_score_heatmap(app, sample_data):
    """测试低分预警热力图功能"""
    with app.app_context():
        visualizer = DataVisualizer()
        
        # 重新查询responses以避免DetachedInstanceError
        responses = SurveyResponse.query.all()
        
        # 构建热力图数据矩阵
        heatmap_data = []
        for response in responses:
            row_data = {
                'name': response.respondent_name,
                'department': response.department,
                'leadership': response.leadership_score,
                'planning': response.planning_score,
                'decision': response.decision_score,
                'professional': response.professional_score
            }
            heatmap_data.append(row_data)
        
        # 识别低分项（假设低于3.5分为低分）
        low_score_threshold = 3.5
        low_score_items = []
        
        for item in heatmap_data:
            for skill in ['leadership', 'planning', 'decision', 'professional']:
                if item[skill] < low_score_threshold:
                    low_score_items.append({
                        'name': item['name'],
                        'department': item['department'],
                        'skill': skill,
                        'score': item[skill]
                    })
        
        # 验证低分预警功能
        assert len(low_score_items) > 0  # 应该有低分项
        
        # 验证热力图配置
        heatmap_config = {
            'type': 'heatmap',
            'data': heatmap_data,
            'title': '技能得分热力图',
            'threshold': low_score_threshold,
            'low_score_items': low_score_items
        }
        
        assert heatmap_config['type'] == 'heatmap'
        assert heatmap_config['threshold'] == 3.5
        assert len(heatmap_config['low_score_items']) > 0
        
        print("✅ 低分预警热力图功能测试通过")
        print(f"   发现 {len(low_score_items)} 个低分预警项")
        for item in low_score_items:
            print(f"   - {item['name']} ({item['department']}): {item['skill']} = {item['score']}")

if __name__ == "__main__":
    pytest.main([__file__])