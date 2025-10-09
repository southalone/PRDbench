import pytest
from typer.testing import CliRunner
import os
import csv
from src.cli.data_cli import app
from src.database import SessionLocal
from src.models.questionnaire import Questionnaire, Question, Choice, QuestionType
from src.models.response import ResponseSession, Response

runner = CliRunner()

@pytest.fixture
def setup_test_data():
    """Fixture to set up test data for export testing."""
    # Import all models to ensure they're registered with Base
    from src.database import Base, engine
    from src.models.questionnaire import Questionnaire, Question, Choice, QuestionType
    from src.models.response import ResponseSession, Response
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create a test questionnaire
        q = Questionnaire(
            title="导出测试问卷",
            description="用于测试数据导出功能的问卷"
        )
        db.add(q)
        db.flush()

        # Add test questions
        q1 = Question(text="您的性别是？", module="个人信息", question_type=QuestionType.SINGLE_CHOICE, questionnaire_id=q.id)
        q2 = Question(text="您的满意度？", module="评价", question_type=QuestionType.SCALE, questionnaire_id=q.id)
        db.add_all([q1, q2])
        db.flush()

        # Add choices
        db.add(Choice(text="男", question_id=q1.id))
        db.add(Choice(text="女", question_id=q1.id))
        db.add(Choice(text="Scale Range: 1-5", question_id=q2.id))

        # Create test response sessions
        session1 = ResponseSession(questionnaire_id=q.id, collector="测试员A", location="测试地点A")
        session2 = ResponseSession(questionnaire_id=q.id, collector="测试员B", location="测试地点B")
        db.add_all([session1, session2])
        db.flush()

        # Add test responses
        responses = [
            Response(session_id=session1.id, question_id=q1.id, answer="男"),
            Response(session_id=session1.id, question_id=q2.id, answer="4"),
            Response(session_id=session2.id, question_id=q1.id, answer="女"),
            Response(session_id=session2.id, question_id=q2.id, answer="5"),
        ]
        db.add_all(responses)
        db.commit()
        
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


def test_export_data_to_csv(setup_test_data, tmp_path):
    """
    Test that the data export command creates a CSV file with correct content.
    """
    # Use temporary path for output
    output_file = tmp_path / "test_export.csv"
    
    # Run the export command
    result = runner.invoke(app, ["export", "--output-path", str(output_file)])
    
    # Assert command succeeded
    assert result.exit_code == 0, f"Command failed with output: {result.stdout}"
    assert "数据已成功导出到" in result.stdout
    
    # Assert file was created
    assert output_file.exists()
    
    # Verify CSV content
    with open(output_file, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # Check header (wide format: each question becomes a column)
        expected_header_start = [
            "session_id",
            "collector",
            "location",
            "session_created_at",
            "questionnaire_title"
        ]
        # The header should start with these fields, followed by question texts as columns
        assert header[:5] == expected_header_start
        assert "您的性别是？" in header
        assert "您的满意度？" in header
        
        # Check data rows (wide format: one row per session)
        rows = list(reader)
        assert len(rows) == 2  # 2 sessions, each as one row
        
        # Verify data content
        row1, row2 = rows
        assert "测试员A" in row1
        assert "测试员B" in row2
        assert "导出测试问卷" in row1  # questionnaire_title
        assert "导出测试问卷" in row2  # questionnaire_title