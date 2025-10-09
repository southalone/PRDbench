"""
性能分析测试
"""
import pytest
import os
import sys
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder
from utils.performance import PerformanceAnalyzer


def test_algorithm_recommendations():
    """测试算法推荐建议"""
    generator = MazeGenerator()
    analyzer = PerformanceAnalyzer()

    # 生成测试迷宫
    result = generator.generate('dfs', 15)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # 进行性能比较
    algorithms = ['dfs', 'bfs', 'astar']
    iterations = 3

    try:
        comparison_result = analyzer.compare_algorithms(
            maze_matrix, start_point, end_point, algorithms, iterations
        )

        # 检查是否包含推荐建议
        assert 'recommendations' in comparison_result, "应该包含推荐建议"

        recommendations = comparison_result['recommendations']
        assert isinstance(recommendations, list), "推荐建议应该是列表"
        assert len(recommendations) > 0, "应该提供至少一条推荐建议"

        # 检查推荐建议的内容质量
        # 建议应该基于算法特点
        recommendation_text = ' '.join(recommendations).lower()

        # 应该提到算法特点
        algorithm_mentions = 0
        if 'bfs' in recommendation_text or '广度优先' in recommendation_text:
            algorithm_mentions += 1
        if 'dfs' in recommendation_text or '深度优先' in recommendation_text:
            algorithm_mentions += 1
        if 'astar' in recommendation_text or 'a*' in recommendation_text:
            algorithm_mentions += 1

        assert algorithm_mentions >= 2, f"推荐建议应该提到至少2种算法，实际提到{algorithm_mentions}种"

    except Exception as e:
        pytest.fail(f"算法推荐测试失败: {e}")


def test_performance_comparison():
    """测试性能比较功能"""
    generator = MazeGenerator()
    analyzer = PerformanceAnalyzer()

    # 生成测试迷宫
    result = generator.generate('dfs', 12)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # 进行性能比较
    algorithms = ['dfs', 'bfs', 'astar']
    iterations = 3

    try:
        comparison_result = analyzer.compare_algorithms(
            maze_matrix, start_point, end_point, algorithms, iterations
        )

        # 检查返回结果结构
        required_keys = ['individual_results', 'comparison_report', 'recommendations']
        missing_keys = []

        for key in required_keys:
            if key not in comparison_result:
                missing_keys.append(key)

        assert len(missing_keys) == 0, f"缺少必需的返回组件: {missing_keys}"

        # 检查individual_results
        individual_results = comparison_result['individual_results']
        assert isinstance(individual_results, dict), "individual_results应该是字典"

        # 检查每个算法的结果
        for algo in algorithms:
            if algo in individual_results:
                algo_result = individual_results[algo]
                if 'error' not in algo_result:
                    # 如果算法成功运行，检查统计信息
                    assert 'average_stats' in algo_result, f"{algo}应该包含平均统计信息"
                    avg_stats = algo_result['average_stats']

                    expected_stats = ['search_time', 'path_length', 'explored_nodes_count']
                    for stat in expected_stats:
                        assert stat in avg_stats, f"{algo}的平均统计应该包含{stat}"

    except Exception as e:
        pytest.fail(f"性能比较测试失败: {e}")


def test_complexity_evaluation():
    """测试复杂度评估功能"""
    generator = MazeGenerator()
    analyzer = PerformanceAnalyzer()

    # 生成两个不同大小的迷宫
    small_maze_result = generator.generate('dfs', 10)
    large_maze_result = generator.generate('dfs', 20)

    small_maze = small_maze_result['maze_matrix']
    large_maze = large_maze_result['maze_matrix']

    try:
        # 分析小迷宫复杂度
        small_complexity = analyzer.evaluate_maze_complexity(small_maze)

        # 分析大迷宫复杂度
        large_complexity = analyzer.evaluate_maze_complexity(large_maze)

        # 检查返回结果结构
        required_sections = ['basic_stats', 'path_analysis', 'structure_analysis', 'complexity_evaluation']

        for complexity_result, description in [(small_complexity, "小迷宫"), (large_complexity, "大迷宫")]:
            missing_sections = []
            for section in required_sections:
                if section not in complexity_result:
                    missing_sections.append(section)

            assert len(missing_sections) == 0, f"{description}复杂度评估缺少部分: {missing_sections}"

        # 验证大迷宫的复杂度评分应该高于小迷宫
        small_score = small_complexity['complexity_evaluation']['complexity_score']
        large_score = large_complexity['complexity_evaluation']['complexity_score']

        # 允许一定的误差，因为复杂度不只取决于大小
        assert large_score >= small_score * 0.8, f"大迷宫复杂度评分{large_score}应该不低于小迷宫的80%({small_score * 0.8})"

    except Exception as e:
        pytest.fail(f"复杂度评估测试失败: {e}")
