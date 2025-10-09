import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from src.career_planning import generate_development_plan

def test_development_plan_core_skills():
    plan = generate_development_plan("技术/职能型 (Technical/Functional Competence)")
    assert "核心能力提升建议" in plan
    assert "深化专业知识" in plan

def test_development_plan_resources():
    plan = generate_development_plan("管理型 (General Managerial Competence)")
    assert "推荐学习资源" in plan
    assert "在线课程平台" in plan

def test_development_plan_goals():
    plan = generate_development_plan("创造/创业型 (Entrepreneurial Creativity)")
    assert "阶段性目标设定" in plan
    assert "短期 (1-3个月)" in plan
