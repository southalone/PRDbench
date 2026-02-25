#!/usr/bin/env python3
"""
测试自定义维度与指标功能
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import SkillDimension, DimensionIndicator

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_add_custom_dimension(app):
    """测试添加自定义技能维度功能"""
    with app.app_context():
        # 添加自定义维度
        custom_dimension = SkillDimension(
            name="沟通能力",
            description="评估管理者的口头表达、书面沟通、倾听技巧和跨文化交流能力",
            category="communication",
            is_preset=False
        )
        
        db.session.add(custom_dimension)
        db.session.commit()
        
        # 验证维度已添加
        saved_dimension = SkillDimension.query.filter_by(name="沟通能力").first()
        assert saved_dimension is not None
        assert saved_dimension.name == "沟通能力"
        assert saved_dimension.category == "communication"
        assert saved_dimension.is_preset == False
        
        # 验证可以查询自定义维度
        custom_dimensions = SkillDimension.query.filter_by(is_preset=False).all()
        assert len(custom_dimensions) == 1
        assert custom_dimensions[0].name == "沟通能力"
        
        print("✅ 自定义技能维度添加功能测试通过")

def test_add_dimension_indicators(app):
    """测试为维度添加指标和权重功能"""
    with app.app_context():
        # 先创建自定义维度
        custom_dimension = SkillDimension(
            name="沟通能力",
            description="评估管理者的沟通技能",
            category="communication",
            is_preset=False
        )
        db.session.add(custom_dimension)
        db.session.commit()
        
        # 为维度添加指标
        indicators = [
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="口头表达能力",
                description="清晰准确地表达想法和指令的能力",
                weight=0.3
            ),
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="书面沟通能力",
                description="撰写清晰、专业文档和邮件的能力",
                weight=0.25
            ),
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="倾听技巧",
                description="有效倾听他人意见和反馈的能力",
                weight=0.25
            ),
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="跨部门协调",
                description="与其他部门有效协作和沟通的能力",
                weight=0.2
            )
        ]
        
        db.session.add_all(indicators)
        db.session.commit()
        
        # 验证指标已添加
        saved_indicators = DimensionIndicator.query.filter_by(dimension_id=custom_dimension.id).all()
        assert len(saved_indicators) == 4
        
        # 验证权重总和
        total_weight = sum(indicator.weight for indicator in saved_indicators)
        assert abs(total_weight - 1.0) < 0.01  # 权重总和应该接近1.0
        
        # 验证具体指标
        indicator_names = [indicator.name for indicator in saved_indicators]
        expected_names = ["口头表达能力", "书面沟通能力", "倾听技巧", "跨部门协调"]
        
        for expected_name in expected_names:
            assert expected_name in indicator_names
        
        # 验证指标权重
        for indicator in saved_indicators:
            assert 0 < indicator.weight <= 1.0
            assert indicator.description is not None
        
        # 测试查询维度配置详情
        dimension_with_indicators = SkillDimension.query.filter_by(name="沟通能力").first()
        related_indicators = DimensionIndicator.query.filter_by(dimension_id=dimension_with_indicators.id).all()
        
        assert len(related_indicators) == 4
        
        print("✅ 维度指标和权重配置功能测试通过")
        print(f"   维度: {dimension_with_indicators.name}")
        print(f"   指标数量: {len(related_indicators)}")
        for indicator in related_indicators:
            print(f"   - {indicator.name}: {indicator.weight}")

if __name__ == "__main__":
    pytest.main([__file__])