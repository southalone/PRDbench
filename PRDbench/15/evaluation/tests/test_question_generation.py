import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from src.questions import generate_questions, Question

def test_all_dimensions_covered():
    question_types = {
        "单选题": 10,
        "多选题": 10,
        "判断题": 10,
        "情景分析题": 10,
    }
    questions, _ = generate_questions(question_types, "初级")
    questions.extend(generate_questions(question_types, "中级")[0])
    questions.extend(generate_questions(question_types, "高级")[0])
    dimensions = {q.dimension for q in questions}
    assert dimensions == {"专业知识", "问题解决", "团队协作", "沟通表达", "学习能力", "职业素养"}

def test_question_content_completeness():
    question_types = {"单选题": 5}
    questions, _ = generate_questions(question_types, "初级")
    for q in questions:
        assert q.answer is not None
        assert q.dimension is not None

def test_star_analysis_present():
    question_types = {"情景分析题": 1}
    questions, _ = generate_questions(question_types, "初级")
    assert questions[0].star_analysis is not None
