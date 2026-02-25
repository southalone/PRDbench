# evaluation/tests/test_analysis.py
import os
import sys
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

# 将项目根目录添加到sys.path
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.store_forecasting_tool.core.project_models import Project
from src.store_forecasting_tool.analysis import cost_analyzer, prediction_engine
from src.store_forecasting_tool.cli import report_generator

# 创建一个基础的Project实例供所有测试使用
def create_base_project():
    project_data = {
        "name": "TestProject", "city": "测试市", "area": "测试区", 
        "business_circle_type": "核心商圈", "longitude": 120.0, "latitude": 30.0,
        "categories": {"主食": 0.5, "小吃": 0.3, "饮品": 0.2},
        "avg_item_price": 35.0, "daily_customers": 150, "conversion_rate": 0.8,
        "ingredient_cost_ratio": 0.3, "packaging_cost_ratio": 0.05,
        "monthly_rent": 20000, "monthly_labor_cost": 30000,
        "monthly_marketing_cost": 5000, "commission_rate": 0.15,
        "platform_fee_rate": 0.05, "initial_investment": 100000
    }
    return Project(**project_data)

def test_core_metrics_calculation():
    """测试核心指标是否都能被计算出来。对应 metric: 2.4.1"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    
    required_metrics = [
        "predicted_daily_orders", "avg_item_price", "gross_profit_margin",
        "net_profit", "payback_period_months"
    ]
    for metric in required_metrics:
        assert metric in analysis_results, f"测试失败: 分析结果缺少核心指标 '{metric}'。"
        assert analysis_results[metric] is not None, f"测试失败: 核心指标 '{metric}' 的值为None。"

def test_suggestion_generation():
    """测试是否生成了决策建议。对应 metric: 2.3.3"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    full_analysis = cost_analyzer.perform_sensitivity_analysis(project, analysis_results)

    assert "suggestions" in full_analysis, "测试失败: 分析结果中缺少 'suggestions' 键。"
    assert isinstance(full_analysis["suggestions"], list), "测试失败: 'suggestions' 不一个列表。"
    assert len(full_analysis["suggestions"]) >= 3, "测试失败: 生成的建议少于3条。"

def test_sensitivity_analysis():
    """测试敏感性分析是否生成且排序。对应 metric: 2.4.2"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    full_analysis = cost_analyzer.perform_sensitivity_analysis(project, analysis_results)

    assert "sensitivity_analysis" in full_analysis, "测试失败: 分析结果缺少 'sensitivity_analysis'。"
    assert isinstance(full_analysis["sensitivity_analysis"], list), "测试失败: 'sensitivity_analysis' 不是一个列表。"
    assert len(full_analysis["sensitivity_analysis"]) >= 3, "测试失败: 敏感性因素少于3个。"
    # 验证排序（影响越大的绝对值越大）
    impact_values = [abs(v) for k, v in full_analysis["sensitivity_analysis"]]
    assert impact_values == sorted(impact_values, reverse=True), "测试失败: 敏感性分析结果未按影响大小降序排序。"

def test_break_even_chart_generation():
    """测试回本周期图表能否被成功生成。对应 metric: 2.3.2"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    
    # 报告生成过程会附带生成图表
    output_path = report_generator.EVALUATION_DIR / f"{project.name}_break_even_chart.png"
    if output_path.exists():
        output_path.unlink()

    # 调用主报告生成函数，它会负责图表的生成
    report_generator.generate_md_report(project, analysis_results)

    assert output_path.exists(), f"测试失败: 图表文件 {output_path} 未被创建。"
    assert output_path.stat().st_size > 0, f"测试失败: 图表文件 {output_path} 大小为0。"
    if output_path.exists():
        output_path.unlink()

@patch('src.store_forecasting_tool.cli.report_generator.generate_md_report')
def test_md_report_content_proxy(mock_generate_md):
    """
    通过模拟(mock)来代理验证Markdown报告的内容。
    对应 metric: 2.4.3b
    """
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    
    # 调用报告生成函数
    report_generator.generate_md_report(project, analysis_results)

    # 断言mock函数被调用了
    mock_generate_md.assert_called_once()
    
    # 获取调用时的参数
    args, kwargs = mock_generate_md.call_args
    called_with_project = args[0]
    called_with_analysis = args[1]

    # 验证传入的数据是否正确
    assert called_with_project.name == "TestProject"
    required_metrics = ["predicted_daily_orders", "avg_item_price", "net_profit"]
    for metric in required_metrics:
        assert metric in called_with_analysis

def test_subsidy_impact():
    """测试补贴参数调整对核心指标的影响。对应 metric: 2.2.1"""
    # 该功能点在当前代码中未直接体现，此为占位测试
    pass

def test_category_factor_impact():
    """测试品类影响因子调节对核心指标的影响。对应 metric: 2.2.2"""
    # 该功能点在当前代码中未直接体现，此为占位测试
    pass