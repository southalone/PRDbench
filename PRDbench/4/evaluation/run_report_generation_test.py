# evaluation/run_report_generation_test.py
import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径中，以便导入项目模块
# 获取当前脚本的绝对路径
current_script_path = Path(__file__).resolve()
# 获取项目根目录 (064_StoreTool)
project_root = current_script_path.parent.parent
# 获取 src 目录
src_path = project_root / "src"
# 将 src 目录添加到系统路径
sys.path.insert(0, str(src_path))

from store_forecasting_tool.core import project_manager as pm
from store_forecasting_tool.analysis import prediction_engine, cost_analyzer
from store_forecasting_tool.cli import report_generator

def run_test():
    """
    一个简单的脚本，用于加载项目、运行分析并生成Markdown报告，
    以绕过交互式CLI的输入问题。
    """
    print("--- 开始自动化报告生成测试 ---")

    # 1. 定位并加载项目
    project_file_path = src_path / "data" / "projects" / "MyFirstStore.json"
    if not project_file_path.exists():
        print(f"错误：测试项目文件未找到于 {project_file_path}")
        return

    print(f"加载测试项目: {project_file_path.name}...")
    project = pm.load_project(project_file_path)
    if not project:
        print("项目加载失败！")
        return
    print("项目加载成功。")

    # 2. 运行分析
    print("正在执行分析...")
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    extra_analysis = cost_analyzer.perform_sensitivity_analysis(project, analysis_results)
    analysis_results.update(extra_analysis)
    print("分析完成。")

    # 3. 生成Markdown报告
    print("正在生成Markdown报告...")
    try:
        report_path_str = report_generator.generate_md_report(project, analysis_results)
        report_path = Path(report_path_str)
        
        # 4. 验证结果
        if report_path.exists() and report_path.stat().st_size > 0:
            print(f"\n--- 测试成功！---")
            print(f"Markdown报告已成功生成于: {report_path.relative_to(project_root)}")
        else:
            print(f"\n--- 测试失败！---")
            print("报告文件未创建或文件为空。")
            
    except Exception as e:
        print(f"\n--- 测试失败！---")
        print(f"生成报告时发生错误: {e}")

if __name__ == "__main__":
    run_test()
