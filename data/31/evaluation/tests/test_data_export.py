"""
数据导出功能测试
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
def setup_export_test():
    """设置数据导出测试环境"""
    create_tables()
    
    scale_manager = ScaleManager()
    data_manager = DataManager()
    
    # 创建默认量表
    scale_manager.create_default_scales()
    
    # 创建测试数据
    participants_data = [
        {'participant_id': 'EXPORT_001', 'name': '导出测试1', 'gender': '男', 'age': 20, 'grade': '大二', 'major': '心理学'},
        {'participant_id': 'EXPORT_002', 'name': '导出测试2', 'gender': '女', 'age': 19, 'grade': '大一', 'major': '教育学'},
        {'participant_id': 'EXPORT_003', 'name': '导出测试3', 'gender': '男', 'age': 21, 'grade': '大三', 'major': '心理学'},
    ]
    
    for p_data in participants_data:
        data_manager.create_participant(**p_data)
    
    # 创建问卷回答
    responses_data = [
        {'participant_id': 'EXPORT_001', 'scale_id': 1, 'responses_data': {str(i): i % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'EXPORT_002', 'scale_id': 1, 'responses_data': {str(i): (i + 2) % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'EXPORT_003', 'scale_id': 1, 'responses_data': {str(i): (i + 4) % 5 + 3 for i in range(1, 9)}},
    ]
    
    for r_data in responses_data:
        data_manager.create_response(**r_data)
    
    return data_manager, scale_manager

def test_export_data_csv(setup_export_test):
    """测试导出数据为CSV格式"""
    data_manager, scale_manager = setup_export_test
    
    # 导出被试者数据
    participants_file = Path("evaluation/temp_exported_participants.csv")
    success = data_manager.export_participants_to_csv(participants_file)
    
    try:
        # 断言
        assert success == True, "被试者数据CSV导出失败"
        assert participants_file.exists(), "被试者CSV文件不存在"
        
        # 验证CSV内容
        df = pd.read_csv(participants_file)
        assert len(df) >= 3, f"导出的被试者数量不足，期望至少3个，实际: {len(df)}"
        
        # 验证必要列
        required_columns = ['participant_id', 'name', 'gender', 'age', 'grade', 'major']
        for col in required_columns:
            assert col in df.columns, f"缺少必要列: {col}"
        
        # 验证数据内容
        assert 'EXPORT_001' in df['participant_id'].values, "缺少测试被试者EXPORT_001"
        assert '导出测试1' in df['name'].values, "缺少测试被试者姓名"
        
    finally:
        # 清理文件
        if participants_file.exists():
            participants_file.unlink()
    
    # 导出问卷回答数据
    responses_file = Path("evaluation/temp_exported_responses.csv")
    success = data_manager.export_responses_to_csv(responses_file, scale_id=1)
    
    try:
        # 断言
        assert success == True, "问卷回答数据CSV导出失败"
        assert responses_file.exists(), "问卷回答CSV文件不存在"
        
        # 验证CSV内容
        df = pd.read_csv(responses_file)
        assert len(df) >= 3, f"导出的回答数量不足，期望至少3个，实际: {len(df)}"
        
        # 验证必要列
        required_columns = ['participant_id', 'total_score', 'completed_at']
        for col in required_columns:
            assert col in df.columns, f"缺少必要列: {col}"
        
        # 验证条目列
        item_columns = [col for col in df.columns if col.startswith('item_')]
        assert len(item_columns) >= 8, f"条目列数量不足，期望至少8个，实际: {len(item_columns)}"
        
        # 验证数据内容
        assert 'EXPORT_001' in df['participant_id'].values, "缺少测试被试者的回答"
        
        # 验证总分计算
        for _, row in df.iterrows():
            assert pd.notna(row['total_score']), "总分不应为空"
            assert isinstance(row['total_score'], (int, float)), "总分应为数值类型"
            assert 1 <= row['total_score'] <= 7, f"总分超出合理范围: {row['total_score']}"
        
    finally:
        # 清理文件
        if responses_file.exists():
            responses_file.unlink()

def test_export_data_excel(setup_export_test):
    """测试导出数据为Excel格式"""
    data_manager, scale_manager = setup_export_test
    
    # 导出被试者数据为Excel
    participants_file = Path("evaluation/temp_exported_participants.xlsx")
    success = data_manager.export_participants_to_excel(participants_file)
    
    try:
        # 断言
        assert success == True, "被试者数据Excel导出失败"
        assert participants_file.exists(), "被试者Excel文件不存在"
        
        # 验证Excel内容
        df = pd.read_excel(participants_file)
        assert len(df) >= 3, f"导出的被试者数量不足，期望至少3个，实际: {len(df)}"
        
        # 验证必要列
        required_columns = ['participant_id', 'name', 'gender', 'age', 'grade', 'major']
        for col in required_columns:
            assert col in df.columns, f"缺少必要列: {col}"
        
        # 验证数据类型
        assert df['age'].dtype in ['int64', 'float64'], "年龄列应为数值类型"
        assert df['participant_id'].dtype == 'object', "被试者ID列应为字符串类型"
        
    finally:
        # 清理文件
        if participants_file.exists():
            participants_file.unlink()
    
    # 导出问卷回答数据为Excel
    responses_file = Path("evaluation/temp_exported_responses.xlsx")
    success = data_manager.export_responses_to_excel(responses_file, scale_id=1)
    
    try:
        # 断言
        assert success == True, "问卷回答数据Excel导出失败"
        assert responses_file.exists(), "问卷回答Excel文件不存在"
        
        # 验证Excel内容
        df = pd.read_excel(responses_file)
        assert len(df) >= 3, f"导出的回答数量不足，期望至少3个，实际: {len(df)}"
        
        # 验证数据类型
        assert df['total_score'].dtype in ['int64', 'float64'], "总分列应为数值类型"
        
        # 验证条目数据类型
        item_columns = [col for col in df.columns if col.startswith('item_')]
        for col in item_columns:
            assert df[col].dtype in ['int64', 'float64'], f"条目列{col}应为数值类型"
        
    finally:
        # 清理文件
        if responses_file.exists():
            responses_file.unlink()

def test_export_analysis_results(setup_export_test):
    """测试导出分析结果"""
    data_manager, scale_manager = setup_export_test
    
    # 进行描述统计分析
    from statistical_analysis import StatisticalAnalyzer
    analyzer = StatisticalAnalyzer()
    
    descriptive_results = analyzer.descriptive_statistics(scale_id=1)
    
    # 导出描述统计结果
    desc_file = Path("evaluation/temp_descriptive_results.csv")
    success = data_manager.export_analysis_results_to_csv(descriptive_results, desc_file)
    
    try:
        # 断言
        assert success == True, "描述统计结果CSV导出失败"
        assert desc_file.exists(), "描述统计结果文件不存在"
        
        # 验证文件内容
        df = pd.read_csv(desc_file)
        assert len(df) > 0, "描述统计结果文件为空"
        
        # 验证统计指标列
        expected_columns = ['metric', 'value']
        for col in expected_columns:
            assert col in df.columns, f"缺少必要列: {col}"
        
        # 验证统计指标内容
        metrics = df['metric'].values
        expected_metrics = ['count', 'mean', 'std', 'min', 'max']
        for metric in expected_metrics:
            assert any(metric in m for m in metrics), f"缺少统计指标: {metric}"
        
    finally:
        # 清理文件
        if desc_file.exists():
            desc_file.unlink()

def test_export_with_filters(setup_export_test):
    """测试带筛选条件的数据导出"""
    data_manager, scale_manager = setup_export_test
    
    # 按性别筛选导出
    male_file = Path("evaluation/temp_male_participants.csv")
    success = data_manager.export_participants_to_csv(male_file, filters={'gender': '男'})
    
    try:
        # 断言
        assert success == True, "按性别筛选导出失败"
        assert male_file.exists(), "筛选导出文件不存在"
        
        # 验证筛选结果
        df = pd.read_csv(male_file)
        assert len(df) >= 2, f"男性被试者数量不足，期望至少2个，实际: {len(df)}"
        assert all(df['gender'] == '男'), "筛选结果包含非男性被试者"
        
    finally:
        # 清理文件
        if male_file.exists():
            male_file.unlink()
    
    # 按年级筛选导出
    grade_file = Path("evaluation/temp_grade_participants.csv")
    success = data_manager.export_participants_to_csv(grade_file, filters={'grade': '大二'})
    
    try:
        # 断言
        assert success == True, "按年级筛选导出失败"
        assert grade_file.exists(), "年级筛选导出文件不存在"
        
        # 验证筛选结果
        df = pd.read_csv(grade_file)
        assert len(df) >= 1, f"大二被试者数量不足，期望至少1个，实际: {len(df)}"
        assert all(df['grade'] == '大二'), "筛选结果包含非大二被试者"
        
    finally:
        # 清理文件
        if grade_file.exists():
            grade_file.unlink()

def test_export_with_custom_columns(setup_export_test):
    """测试自定义列的数据导出"""
    data_manager, scale_manager = setup_export_test
    
    # 指定导出列
    custom_columns = ['participant_id', 'name', 'gender', 'age']
    custom_file = Path("evaluation/temp_custom_participants.csv")
    
    success = data_manager.export_participants_to_csv(custom_file, columns=custom_columns)
    
    try:
        # 断言
        assert success == True, "自定义列导出失败"
        assert custom_file.exists(), "自定义列导出文件不存在"
        
        # 验证列
        df = pd.read_csv(custom_file)
        assert list(df.columns) == custom_columns, f"导出列不匹配，期望: {custom_columns}, 实际: {list(df.columns)}"
        assert len(df) >= 3, "导出数据行数不足"
        
        # 验证不包含未指定的列
        assert 'grade' not in df.columns, "不应包含未指定的grade列"
        assert 'major' not in df.columns, "不应包含未指定的major列"
        
    finally:
        # 清理文件
        if custom_file.exists():
            custom_file.unlink()

def test_export_data_integrity(setup_export_test):
    """测试导出数据完整性"""
    data_manager, scale_manager = setup_export_test
    
    # 获取原始数据
    original_participants = data_manager.list_participants()
    original_responses = data_manager.list_responses(scale_id=1)
    
    # 导出数据
    participants_file = Path("evaluation/temp_integrity_participants.csv")
    responses_file = Path("evaluation/temp_integrity_responses.csv")
    
    success1 = data_manager.export_participants_to_csv(participants_file)
    success2 = data_manager.export_responses_to_csv(responses_file, scale_id=1)
    
    try:
        # 断言导出成功
        assert success1 == True, "被试者数据导出失败"
        assert success2 == True, "问卷回答数据导出失败"
        
        # 验证数据完整性
        exported_participants = pd.read_csv(participants_file)
        exported_responses = pd.read_csv(responses_file)
        
        # 验证数量一致性
        assert len(exported_participants) == len(original_participants), "导出的被试者数量与原始数据不一致"
        assert len(exported_responses) == len(original_responses), "导出的回答数量与原始数据不一致"
        
        # 验证ID一致性
        original_participant_ids = {p.participant_id for p in original_participants}
        exported_participant_ids = set(exported_participants['participant_id'].values)
        assert original_participant_ids == exported_participant_ids, "导出的被试者ID与原始数据不一致"
        
        # 验证数据值一致性（抽样检查）
        for _, row in exported_participants.iterrows():
            original_participant = next((p for p in original_participants if p.participant_id == row['participant_id']), None)
            assert original_participant is not None, f"找不到原始被试者: {row['participant_id']}"
            assert original_participant.name == row['name'], "被试者姓名不一致"
            assert original_participant.gender == row['gender'], "被试者性别不一致"
            assert original_participant.age == row['age'], "被试者年龄不一致"
        
    finally:
        # 清理文件
        if participants_file.exists():
            participants_file.unlink()
        if responses_file.exists():
            responses_file.unlink()

def test_export_error_handling(setup_export_test):
    """测试导出错误处理"""
    data_manager, scale_manager = setup_export_test
    
    # 测试导出到无效路径
    invalid_path = Path("/invalid/path/test.csv")
    success = data_manager.export_participants_to_csv(invalid_path)
    assert success == False, "导出到无效路径应该失败"
    
    # 测试导出不存在的量表数据
    nonexistent_file = Path("evaluation/temp_nonexistent.csv")
    success = data_manager.export_responses_to_csv(nonexistent_file, scale_id=999)
    assert success == False, "导出不存在的量表数据应该失败"
    
    # 测试空数据导出
    empty_scale = scale_manager.create_scale(name="空量表", description="没有数据")
    empty_file = Path("evaluation/temp_empty.csv")
    
    try:
        success = data_manager.export_responses_to_csv(empty_file, scale_id=empty_scale.id)
        # 空数据导出可能成功但文件应该只包含表头
        if success and empty_file.exists():
            df = pd.read_csv(empty_file)
            assert len(df) == 0, "空数据导出应该只包含表头"
    finally:
        if empty_file.exists():
            empty_file.unlink()

def test_export_large_dataset(setup_export_test):
    """测试大数据集导出性能"""
    data_manager, scale_manager = setup_export_test
    
    # 创建大量测试数据
    import time
    
    # 记录开始时间
    start_time = time.time()
    
    # 创建100个被试者（模拟大数据集）
    for i in range(100):
        data_manager.create_participant(
            participant_id=f'LARGE_{i:03d}',
            name=f'大数据测试{i}',
            gender='男' if i % 2 == 0 else '女',
            age=18 + (i % 10),
            grade=f'大{(i % 4) + 1}',
            major='心理学' if i % 3 == 0 else '教育学'
        )
        
        # 为每个被试者创建回答
        responses_data = {str(j): (i + j) % 5 + 3 for j in range(1, 9)}
        data_manager.create_response(f'LARGE_{i:03d}', 1, responses_data)
    
    # 导出大数据集
    large_file = Path("evaluation/temp_large_dataset.csv")
    
    try:
        export_start = time.time()
        success = data_manager.export_responses_to_csv(large_file, scale_id=1)
        export_time = time.time() - export_start
        
        # 断言
        assert success == True, "大数据集导出失败"
        assert large_file.exists(), "大数据集导出文件不存在"
        
        # 验证导出内容
        df = pd.read_csv(large_file)
        assert len(df) >= 103, f"大数据集导出数量不足，期望至少103个，实际: {len(df)}"  # 原有3个 + 新增100个
        
        # 性能断言（导出时间应该在合理范围内）
        assert export_time < 30, f"大数据集导出时间过长: {export_time}秒"
        
        # 验证文件大小合理
        file_size = large_file.stat().st_size
        assert file_size > 1000, f"导出文件大小异常小: {file_size}字节"
        
    finally:
        # 清理文件
        if large_file.exists():
            large_file.unlink()
        
        total_time = time.time() - start_time
        print(f"大数据集测试总耗时: {total_time:.2f}秒")

def test_export_data_formats(setup_export_test):
    """测试多种数据格式导出"""
    data_manager, scale_manager = setup_export_test
    
    # 测试支持的格式
    formats = [
        ('csv', 'temp_format_test.csv'),
        ('xlsx', 'temp_format_test.xlsx'),
        ('json', 'temp_format_test.json')
    ]
    
    for format_name, filename in formats:
        file_path = Path(f"evaluation/{filename}")
        
        try:
            # 根据格式调用相应的导出方法
            if format_name == 'csv':
                success = data_manager.export_participants_to_csv(file_path)
            elif format_name == 'xlsx':
                success = data_manager.export_participants_to_excel(file_path)
            elif format_name == 'json':
                success = data_manager.export_participants_to_json(file_path)
            
            # 断言
            assert success == True, f"{format_name}格式导出失败"
            assert file_path.exists(), f"{format_name}格式导出文件不存在"
            
            # 验证文件大小
            file_size = file_path.stat().st_size
            assert file_size > 0, f"{format_name}格式导出文件为空"
            
            # 验证文件内容（基本检查）
            if format_name == 'json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assert isinstance(data, (list, dict)), "JSON格式数据结构不正确"
                    if isinstance(data, list):
                        assert len(data) >= 3, "JSON数据数量不足"
            
        finally:
            # 清理文件
            if file_path.exists():
                file_path.unlink()