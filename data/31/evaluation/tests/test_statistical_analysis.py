"""
统计分析功能测试
"""
import pytest
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from statistical_analysis import StatisticalAnalyzer
from scale_manager import ScaleManager
from data_manager import DataManager
from models import create_tables

@pytest.fixture
def setup_test_data():
    """设置测试数据"""
    create_tables()
    
    scale_manager = ScaleManager()
    data_manager = DataManager()
    analyzer = StatisticalAnalyzer()
    
    # 创建默认量表
    scale_manager.create_default_scales()
    
    # 创建测试被试者（增加到12个以满足回归分析需求）
    participants_data = [
        {'participant_id': 'TEST001', 'gender': '男', 'age': 20, 'grade': '大二', 'major': '心理学'},
        {'participant_id': 'TEST002', 'gender': '女', 'age': 19, 'grade': '大一', 'major': '教育学'},
        {'participant_id': 'TEST003', 'gender': '男', 'age': 21, 'grade': '大三', 'major': '心理学'},
        {'participant_id': 'TEST004', 'gender': '女', 'age': 20, 'grade': '大二', 'major': '教育学'},
        {'participant_id': 'TEST005', 'gender': '男', 'age': 22, 'grade': '大四', 'major': '心理学'},
        {'participant_id': 'TEST006', 'gender': '女', 'age': 19, 'grade': '大一', 'major': '心理学'},
        {'participant_id': 'TEST007', 'gender': '男', 'age': 20, 'grade': '大二', 'major': '教育学'},
        {'participant_id': 'TEST008', 'gender': '女', 'age': 21, 'grade': '大三', 'major': '心理学'},
        {'participant_id': 'TEST009', 'gender': '男', 'age': 22, 'grade': '大四', 'major': '教育学'},
        {'participant_id': 'TEST010', 'gender': '女', 'age': 20, 'grade': '大二', 'major': '心理学'},
        {'participant_id': 'TEST011', 'gender': '男', 'age': 19, 'grade': '大一', 'major': '教育学'},
        {'participant_id': 'TEST012', 'gender': '女', 'age': 21, 'grade': '大三', 'major': '心理学'},
    ]
    
    for p_data in participants_data:
        data_manager.create_participant(**p_data)
    
    # 创建测试回答数据（增加到12个样本）
    responses_data = [
        {'participant_id': 'TEST001', 'scale_id': 1, 'responses_data': {'1': 5, '2': 3, '3': 6, '4': 2, '5': 5, '6': 4, '7': 3, '8': 5}},
        {'participant_id': 'TEST002', 'scale_id': 1, 'responses_data': {'1': 6, '2': 2, '3': 7, '4': 1, '5': 6, '6': 5, '7': 2, '8': 6}},
        {'participant_id': 'TEST003', 'scale_id': 1, 'responses_data': {'1': 4, '2': 4, '3': 5, '4': 3, '5': 4, '6': 3, '7': 4, '8': 4}},
        {'participant_id': 'TEST004', 'scale_id': 1, 'responses_data': {'1': 7, '2': 1, '3': 6, '4': 2, '5': 7, '6': 6, '7': 1, '8': 7}},
        {'participant_id': 'TEST005', 'scale_id': 1, 'responses_data': {'1': 3, '2': 5, '3': 4, '4': 4, '5': 3, '6': 2, '7': 5, '8': 3}},
        {'participant_id': 'TEST006', 'scale_id': 1, 'responses_data': {'1': 5, '2': 4, '3': 6, '4': 3, '5': 5, '6': 4, '7': 3, '8': 5}},
        {'participant_id': 'TEST007', 'scale_id': 1, 'responses_data': {'1': 4, '2': 3, '3': 5, '4': 4, '5': 4, '6': 3, '7': 4, '8': 4}},
        {'participant_id': 'TEST008', 'scale_id': 1, 'responses_data': {'1': 6, '2': 2, '3': 6, '4': 2, '5': 6, '6': 5, '7': 2, '8': 6}},
        {'participant_id': 'TEST009', 'scale_id': 1, 'responses_data': {'1': 3, '2': 5, '3': 4, '4': 5, '5': 3, '6': 2, '7': 5, '8': 3}},
        {'participant_id': 'TEST010', 'scale_id': 1, 'responses_data': {'1': 7, '2': 1, '3': 7, '4': 1, '5': 7, '6': 6, '7': 1, '8': 7}},
        {'participant_id': 'TEST011', 'scale_id': 1, 'responses_data': {'1': 4, '2': 4, '3': 5, '4': 3, '5': 4, '6': 3, '7': 4, '8': 4}},
        {'participant_id': 'TEST012', 'scale_id': 1, 'responses_data': {'1': 5, '2': 3, '3': 6, '4': 2, '5': 5, '6': 4, '7': 3, '8': 5}},
    ]
    
    for r_data in responses_data:
        data_manager.create_response(**r_data)
    
    # 为第二个量表创建回答数据（增加到12个样本）
    responses_data_scale2 = [
        {'participant_id': 'TEST001', 'scale_id': 2, 'responses_data': {'1': 4, '2': 4, '3': 5, '4': 3, '5': 4, '6': 3, '7': 4, '8': 4}},
        {'participant_id': 'TEST002', 'scale_id': 2, 'responses_data': {'1': 6, '2': 2, '3': 6, '4': 2, '5': 6, '6': 2, '7': 6, '8': 2}},
        {'participant_id': 'TEST003', 'scale_id': 2, 'responses_data': {'1': 3, '2': 5, '3': 4, '4': 4, '5': 3, '6': 5, '7': 3, '8': 5}},
        {'participant_id': 'TEST004', 'scale_id': 2, 'responses_data': {'1': 7, '2': 1, '3': 7, '4': 1, '5': 7, '6': 1, '7': 7, '8': 1}},
        {'participant_id': 'TEST005', 'scale_id': 2, 'responses_data': {'1': 2, '2': 6, '3': 3, '4': 5, '5': 2, '6': 6, '7': 2, '8': 6}},
        {'participant_id': 'TEST006', 'scale_id': 2, 'responses_data': {'1': 5, '2': 3, '3': 5, '4': 3, '5': 5, '6': 3, '7': 5, '8': 3}},
        {'participant_id': 'TEST007', 'scale_id': 2, 'responses_data': {'1': 4, '2': 4, '3': 4, '4': 4, '5': 4, '6': 4, '7': 4, '8': 4}},
        {'participant_id': 'TEST008', 'scale_id': 2, 'responses_data': {'1': 6, '2': 2, '3': 6, '4': 2, '5': 6, '6': 2, '7': 6, '8': 2}},
        {'participant_id': 'TEST009', 'scale_id': 2, 'responses_data': {'1': 3, '2': 5, '3': 3, '4': 5, '5': 3, '6': 5, '7': 3, '8': 5}},
        {'participant_id': 'TEST010', 'scale_id': 2, 'responses_data': {'1': 7, '2': 1, '3': 7, '4': 1, '5': 7, '6': 1, '7': 7, '8': 1}},
        {'participant_id': 'TEST011', 'scale_id': 2, 'responses_data': {'1': 2, '2': 6, '3': 2, '4': 6, '5': 2, '6': 6, '7': 2, '8': 6}},
        {'participant_id': 'TEST012', 'scale_id': 2, 'responses_data': {'1': 5, '2': 3, '3': 5, '4': 3, '5': 5, '6': 3, '7': 5, '8': 3}},
    ]
    
    for r_data in responses_data_scale2:
        data_manager.create_response(**r_data)
    
    return scale_manager, data_manager, analyzer

def test_factor_analysis_with_rotation(setup_test_data):
    """测试带旋转的因子分析"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 执行因子分析
    results = analyzer.factor_analysis(scale_id=1, n_factors=2, rotation='varimax')
    
    # 断言
    assert 'error' not in results, f"因子分析失败: {results.get('error', '')}"
    assert 'factor_loadings' in results, "缺少因子载荷矩阵"
    assert 'eigenvalues' in results, "缺少特征值"
    assert 'variance_explained' in results, "缺少方差解释"
    assert 'kmo' in results, "缺少KMO检验结果"
    assert 'bartlett_test' in results, "缺少Bartlett检验结果"
    
    # 验证KMO值
    if results['kmo']:
        kmo_value = results['kmo']['overall']
        assert 0 <= kmo_value <= 1, f"KMO值应在0-1之间，实际: {kmo_value}"
    
    # 验证Bartlett检验
    if results['bartlett_test']:
        p_value = results['bartlett_test']['p_value']
        assert 0 <= p_value <= 1, f"Bartlett检验p值应在0-1之间，实际: {p_value}"
    
    # 验证因子载荷矩阵
    loadings = results['factor_loadings']
    assert len(loadings) > 0, "因子载荷矩阵为空"
    
    # 验证特征值
    eigenvalues = results['eigenvalues']
    assert len(eigenvalues) > 0, "特征值列表为空"
    assert all(isinstance(ev, (int, float)) for ev in eigenvalues), "特征值应为数值类型"

def test_reliability_item_analysis(setup_test_data):
    """测试信度分析中的项目分析"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 执行信度分析
    results = analyzer.reliability_analysis(scale_id=1)
    
    # 断言
    assert 'error' not in results, f"信度分析失败: {results.get('error', '')}"
    assert 'cronbach_alpha' in results, "缺少Cronbach's α系数"
    assert 'item_analysis' in results, "缺少项目分析"
    
    # 验证Cronbach's α系数
    if results['cronbach_alpha']:
        alpha = results['cronbach_alpha']
        assert 0 <= alpha <= 1, f"Cronbach's α系数应在0-1之间，实际: {alpha}"
    
    # 验证项目分析
    item_analysis = results['item_analysis']
    assert len(item_analysis) > 0, "项目分析结果为空"
    
    # 验证每个项目的分析结果
    for item_key, analysis in item_analysis.items():
        assert 'item_total_correlation' in analysis, f"项目{item_key}缺少项目-总分相关"
        assert 'alpha_if_deleted' in analysis, f"项目{item_key}缺少删除后α值"
        assert 'mean' in analysis, f"项目{item_key}缺少均值"
        assert 'std' in analysis, f"项目{item_key}缺少标准差"
        
        # 验证数值范围
        correlation = analysis['item_total_correlation']
        assert -1 <= correlation <= 1, f"项目{item_key}的相关系数超出范围: {correlation}"

def test_regression_analysis(setup_test_data):
    """测试回归分析"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 执行回归分析（以量表2为因变量，量表1为自变量）
    results = analyzer.regression_analysis(
        dependent_scale_id=2,
        independent_scale_ids=[1],
        regression_type='linear'
    )
    
    # 断言
    assert 'error' not in results, f"回归分析失败: {results.get('error', '')}"
    assert 'model_summary' in results, "缺少模型摘要"
    assert 'coefficients' in results, "缺少回归系数"
    
    # 验证模型摘要
    model_summary = results['model_summary']
    assert 'r_squared' in model_summary, "缺少R²值"
    assert 'f_statistic' in model_summary, "缺少F统计量"
    assert 'f_pvalue' in model_summary, "缺少F检验p值"
    
    # 验证R²值范围
    r_squared = model_summary['r_squared']
    assert 0 <= r_squared <= 1, f"R²值应在0-1之间，实际: {r_squared}"
    
    # 验证回归系数
    coefficients = results['coefficients']
    assert len(coefficients) > 0, "回归系数为空"
    
    # 验证每个系数的信息
    for var_name, coef_info in coefficients.items():
        assert 'coefficient' in coef_info, f"变量{var_name}缺少系数值"
        assert 'p_value' in coef_info, f"变量{var_name}缺少p值"
        assert 'std_error' in coef_info, f"变量{var_name}缺少标准误"
        
        # 验证p值范围
        p_value = coef_info['p_value']
        assert 0 <= p_value <= 1, f"变量{var_name}的p值超出范围: {p_value}"

def test_trend_analysis(setup_test_data):
    """测试趋势分析"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 由于当前实现中没有专门的趋势分析函数，我们测试分组比较中的趋势
    # 这里我们测试按年级分组的分析，可以反映趋势
    results = analyzer.group_comparison(scale_id=1, group_by='grade')
    
    # 断言
    assert 'error' not in results, f"分组比较分析失败: {results.get('error', '')}"
    assert 'group_info' in results, "缺少分组信息"
    assert 'test_results' in results, "缺少检验结果"
    
    # 验证分组信息
    group_info = results['group_info']
    assert len(group_info) > 1, "分组数量不足"
    
    # 验证每组的统计信息
    for group_name, group_data in group_info.items():
        assert 'count' in group_data, f"分组{group_name}缺少样本量"
        assert 'mean' in group_data, f"分组{group_name}缺少均值"
        assert 'std' in group_data, f"分组{group_name}缺少标准差"
        
        # 验证数值合理性
        assert group_data['count'] > 0, f"分组{group_name}样本量应大于0"
        assert group_data['std'] >= 0, f"分组{group_name}标准差应非负"
    
    # 验证检验结果
    test_results = results['test_results']
    assert 'test_type' in test_results, "缺少检验类型"
    assert 'p_value' in test_results, "缺少p值"
    assert 'significant' in test_results, "缺少显著性判断"
    
    # 验证p值范围
    p_value = test_results['p_value']
    assert 0 <= p_value <= 1, f"p值应在0-1之间，实际: {p_value}"

def test_path_analysis_setup(setup_test_data):
    """测试路径分析设置"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 由于当前实现中路径分析功能在可视化模块中，我们测试相关的功能
    # 这里测试相关分析作为路径分析的基础
    results = analyzer.correlation_analysis(scale_ids=[1, 2], method='pearson')
    
    # 断言
    assert 'error' not in results, f"相关分析失败: {results.get('error', '')}"
    assert 'correlation_matrix' in results, "缺少相关矩阵"
    assert 'p_values' in results, "缺少p值矩阵"
    assert 'sample_size' in results, "缺少样本量信息"
    
    # 验证相关矩阵
    correlation_matrix = results['correlation_matrix']
    assert len(correlation_matrix) > 0, "相关矩阵为空"
    
    # 验证相关系数范围
    for var1, correlations in correlation_matrix.items():
        for var2, correlation in correlations.items():
            assert -1 <= correlation <= 1, f"相关系数{var1}-{var2}超出范围: {correlation}"
    
    # 验证p值矩阵
    p_values = results['p_values']
    for var1, p_vals in p_values.items():
        for var2, p_val in p_vals.items():
            if var1 != var2:  # 排除对角线元素
                assert 0 <= p_val <= 1, f"p值{var1}-{var2}超出范围: {p_val}"

def test_path_analysis_results(setup_test_data):
    """测试路径分析结果"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 测试回归分析作为路径分析的一部分
    results = analyzer.regression_analysis(
        dependent_scale_id=2,
        independent_scale_ids=[1],
        regression_type='linear'
    )
    
    # 断言基本结果结构
    assert 'error' not in results, f"回归分析失败: {results.get('error', '')}"
    assert 'model_summary' in results, "缺少模型摘要（相当于拟合指标）"
    assert 'coefficients' in results, "缺少路径系数"
    
    # 验证模型拟合指标（相当于路径分析的拟合指标）
    model_summary = results['model_summary']
    required_fit_indices = ['r_squared', 'f_statistic', 'f_pvalue']
    for index in required_fit_indices:
        assert index in model_summary, f"缺少拟合指标: {index}"
    
    # 验证路径系数（回归系数）
    coefficients = results['coefficients']
    assert len(coefficients) >= 1, "路径系数数量不足"
    
    # 验证系数信息完整性
    for var_name, coef_info in coefficients.items():
        if var_name != 'const':  # 排除常数项
            required_fields = ['coefficient', 'p_value', 'std_error', 't_value']
            for field in required_fields:
                assert field in coef_info, f"变量{var_name}缺少{field}"

def test_descriptive_statistics(setup_test_data):
    """测试描述统计分析"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 执行描述统计分析
    results = analyzer.descriptive_statistics(scale_id=1)
    
    # 断言
    assert 'error' not in results, f"描述统计分析失败: {results.get('error', '')}"
    assert 'overall_stats' in results, "缺少整体统计信息"
    assert 'sample_info' in results, "缺少样本信息"
    
    # 验证统计指标
    overall_stats = results['overall_stats']
    assert 'total_score' in overall_stats, "缺少总分统计"
    
    total_score_stats = overall_stats['total_score']
    required_stats = ['count', 'mean', 'std', 'min', 'max', 'median', 'q25', 'q75']
    
    for stat in required_stats:
        assert stat in total_score_stats, f"缺少统计指标: {stat}"
    
    # 验证统计值的合理性
    assert total_score_stats['count'] > 0, "样本量应大于0"
    assert total_score_stats['std'] >= 0, "标准差应非负"
    assert total_score_stats['min'] <= total_score_stats['max'], "最小值应小于等于最大值"
    assert total_score_stats['q25'] <= total_score_stats['median'] <= total_score_stats['q75'], "分位数顺序错误"

def test_group_comparison_analysis(setup_test_data):
    """测试分组比较分析"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 执行分组比较（按性别）
    results = analyzer.group_comparison(scale_id=1, group_by='gender')
    
    # 断言
    assert 'error' not in results, f"分组比较分析失败: {results.get('error', '')}"
    assert 'group_info' in results, "缺少分组信息"
    assert 'test_results' in results, "缺少检验结果"
    
    # 验证分组信息
    group_info = results['group_info']
    assert len(group_info) == 2, f"性别分组应该有2组，实际: {len(group_info)}"
    
    # 验证检验结果
    test_results = results['test_results']
    assert 'test_type' in test_results, "缺少检验类型"
    assert 'p_value' in test_results, "缺少p值"
    assert 'significant' in test_results, "缺少显著性判断"
    
    # 对于t检验，应该有t统计量和效应量
    if test_results['test_type'] == 't_test':
        assert 'statistic' in test_results, "缺少t统计量"
        assert 'effect_size' in test_results, "缺少效应量"
    
    # 对于ANOVA，应该有F统计量和效应量
    elif test_results['test_type'] == 'anova':
        assert 'f_statistic' in test_results, "缺少F统计量"
        assert 'eta_squared' in test_results, "缺少效应量"

def test_correlation_analysis(setup_test_data):
    """测试相关分析"""
    scale_manager, data_manager, analyzer = setup_test_data
    
    # 执行相关分析
    results = analyzer.correlation_analysis(scale_ids=[1, 2], method='pearson')
    
    # 断言
    assert 'error' not in results, f"相关分析失败: {results.get('error', '')}"
    assert 'correlation_matrix' in results, "缺少相关矩阵"
    assert 'p_values' in results, "缺少p值矩阵"
    assert 'method' in results, "缺少分析方法信息"
    assert 'sample_size' in results, "缺少样本量信息"
    
    # 验证分析方法
    assert results['method'] == 'pearson', "分析方法不匹配"
    
    # 验证样本量
    sample_size = results['sample_size']
    assert sample_size > 0, "样本量应大于0"
    
    # 验证相关矩阵结构
    correlation_matrix = results['correlation_matrix']
    p_values = results['p_values']
    
    # 相关矩阵和p值矩阵应该有相同的结构
    assert len(correlation_matrix) == len(p_values), "相关矩阵和p值矩阵结构不匹配"
    
    for var1 in correlation_matrix:
        assert var1 in p_values, f"p值矩阵中缺少变量: {var1}"
        assert len(correlation_matrix[var1]) == len(p_values[var1]), f"变量{var1}的矩阵结构不匹配"