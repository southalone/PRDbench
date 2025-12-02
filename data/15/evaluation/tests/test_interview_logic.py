import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import os
from src.main import generate_radar_chart, generate_report

# Mocking the console and other dependencies if necessary
class MockConsole:
    def print(self, text):
        pass

@pytest.fixture
def mock_console(monkeypatch):
    monkeypatch.setattr('src.main.console', MockConsole())

def test_radar_chart_generation(mock_console):
    scores = {
        "专业知识": 4.5,
        "问题解决": 3.8,
        "团队协作": 4.2,
        "沟通表达": 4.0,
        "学习能力": 4.8,
        "职业素养": 4.6
    }
    generate_radar_chart(scores)
    assert os.path.exists("competency_radar_chart.png")
    os.remove("competency_radar_chart.png")

def test_report_contains_suggestions(capsys):
    scores = {
        "专业知识": 2.5,
        "问题解决": 3.0,
        "团队协作": 4.0,
        "沟通表达": 3.5,
        "学习能力": 4.5,
        "职业素养": 4.0
    }
    generate_report(scores, 120)  # Add a mock total_time
    captured = capsys.readouterr()
    # This is a simple check. A more robust test would check for specific suggestions.
    assert "综合评价报告" in captured.out
