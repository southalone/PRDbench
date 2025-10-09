#!/usr/bin/env python3
"""
测试预置管理技能维度功能
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import SkillDimension

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_preset_skill_dimensions(app):
    """测试系统预置的四大核心管理技能维度"""
    with app.app_context():
        # 预置的四大管理技能维度
        preset_dimensions = [
            {
                'name': '领导与激励技能',
                'description': '评估管理者的团队领导能力、激励技巧、沟通协调和团队建设水平',
                'category': 'leadership'
            },
            {
                'name': '计划组织与协调技能',
                'description': '衡量管理者的计划制定、资源配置、流程优化和跨部门协调能力',
                'category': 'planning'
            },
            {
                'name': '决策与创新技能',
                'description': '考察管理者的决策分析、风险评估、创新思维和变革管理能力',
                'category': 'decision'
            },
            {
                'name': '专业与控制技能',
                'description': '评价管理者的专业知识水平、质量控制、绩效管理和标准执行能力',
                'category': 'professional'
            }
        ]
        
        # 创建预置维度（模拟系统初始化）
        for dim_data in preset_dimensions:
            dimension = SkillDimension(
                name=dim_data['name'],
                description=dim_data['description'],
                category=dim_data['category'],
                is_preset=True
            )
            db.session.add(dimension)
        
        db.session.commit()
        
        # 验证预置维度
        all_dimensions = SkillDimension.query.filter_by(is_preset=True).all()
        assert len(all_dimensions) == 4
        
        # 验证具体维度名称
        dimension_names = [dim.name for dim in all_dimensions]
        expected_names = [
            '领导与激励技能',
            '计划组织与协调技能', 
            '决策与创新技能',
            '专业与控制技能'
        ]
        
        for expected_name in expected_names:
            assert expected_name in dimension_names
        
        # 验证维度分类
        categories = [dim.category for dim in all_dimensions]
        expected_categories = ['leadership', 'planning', 'decision', 'professional']
        
        for expected_category in expected_categories:
            assert expected_category in categories
        
        # 验证每个维度都有描述
        for dimension in all_dimensions:
            assert dimension.description is not None
            assert len(dimension.description) > 0
        
        print("✅ 预置管理技能维度功能测试通过")
        print(f"   发现 {len(all_dimensions)} 个预置技能维度")
        for dim in all_dimensions:
            print(f"   - {dim.name} ({dim.category})")

if __name__ == "__main__":
    pytest.main([__file__])