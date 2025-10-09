import sys
import os
import pandas as pd
import pytest

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from tta.processor import process_data


def test_feedback_simplification():
    """
    测试反馈列文本简化功能是否按预期工作。
    """
    # 准备 (Arrange)
    data = {
        '任务单号': ['TASK-001'],
        '任务名称': ['测试任务'],
        '测试项目': ['项目A'],
        '设备时长': [1.0],
        '测试状态': ['成功'],
        '测试类型': ['类型1'],
        '测试项目情况【反馈列】': ['试验暂无异常']
    }
    input_df = pd.DataFrame(data)

    # 执行 (Act)
    result_df = process_data(input_df)

    # 断言 (Assert)
    assert not result_df.empty
    assert '测试项目情况【反馈列】' in result_df.columns
    assert result_df.loc[0, '测试项目情况【反馈列】'] == '暂无异常'


def test_error_code_extraction():
    """
    测试从反馈列中提取异常标识的功能。
    """
    # 准备 (Arrange)
    data = {
        '任务单号': ['TASK-002'],
        '任务名称': ['另一个测试'],
        '测试项目': ['项目B'],
        '设备时长': [2.0],
        '测试状态': ['失败'],
        '测试类型': ['类型2'],
        '测试项目情况【反馈列】': ['Error-404，设备重启']
    }
    input_df = pd.DataFrame(data)

    # 执行 (Act)
    result_df = process_data(input_df)

    # 断言 (Assert)
    assert '异常标识' in result_df.columns
    assert result_df.loc[0, '异常标识'] == 'Error-404,'