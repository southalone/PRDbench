"""
数据管理功能测试
"""
import pytest
import sys
import pandas as pd
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_manager import DataManager
from scale_manager import ScaleManager
from models import create_tables

@pytest.fixture
def setup_data_manager():
    """设置数据管理器"""
    create_tables()
    
    scale_manager = ScaleManager()
    data_manager = DataManager()
    
    # 创建默认量表
    scale_manager.create_default_scales()
    
    return data_manager, scale_manager

def test_create_participant(setup_data_manager):
    """测试创建被试者"""
    data_manager, scale_manager = setup_data_manager
    
    # 执行创建被试者
    participant = data_manager.create_participant(
        participant_id="TEST_P001",
        name="测试被试者",
        gender="男",
        age=20,
        grade="大二",
        major="心理学"
    )
    
    # 断言
    assert participant is not None, "被试者创建失败"
    assert participant.participant_id == "TEST_P001", "被试者ID不匹配"
    assert participant.name == "测试被试者", "被试者姓名不匹配"
    assert participant.gender == "男", "被试者性别不匹配"
    assert participant.age == 20, "被试者年龄不匹配"
    assert participant.grade == "大二", "被试者年级不匹配"
    assert participant.major == "心理学", "被试者专业不匹配"

def test_create_response(setup_data_manager):
    """测试创建问卷回答"""
    data_manager, scale_manager = setup_data_manager
    
    # 先创建被试者
    participant = data_manager.create_participant(
        participant_id="TEST_R001",
        name="回答测试者",
        gender="女",
        age=19,
        grade="大一",
        major="教育学"
    )
    
    # 创建问卷回答
    responses_data = {
        "1": 5, "2": 3, "3": 6, "4": 2,
        "5": 5, "6": 4, "7": 3, "8": 5
    }
    
    response = data_manager.create_response(
        participant_id="TEST_R001",
        scale_id=1,
        responses_data=responses_data
    )
    
    # 断言
    assert response is not None, "问卷回答创建失败"
    assert response.participant_id == participant.id, "被试者ID关联错误"
    assert response.scale_id == 1, "量表ID不匹配"
    assert response.responses_data == responses_data, "回答数据不匹配"
    assert response.total_score is not None, "总分计算失败"
    assert response.dimension_scores is not None, "维度得分计算失败"

def test_data_grouping(setup_data_manager):
    """测试数据分组功能"""
    data_manager, scale_manager = setup_data_manager
    
    # 创建多个被试者用于分组测试
    participants_data = [
        {'participant_id': 'GROUP_001', 'gender': '男', 'grade': '大一', 'major': '心理学'},
        {'participant_id': 'GROUP_002', 'gender': '女', 'grade': '大一', 'major': '教育学'},
        {'participant_id': 'GROUP_003', 'gender': '男', 'grade': '大二', 'major': '心理学'},
        {'participant_id': 'GROUP_004', 'gender': '女', 'grade': '大二', 'major': '教育学'},
        {'participant_id': 'GROUP_005', 'gender': '男', 'grade': '大三', 'major': '心理学'},
    ]
    
    for p_data in participants_data:
        data_manager.create_participant(**p_data)
    
    # 测试按性别分组
    gender_groups = data_manager.list_participants(gender='男')
    assert len(gender_groups) == 3, f"男性被试者数量不匹配，期望: 3, 实际: {len(gender_groups)}"
    
    female_groups = data_manager.list_participants(gender='女')
    assert len(female_groups) == 2, f"女性被试者数量不匹配，期望: 2, 实际: {len(female_groups)}"
    
    # 测试按年级分组
    grade1_groups = data_manager.list_participants(grade='大一')
    assert len(grade1_groups) == 2, f"大一被试者数量不匹配，期望: 2, 实际: {len(grade1_groups)}"
    
    grade2_groups = data_manager.list_participants(grade='大二')
    assert len(grade2_groups) == 2, f"大二被试者数量不匹配，期望: 2, 实际: {len(grade2_groups)}"
    
    # 测试按专业分组
    psychology_groups = data_manager.list_participants(major='心理学')
    assert len(psychology_groups) == 3, f"心理学专业被试者数量不匹配，期望: 3, 实际: {len(psychology_groups)}"
    
    education_groups = data_manager.list_participants(major='教育学')
    assert len(education_groups) == 2, f"教育学专业被试者数量不匹配，期望: 2, 实际: {len(education_groups)}"

def test_data_summary(setup_data_manager):
    """测试数据摘要功能"""
    data_manager, scale_manager = setup_data_manager
    
    # 创建测试数据
    participants_data = [
        {'participant_id': 'SUMMARY_001', 'gender': '男', 'grade': '大一'},
        {'participant_id': 'SUMMARY_002', 'gender': '女', 'grade': '大二'},
        {'participant_id': 'SUMMARY_003', 'gender': '男', 'grade': '大三'},
    ]
    
    for p_data in participants_data:
        data_manager.create_participant(**p_data)
    
    # 创建问卷回答
    for i, p_data in enumerate(participants_data):
        responses_data = {str(j): (i % 5) + 3 for j in range(1, 9)}  # 生成3-7的回答
        data_manager.create_response(
            participant_id=p_data['participant_id'],
            scale_id=1,
            responses_data=responses_data
        )
    
    # 测试整体数据摘要
    summary = data_manager.get_data_summary()
    
    # 断言
    assert 'error' not in summary, f"数据摘要获取失败: {summary.get('error', '')}"
    assert 'total_participants' in summary, "缺少总参与人数"
    assert 'total_responses' in summary, "缺少总回答数"
    assert 'gender_distribution' in summary, "缺少性别分布"
    assert 'grade_distribution' in summary, "缺少年级分布"
    
    # 验证数值合理性
    assert summary['total_participants'] >= 3, "总参与人数应至少为3"
    assert summary['total_responses'] >= 3, "总回答数应至少为3"
    
    # 测试特定量表的数据摘要
    scale_summary = data_manager.get_data_summary(scale_id=1)
    
    assert 'responses_count' in scale_summary, "缺少量表回答数"
    assert 'completion_rate' in scale_summary, "缺少完成率"
    assert scale_summary['responses_count'] >= 3, "量表回答数应至少为3"
    assert 0 <= scale_summary['completion_rate'] <= 100, "完成率应在0-100之间"

def test_data_anomaly_detection(setup_data_manager):
    """测试数据异常检测"""
    data_manager, scale_manager = setup_data_manager
    
    # 创建包含异常的测试数据
    participants_data = [
        {'participant_id': 'ANOMALY_001', 'gender': '男', 'grade': '大一'},
        {'participant_id': 'ANOMALY_002', 'gender': '女', 'grade': '大二'},
        {'participant_id': 'ANOMALY_003', 'gender': '男', 'grade': '大三'},
    ]
    
    for p_data in participants_data:
        data_manager.create_participant(**p_data)
    
    # 创建正常回答
    normal_responses = {str(j): j % 5 + 2 for j in range(1, 9)}
    data_manager.create_response("ANOMALY_001", 1, normal_responses)
    
    # 创建极端值回答（全选7）
    extreme_responses = {str(j): 7 for j in range(1, 9)}
    data_manager.create_response("ANOMALY_002", 1, extreme_responses)
    
    # 创建缺失回答（只回答部分条目）
    missing_responses = {str(j): j % 5 + 2 for j in range(1, 6)}  # 只回答前5个条目
    data_manager.create_response("ANOMALY_003", 1, missing_responses)
    
    # 执行异常检测
    anomalies = data_manager.detect_data_anomalies(scale_id=1)
    
    # 断言
    assert 'error' not in anomalies, f"异常检测失败: {anomalies.get('error', '')}"
    assert 'missing_responses' in anomalies, "缺少缺失回答检测"
    assert 'extreme_values' in anomalies, "缺少极端值检测"
    assert 'duplicate_responses' in anomalies, "缺少重复回答检测"
    
    # 验证检测结果
    # 应该检测到极端值（全选7）
    extreme_values = anomalies['extreme_values']
    assert len(extreme_values) >= 1, "应该检测到至少1个极端值"
    
    # 验证极端值检测结果的结构
    if extreme_values:
        extreme_item = extreme_values[0]
        assert 'participant_id' in extreme_item, "极端值检测结果缺少被试者ID"
        assert 'pattern' in extreme_item, "极端值检测结果缺少模式描述"

def test_import_export_participants(setup_data_manager):
    """测试被试者数据导入导出"""
    data_manager, scale_manager = setup_data_manager
    
    # 创建测试CSV文件
    test_data = {
        'participant_id': ['IMPORT_001', 'IMPORT_002', 'IMPORT_003'],
        'name': ['导入测试1', '导入测试2', '导入测试3'],
        'gender': ['男', '女', '男'],
        'age': [20, 19, 21],
        'grade': ['大二', '大一', '大三'],
        'major': ['心理学', '教育学', '心理学']
    }
    
    test_file = Path("evaluation/temp_participants.csv")
    df = pd.DataFrame(test_data)
    df.to_csv(test_file, index=False, encoding='utf-8')
    
    try:
        # 测试导入
        participants = data_manager.import_participants_from_csv(test_file)
        
        # 断言
        assert len(participants) == 3, f"导入的被试者数量不匹配，期望: 3, 实际: {len(participants)}"
        
        # 验证导入的数据
        for i, participant in enumerate(participants):
            assert participant.participant_id == test_data['participant_id'][i], f"第{i+1}个被试者ID不匹配"
            assert participant.name == test_data['name'][i], f"第{i+1}个被试者姓名不匹配"
            assert participant.gender == test_data['gender'][i], f"第{i+1}个被试者性别不匹配"
        
        # 测试导出
        export_file = Path("evaluation/temp_exported_participants.csv")
        success = data_manager.export_participants_to_csv(export_file)
        
        assert success == True, "被试者数据导出失败"
        assert export_file.exists(), "导出的被试者文件不存在"
        
        # 验证导出内容
        exported_df = pd.read_csv(export_file)
        assert len(exported_df) >= 3, "导出的被试者数量不足"
        assert 'participant_id' in exported_df.columns, "导出文件缺少participant_id列"
        assert 'gender' in exported_df.columns, "导出文件缺少gender列"
        
        # 清理导出文件
        if export_file.exists():
            export_file.unlink()
            
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()

def test_import_export_responses(setup_data_manager):
    """测试问卷回答数据导入导出"""
    data_manager, scale_manager = setup_data_manager
    
    # 先创建被试者
    participants = [
        {'participant_id': 'RESP_001', 'gender': '男', 'grade': '大一'},
        {'participant_id': 'RESP_002', 'gender': '女', 'grade': '大二'},
    ]
    
    for p_data in participants:
        data_manager.create_participant(**p_data)
    
    # 创建测试回答CSV文件
    test_data = {
        'participant_id': ['RESP_001', 'RESP_002'],
        'item_1': [5, 6],
        'item_2': [3, 2],
        'item_3': [6, 7],
        'item_4': [2, 1],
        'item_5': [5, 6],
        'item_6': [4, 5],
        'item_7': [3, 2],
        'item_8': [5, 6]
    }
    
    test_file = Path("evaluation/temp_responses.csv")
    df = pd.DataFrame(test_data)
    df.to_csv(test_file, index=False, encoding='utf-8')
    
    try:
        # 测试导入
        responses = data_manager.import_responses_from_csv(test_file, scale_id=1)
        
        # 断言
        assert len(responses) == 2, f"导入的回答数量不匹配，期望: 2, 实际: {len(responses)}"
        
        # 验证回答数据
        for response in responses:
            assert response.scale_id == 1, "量表ID不匹配"
            assert response.total_score is not None, "总分未计算"
            assert response.dimension_scores is not None, "维度得分未计算"
            assert len(response.responses_data) == 8, "回答条目数量不匹配"
        
        # 测试导出
        export_file = Path("evaluation/temp_exported_responses.csv")
        success = data_manager.export_responses_to_csv(export_file, scale_id=1)
        
        assert success == True, "问卷回答导出失败"
        assert export_file.exists(), "导出的回答文件不存在"
        
        # 验证导出内容
        exported_df = pd.read_csv(export_file)
        assert len(exported_df) >= 2, "导出的回答数量不足"
        assert 'participant_id' in exported_df.columns, "导出文件缺少participant_id列"
        assert 'total_score' in exported_df.columns, "导出文件缺少total_score列"
        
        # 清理导出文件
        if export_file.exists():
            export_file.unlink()
            
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()

def test_get_response_data(setup_data_manager):
    """测试获取回答数据DataFrame"""
    data_manager, scale_manager = setup_data_manager
    
    # 创建测试数据
    participant = data_manager.create_participant(
        participant_id="DATA_001",
        gender="男",
        age=20,
        grade="大二",
        major="心理学"
    )
    
    responses_data = {str(i): i % 5 + 3 for i in range(1, 9)}
    data_manager.create_response("DATA_001", 1, responses_data)
    
    # 获取数据DataFrame
    df = data_manager.get_response_data(scale_id=1, include_demographics=True)
    
    # 断言
    assert not df.empty, "获取的数据DataFrame为空"
    assert 'participant_id' in df.columns, "缺少participant_id列"
    assert 'total_score' in df.columns, "缺少total_score列"
    assert 'gender' in df.columns, "缺少gender列"
    assert 'grade' in df.columns, "缺少grade列"
    
    # 验证条目列
    item_columns = [col for col in df.columns if col.startswith('item_')]
    assert len(item_columns) >= 8, f"条目列数量不足，期望至少8个，实际: {len(item_columns)}"
    
    # 验证数据内容
    assert len(df) >= 1, "数据行数不足"
    first_row = df.iloc[0]
    assert first_row['participant_id'] == "DATA_001", "被试者ID不匹配"
    assert first_row['gender'] == "男", "性别信息不匹配"

def test_data_validation():
    """测试数据验证功能"""
    data_manager = DataManager()
    
    # 测试重复被试者ID
    data_manager.create_participant(participant_id="DUPLICATE_001", name="第一个")
    duplicate_participant = data_manager.create_participant(participant_id="DUPLICATE_001", name="第二个")
    
    # 系统应该返回已存在的被试者，而不是创建新的
    assert duplicate_participant.name == "第一个", "重复ID处理不正确"
    
    # 测试无效的问卷回答
    with pytest.raises(Exception):
        # 尝试为不存在的被试者创建回答
        data_manager.create_response("NONEXISTENT", 1, {"1": 5})
    
    with pytest.raises(Exception):
        # 尝试为不存在的量表创建回答
        data_manager.create_response("DUPLICATE_001", 999, {"1": 5})

def test_score_calculation(setup_data_manager):
    """测试得分计算功能"""
    data_manager, scale_manager = setup_data_manager
    
    # 创建被试者
    participant = data_manager.create_participant(
        participant_id="SCORE_001",
        gender="女",
        age=19
    )
    
    # 创建包含反向计分的回答
    responses_data = {
        "1": 7,  # 正向条目，高分
        "2": 1,  # 反向条目，低分（实际高分）
        "3": 6,  # 正向条目
        "4": 2,  # 反向条目（实际高分）
        "5": 5,  # 正向条目
        "6": 4,  # 正向条目
        "7": 3,  # 反向条目（实际中等分）
        "8": 6   # 正向条目
    }
    
    response = data_manager.create_response("SCORE_001", 1, responses_data)
    
    # 断言
    assert response.total_score is not None, "总分计算失败"
    assert response.dimension_scores is not None, "维度得分计算失败"
    assert isinstance(response.total_score, (int, float)), "总分应为数值类型"
    assert isinstance(response.dimension_scores, dict), "维度得分应为字典类型"
    
    # 验证得分范围合理性（假设7点量表）
    assert 1 <= response.total_score <= 7, f"总分超出合理范围: {response.total_score}"
    
    # 验证维度得分
    for dimension, score in response.dimension_scores.items():
        assert 1 <= score <= 7, f"维度{dimension}得分超出合理范围: {score}"