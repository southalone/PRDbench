"""
可视化功能测试
"""
import pytest
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from visualization import Visualizer
from scale_manager import ScaleManager
from data_manager import DataManager
from models import create_tables

@pytest.fixture
def setup_visualization_test():
    """设置可视化测试环境"""
    create_tables()
    
    scale_manager = ScaleManager()
    data_manager = DataManager()
    visualizer = Visualizer()
    
    # 创建默认量表
    scale_manager.create_default_scales()
    
    # 创建测试数据
    participants_data = [
        {'participant_id': 'VIZ_001', 'gender': '男', 'age': 20, 'grade': '大二'},
        {'participant_id': 'VIZ_002', 'gender': '女', 'age': 19, 'grade': '大一'},
        {'participant_id': 'VIZ_003', 'gender': '男', 'age': 21, 'grade': '大三'},
        {'participant_id': 'VIZ_004', 'gender': '女', 'age': 20, 'grade': '大二'},
    ]
    
    for p_data in participants_data:
        data_manager.create_participant(**p_data)
    
    # 创建问卷回答
    responses_data = [
        {'participant_id': 'VIZ_001', 'scale_id': 1, 'responses_data': {str(i): i % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'VIZ_002', 'scale_id': 1, 'responses_data': {str(i): (i + 2) % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'VIZ_003', 'scale_id': 1, 'responses_data': {str(i): (i + 4) % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'VIZ_004', 'scale_id': 1, 'responses_data': {str(i): (i + 1) % 5 + 3 for i in range(1, 9)}},
    ]
    
    for r_data in responses_data:
        data_manager.create_response(**r_data)
    
    return visualizer, scale_manager, data_manager

def test_export_chart_pdf(setup_visualization_test):
    """测试导出PDF格式图表"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 生成描述统计图表
    result = visualizer.plot_descriptive_stats(scale_id=1)
    
    # 断言基本结果
    assert 'error' not in result, f"图表生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    assert result['success'] == True, "图表生成未成功"
    
    # 测试PDF导出功能
    if 'file_path' in result:
        original_path = Path(result['file_path'])
        pdf_path = original_path.with_suffix('.pdf')
        
        # 模拟PDF导出
        export_result = visualizer.export_chart_as_pdf(original_path, pdf_path)
        
        # 断言
        assert export_result.get('success') == True, "PDF导出失败"
        assert 'file_path' in export_result, "缺少PDF文件路径"
        
        # 清理测试文件
        if pdf_path.exists():
            pdf_path.unlink()
        if original_path.exists():
            original_path.unlink()

def test_export_chart_svg(setup_visualization_test):
    """测试导出SVG格式图表"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 生成描述统计图表
    result = visualizer.plot_descriptive_stats(1)
    
    # 断言基本结果
    assert 'error' not in result, f"热力图生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    
    # 测试SVG导出功能
    if result.get('success') and 'file_path' in result:
        original_path = Path(result['file_path'])
        svg_path = original_path.with_suffix('.svg')
        
        # 模拟SVG导出
        export_result = visualizer.export_chart_as_svg(original_path, svg_path)
        
        # 断言
        assert export_result.get('success') == True, "SVG导出失败"
        assert 'file_path' in export_result, "缺少SVG文件路径"
        
        # 验证SVG文件特征
        if svg_path.exists():
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<svg' in content, "SVG文件格式不正确"
                assert '</svg>' in content, "SVG文件格式不完整"
        
        # 清理测试文件
        if svg_path.exists():
            svg_path.unlink()
        if original_path.exists():
            original_path.unlink()

def test_plot_descriptive_stats(setup_visualization_test):
    """测试描述统计图表生成"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 生成描述统计图表
    result = visualizer.plot_descriptive_stats(scale_id=1)
    
    # 断言
    assert 'error' not in result, f"描述统计图表生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    assert result['success'] == True, "图表生成未成功"
    assert 'file_path' in result, "缺少文件路径"
    assert 'chart_type' in result, "缺少图表类型"
    
    # 验证文件存在
    if 'file_path' in result:
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"图表文件不存在: {file_path}"
        assert file_path.suffix in ['.png', '.jpg', '.jpeg', '.pdf'], "图表文件格式不正确"
        
        # 清理测试文件
        if file_path.exists():
            file_path.unlink()

def test_plot_correlation_heatmap(setup_visualization_test):
    """测试相关分析热力图生成"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 生成相关分析热力图
    result = visualizer.plot_correlation_heatmap(scale_ids=[1])
    
    # 断言
    assert 'error' not in result, f"相关热力图生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    
    if result.get('success'):
        assert 'file_path' in result, "缺少文件路径"
        assert 'chart_type' in result, "缺少图表类型"
        assert result['chart_type'] == 'correlation_heatmap', "图表类型不匹配"
        
        # 验证文件存在
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"热力图文件不存在: {file_path}"
        
        # 清理测试文件
        if file_path.exists():
            file_path.unlink()

def test_plot_group_comparison(setup_visualization_test):
    """测试分组比较图表生成"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 生成分组比较图表
    result = visualizer.plot_group_comparison(scale_id=1, group_by='gender')
    
    # 断言
    assert 'error' not in result, f"分组比较图表生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    
    if result.get('success'):
        assert 'file_path' in result, "缺少文件路径"
        assert 'chart_type' in result, "缺少图表类型"
        assert result['chart_type'] == 'group_comparison', "图表类型不匹配"
        
        # 验证文件存在
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"分组比较图表文件不存在: {file_path}"
        
        # 清理测试文件
        if file_path.exists():
            file_path.unlink()

def test_create_interactive_dashboard(setup_visualization_test):
    """测试创建交互式仪表板"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 创建交互式仪表板
    result = visualizer.create_interactive_dashboard(scale_id=1)
    
    # 断言
    assert 'error' not in result, f"交互式仪表板创建失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    
    if result.get('success'):
        assert 'file_path' in result, "缺少文件路径"
        assert 'dashboard_type' in result, "缺少仪表板类型"
        
        # 验证HTML文件存在
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"仪表板文件不存在: {file_path}"
        assert file_path.suffix == '.html', "仪表板文件应为HTML格式"
        
        # 验证HTML内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<html' in content.lower(), "HTML文件格式不正确"
            assert '</html>' in content.lower(), "HTML文件格式不完整"
            assert 'plotly' in content.lower() or 'chart' in content.lower(), "仪表板应包含图表内容"
        
        # 清理测试文件
        if file_path.exists():
            file_path.unlink()

def test_plot_factor_analysis(setup_visualization_test):
    """测试因子分析图表生成"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 生成因子分析图表
    result = visualizer.plot_factor_analysis(scale_id=1, n_factors=2)
    
    # 断言
    assert 'error' not in result, f"因子分析图表生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    
    if result.get('success'):
        assert 'file_path' in result, "缺少文件路径"
        assert 'chart_type' in result, "缺少图表类型"
        assert result['chart_type'] == 'factor_analysis', "图表类型不匹配"
        
        # 验证文件存在
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"因子分析图表文件不存在: {file_path}"
        
        # 清理测试文件
        if file_path.exists():
            file_path.unlink()

def test_plot_path_analysis(setup_visualization_test):
    """测试路径分析图表生成"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 定义简单的路径模型
    path_model = {
        'paths': [
            {'from': 'scale_1_total', 'to': 'scale_1_dim1', 'coefficient': 0.8},
            {'from': 'scale_1_total', 'to': 'scale_1_dim2', 'coefficient': 0.7}
        ],
        'variables': ['scale_1_total', 'scale_1_dim1', 'scale_1_dim2']
    }
    
    # 生成路径分析图表
    result = visualizer.plot_path_analysis(path_model)
    
    # 断言
    assert 'error' not in result, f"路径分析图表生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    
    if result.get('success'):
        assert 'file_path' in result, "缺少文件路径"
        assert 'chart_type' in result, "缺少图表类型"
        assert result['chart_type'] == 'path_analysis', "图表类型不匹配"
        
        # 验证文件存在
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"路径分析图表文件不存在: {file_path}"
        
        # 清理测试文件
        if file_path.exists():
            file_path.unlink()

def test_chart_customization(setup_visualization_test):
    """测试图表自定义选项"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 测试自定义选项
    custom_options = {
        'title': '自定义标题',
        'width': 800,
        'height': 600,
        'dpi': 300,
        'color_palette': 'viridis',
        'font_size': 12
    }
    
    # 生成带自定义选项的图表
    result = visualizer.plot_descriptive_stats(scale_id=1, **custom_options)
    
    # 断言
    assert 'error' not in result, f"自定义图表生成失败: {result.get('error', '')}"
    assert 'success' in result, "缺少成功标志"
    
    if result.get('success'):
        assert 'file_path' in result, "缺少文件路径"
        assert 'options_used' in result, "缺少使用的选项信息"
        
        # 验证自定义选项是否被应用
        options_used = result['options_used']
        assert options_used.get('title') == '自定义标题', "标题自定义未生效"
        assert options_used.get('width') == 800, "宽度自定义未生效"
        assert options_used.get('height') == 600, "高度自定义未生效"
        
        # 清理测试文件
        file_path = Path(result['file_path'])
        if file_path.exists():
            file_path.unlink()

def test_batch_chart_generation(setup_visualization_test):
    """测试批量图表生成"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 定义批量生成任务
    chart_tasks = [
        {'type': 'descriptive_stats', 'scale_id': 1},
        {'type': 'correlation_heatmap', 'scale_ids': [1]},
        {'type': 'group_comparison', 'scale_id': 1, 'group_by': 'gender'}
    ]
    
    # 执行批量生成
    results = visualizer.generate_charts_batch(chart_tasks)
    
    # 断言
    assert len(results) == len(chart_tasks), f"生成的图表数量不匹配，期望: {len(chart_tasks)}, 实际: {len(results)}"
    
    # 验证每个结果
    for i, result in enumerate(results):
        assert 'task_index' in result, f"第{i+1}个结果缺少任务索引"
        assert 'success' in result, f"第{i+1}个结果缺少成功标志"
        
        if result.get('success'):
            assert 'file_path' in result, f"第{i+1}个结果缺少文件路径"
            
            # 清理测试文件
            file_path = Path(result['file_path'])
            if file_path.exists():
                file_path.unlink()

def test_chart_format_support(setup_visualization_test):
    """测试图表格式支持"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 测试不同格式的图表生成
    formats = ['png', 'pdf', 'svg', 'jpg']
    
    for fmt in formats:
        result = visualizer.plot_descriptive_stats(scale_id=1, output_format=fmt)
        
        # 断言
        assert 'error' not in result, f"{fmt}格式图表生成失败: {result.get('error', '')}"
        
        if result.get('success'):
            assert 'file_path' in result, f"{fmt}格式缺少文件路径"
            
            file_path = Path(result['file_path'])
            assert file_path.suffix.lower() == f'.{fmt}', f"{fmt}格式文件扩展名不正确"
            
            if file_path.exists():
                assert file_path.stat().st_size > 0, f"{fmt}格式文件大小为0"
                
                # 清理测试文件
                file_path.unlink()

def test_visualization_error_handling(setup_visualization_test):
    """测试可视化错误处理"""
    visualizer, scale_manager, data_manager = setup_visualization_test
    
    # 测试不存在的量表ID
    result = visualizer.plot_descriptive_stats(scale_id=999)
    assert 'error' in result, "应该返回错误信息"
    assert result['success'] == False, "成功标志应为False"
    
    # 测试空数据
    # 创建没有回答数据的量表
    empty_scale = scale_manager.create_scale(name="空量表", description="没有数据的量表")
    result = visualizer.plot_descriptive_stats(scale_id=empty_scale.id)
    assert 'error' in result, "空数据应该返回错误信息"
    
    # 测试无效的分组字段
    result = visualizer.plot_group_comparison(scale_id=1, group_by='nonexistent_field')
    assert 'error' in result, "无效分组字段应该返回错误信息"