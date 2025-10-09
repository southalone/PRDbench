#!/usr/bin/env python3
"""
测试访谈文本手动录入功能
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Interview

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

def test_manual_interview_input(app):
    """测试手动录入访谈文本功能"""
    with app.app_context():
        # 创建测试企业
        company = Company(name="测试企业", industry="测试行业")
        db.session.add(company)
        db.session.commit()
        
        # 准备访谈文本
        interview_content = """
        访谈记录 - 管理技能评估
        
        访谈对象：测试经理
        职位：部门经理
        访谈时间：2024年1月15日
        
        问题1：您认为最重要的管理技能是什么？
        回答：我认为沟通能力最重要，能够有效地与团队成员交流，理解他们的需求和困难。
        
        问题2：在项目管理方面有什么经验？
        回答：我通常会制定详细的项目计划，设定明确的里程碑，并定期跟踪进度。
        
        总结：该经理在沟通和项目管理方面表现良好。
        """
        
        # 创建访谈记录
        interview = Interview(
            title="手动录入测试访谈",
            company_id=company.id,
            content=interview_content.strip(),
            interviewee_name="测试经理",
            interviewee_position="部门经理"
        )
        
        db.session.add(interview)
        db.session.commit()
        
        # 验证访谈记录已保存
        saved_interview = Interview.query.filter_by(title="手动录入测试访谈").first()
        assert saved_interview is not None
        assert saved_interview.content == interview_content.strip()
        assert saved_interview.interviewee_name == "测试经理"
        assert saved_interview.company_id == company.id
        
        print("✅ 访谈文本手动录入功能测试通过")

if __name__ == "__main__":
    pytest.main([__file__])