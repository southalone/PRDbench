import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.evaluation.metrics import EvaluationMetrics


class TestEvaluationMetrics:
    """推荐系统评估指标单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.metrics = EvaluationMetrics()
        
    def create_test_data(self):
        """创建测试数据"""
        # 创建用户推荐和真实数据
        user_recommendations = {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # 推荐商品列表
            2: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            3: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            4: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19],
            5: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        }
        
        user_ground_truth = {
            1: [1, 2, 11, 12, 21],  # 真实喜欢的商品
            2: [5, 6, 15, 16, 25],
            3: [10, 11, 20, 21, 30],
            4: [1, 7, 13, 19, 31],
            5: [2, 8, 14, 20, 32]
        }
        
        # 创建商品特征数据
        items_df = pd.DataFrame({
            'item_id': range(1, 33),
            'category': ['电子产品', '服装', '图书', '家电', '食品'] * 6 + ['电子产品', '服装'],
            'brand': ['品牌A', '品牌B', '品牌C', '品牌D', '品牌E'] * 6 + ['品牌A', '品牌B'],
            'price': np.random.uniform(100, 1000, 32)
        })
        
        return user_recommendations, user_ground_truth, items_df
    
    def test_precision_at_k(self):
        """测试Precision@K指标"""
        # 测试基本功能
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]
        
        # 测试Precision@5
        # predicted[:5] = [1, 2, 6, 7, 8]，其中 [1, 2] 在 actual 中
        precision_5 = self.metrics.precision_at_k(actual, predicted, 5)
        expected_precision_5 = 2 / 5  # 前5个预测中有2个正确（不是3个）
        assert abs(precision_5 - expected_precision_5) < 0.001, f"Precision@5应该为{expected_precision_5}，实际为{precision_5}"
        
        # 测试Precision@10
        precision_10 = self.metrics.precision_at_k(actual, predicted, 10)
        expected_precision_10 = 4 / 9  # 前9个预测中有4个正确（predicted只有9个）
        assert abs(precision_10 - expected_precision_10) < 0.001, f"Precision@10应该为{expected_precision_10}，实际为{precision_10}"
        
        # 测试边界情况
        assert self.metrics.precision_at_k([], predicted, 5) == 0.0, "空实际列表应该返回0"
        assert self.metrics.precision_at_k(actual, [], 5) == 0.0, "空预测列表应该返回0"
        assert self.metrics.precision_at_k(actual, predicted, 0) == 0.0, "K=0应该返回0"
    
    def test_recall_at_k(self):
        """测试Recall@K指标"""
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]
        
        # 测试Recall@5
        # predicted[:5] = [1, 2, 6, 7, 8]，其中 [1, 2] 在 actual 中，actual 共有 5 个
        recall_5 = self.metrics.recall_at_k(actual, predicted, 5)
        expected_recall_5 = 2 / 5  # 5个实际商品中有2个被推荐在前5位（不是3个）
        assert abs(recall_5 - expected_recall_5) < 0.001, f"Recall@5应该为{expected_recall_5}，实际为{recall_5}"
        
        # 测试Recall@10
        recall_10 = self.metrics.recall_at_k(actual, predicted, 10)
        expected_recall_10 = 4 / 5  # 5个实际商品中有4个被推荐
        assert abs(recall_10 - expected_recall_10) < 0.001, f"Recall@10应该为{expected_recall_10}，实际为{recall_10}"
        
        # 测试边界情况
        assert self.metrics.recall_at_k([], predicted, 5) == 0.0, "空实际列表应该返回0"
        assert self.metrics.recall_at_k(actual, [], 5) == 0.0, "空预测列表应该返回0"
        assert self.metrics.recall_at_k(actual, predicted, 0) == 0.0, "K=0应该返回0"
    
    def test_f1_score_at_k(self):
        """测试F1-Score@K指标"""
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]
        
        # 计算F1@5
        precision_5 = self.metrics.precision_at_k(actual, predicted, 5)
        recall_5 = self.metrics.recall_at_k(actual, predicted, 5)
        f1_5 = self.metrics.f1_score_at_k(actual, predicted, 5)
        
        expected_f1_5 = 2 * (precision_5 * recall_5) / (precision_5 + recall_5)
        assert abs(f1_5 - expected_f1_5) < 0.001, f"F1@5计算错误"
        
        # 测试边界情况
        assert self.metrics.f1_score_at_k([], predicted, 5) == 0.0, "空实际列表应该返回0"
        assert self.metrics.f1_score_at_k(actual, [], 5) == 0.0, "空预测列表应该返回0"
    
    def test_ndcg_at_k(self):
        """测试NDCG@K指标"""
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]
        
        # 测试NDCG@5
        ndcg_5 = self.metrics.ndcg_at_k(actual, predicted, k=5)
        assert 0 <= ndcg_5 <= 1, f"NDCG@5应该在[0,1]范围内，实际为{ndcg_5}"
        
        # 测试完美排序情况
        perfect_predicted = [1, 2, 3, 4, 5]
        perfect_ndcg = self.metrics.ndcg_at_k(actual, perfect_predicted, k=5)
        assert abs(perfect_ndcg - 1.0) < 0.001, "完美排序的NDCG应该接近1.0"
        
        # 测试不同的K值
        ndcg_10 = self.metrics.ndcg_at_k(actual, predicted, k=10)
        assert 0 <= ndcg_10 <= 1, "NDCG@10应该在[0,1]范围内"
        
        # 测试边界情况
        assert self.metrics.ndcg_at_k([], predicted, k=5) == 0.0, "空实际列表应该返回0"
        assert self.metrics.ndcg_at_k(actual, [], k=5) == 0.0, "空预测列表应该返回0"
    
    def test_mean_average_precision(self):
        """测试MAP指标"""
        actual_list = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        predicted_list = [
            [1, 4, 2, 7, 3],
            [4, 1, 5, 8, 6],
            [7, 2, 8, 5, 9]
        ]
        
        map_score = self.metrics.mean_average_precision(actual_list, predicted_list, k=5)
        assert 0 <= map_score <= 1, f"MAP应该在[0,1]范围内，实际为{map_score}"
        
        # 测试边界情况
        empty_actual = [[], [], []]
        map_empty = self.metrics.mean_average_precision(empty_actual, predicted_list, k=5)
        assert map_empty == 0.0, "空实际列表的MAP应该为0"
        
        # 测试长度不匹配
        with pytest.raises(ValueError):
            self.metrics.mean_average_precision([1, 2], [1, 2, 3], k=5)
    
    def test_diversity_score(self):
        """测试多样性指标"""
        # 测试推荐结果的多样性
        recommendations = [
            {'category': 'A', 'brand': 'X'},
            {'category': 'B', 'brand': 'Y'},
            {'category': 'A', 'brand': 'Z'},
            {'category': 'C', 'brand': 'X'},
            {'category': 'B', 'brand': 'Y'}
        ]
        
        # 测试类别多样性
        category_diversity = self.metrics.diversity_score(recommendations, 'category')
        assert 0 <= category_diversity <= 1, f"类别多样性应该在[0,1]范围内，实际为{category_diversity}"
        
        # 测试品牌多样性
        brand_diversity = self.metrics.diversity_score(recommendations, 'brand')
        assert 0 <= brand_diversity <= 1, f"品牌多样性应该在[0,1]范围内，实际为{brand_diversity}"
        
        # 测试完全相同的推荐结果
        same_recommendations = [
            {'category': 'A', 'brand': 'X'},
            {'category': 'A', 'brand': 'X'},
            {'category': 'A', 'brand': 'X'}
        ]
        same_diversity = self.metrics.diversity_score(same_recommendations, 'category')
        assert same_diversity < 0.5, "完全相同的推荐结果多样性应该很低"
        
        # 测试边界情况
        empty_diversity = self.metrics.diversity_score([], 'category')
        assert empty_diversity == 0.0, "空推荐列表应该返回0.0"
        
        print("✓ 多样性指标测试通过")
        print(f"✓ 类别多样性: {category_diversity:.3f}")
        print(f"✓ 品牌多样性: {brand_diversity:.3f}")
    
    def test_coverage_score(self):
        """测试覆盖率指标"""
        recommendations = [
            [1, 2, 3, 4, 5],
            [3, 4, 5, 6, 7],
            [5, 6, 7, 8, 9]
        ]
        
        all_items = set(range(1, 21))  # 总共20个商品
        
        coverage_metrics = self.metrics.coverage_score(recommendations, all_items)
        
        # 验证覆盖率指标
        assert 'item_coverage' in coverage_metrics, "应该包含商品覆盖率"
        assert 'recommendation_coverage' in coverage_metrics, "应该包含推荐覆盖率"
        
        item_coverage = coverage_metrics['item_coverage']
        assert 0 <= item_coverage <= 1, f"商品覆盖率应该在[0,1]范围内，实际为{item_coverage}"
        
        # 验证计算正确性
        unique_recommended = len(set([item for rec in recommendations for item in rec]))
        expected_coverage = unique_recommended / len(all_items)
        assert abs(item_coverage - expected_coverage) < 0.001, "商品覆盖率计算错误"
    
    def test_novelty_score(self):
        """测试新颖性指标"""
        recommendations = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        
        # 设置商品流行度（归一化后的值）
        item_popularity = {
            1: 0.9, 2: 0.8, 3: 0.7,  # 高流行度
            4: 0.5, 5: 0.4, 6: 0.3,  # 中等流行度
            7: 0.2, 8: 0.1, 9: 0.05  # 低流行度（新颖）
        }
        
        novelty = self.metrics.novelty_score(recommendations, item_popularity)
        
        # 验证新颖性分数
        assert 0 <= novelty <= 1, f"新颖性分数应该在[0,1]范围内，实际为{novelty}"
        
        # 验证计算逻辑：新颖性 = 1 - 流行度
        expected_novelty = 1 - np.mean(list(item_popularity.values()))
        assert abs(novelty - expected_novelty) < 0.1, "新颖性计算逻辑正确"
    
    def test_long_tail_coverage(self):
        """测试长尾覆盖率"""
        recommendations = [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10]
        ]
        
        # 创建流行度分布（模拟长尾分布）
        item_popularity = {}
        for i in range(1, 21):
            # 前5个商品流行度高，后15个商品流行度低（长尾）
            if i <= 5:
                item_popularity[i] = 1.0 - (i - 1) * 0.1  # 1.0, 0.9, 0.8, 0.7, 0.6
            else:
                item_popularity[i] = 0.3 - (i - 6) * 0.02  # 递减的低流行度
        
        long_tail_cov = self.metrics.long_tail_coverage(
            recommendations, item_popularity, tail_threshold=0.2
        )
        
        # 验证长尾覆盖率
        assert 0 <= long_tail_cov <= 1, f"长尾覆盖率应该在[0,1]范围内，实际为{long_tail_cov}"
        
        # 测试边界情况
        empty_coverage = self.metrics.long_tail_coverage([], item_popularity)
        assert empty_coverage == 0.0, "空推荐列表的长尾覆盖率应该为0"
    
    def test_comprehensive_evaluation(self):
        """测试综合评估功能"""
        user_recommendations, user_ground_truth, items_df = self.create_test_data()
        
        # 进行综合评估
        evaluation_results = self.metrics.evaluate_recommendations(
            user_recommendations, user_ground_truth, items_df, k_values=[5, 10, 20]
        )
        
        # 验证评估结果结构
        expected_metrics = [
            'precision_at_k', 'recall_at_k', 'f1_at_k', 
            'ndcg_at_k', 'map_at_k', 'hit_rate_at_k'
        ]
        
        for metric in expected_metrics:
            assert metric in evaluation_results, f"应该包含{metric}指标"
            assert isinstance(evaluation_results[metric], dict), f"{metric}应该是字典"
            
            for k in [5, 10, 20]:
                assert k in evaluation_results[metric], f"{metric}应该包含K={k}的结果"
                value = evaluation_results[metric][k]
                assert 0 <= value <= 1, f"{metric}@{k}应该在[0,1]范围内，实际为{value}"
        
        # 验证多样性和覆盖率指标
        assert 'diversity' in evaluation_results, "应该包含多样性指标"
        assert 'coverage' in evaluation_results, "应该包含覆盖率指标"
        assert 'novelty' in evaluation_results, "应该包含新颖性指标"
        assert 'long_tail_coverage' in evaluation_results, "应该包含长尾覆盖率指标"
        
        # 验证指标数值合理性
        novelty = evaluation_results['novelty']
        assert 0 <= novelty <= 1, f"新颖性应该在[0,1]范围内，实际为{novelty}"
        
        long_tail_cov = evaluation_results['long_tail_coverage']
        assert 0 <= long_tail_cov <= 1, f"长尾覆盖率应该在[0,1]范围内，实际为{long_tail_cov}"
    
    def test_evaluation_report_generation(self):
        """测试评估报告生成"""
        user_recommendations, user_ground_truth, items_df = self.create_test_data()
        
        # 进行评估
        evaluation_results = self.metrics.evaluate_recommendations(
            user_recommendations, user_ground_truth, items_df, k_values=[5, 10]
        )
        
        # 生成报告
        report = self.metrics.generate_evaluation_report(
            evaluation_results, algorithm_name="测试推荐算法"
        )
        
        # 验证报告内容
        assert isinstance(report, str), "报告应该是字符串"
        assert len(report) > 0, "报告不应该为空"
        assert "测试推荐算法" in report, "报告应该包含算法名称"
        assert "评估指标汇总" in report, "报告应该包含指标汇总"
        assert "Precision@K" in report, "报告应该包含Precision指标"
        assert "多样性和覆盖率" in report, "报告应该包含多样性分析"
        
        # 验证报告格式
        lines = report.split('\n')
        assert len(lines) > 10, "报告应该包含多行内容"
        
        # 验证Markdown格式
        has_table_header = any('|' in line and 'K值' in line for line in lines)
        assert has_table_header, "报告应该包含表格格式的指标"
    
    def test_edge_cases_and_robustness(self):
        """测试边界情况和鲁棒性"""
        # 测试空数据
        empty_user_recs = {}
        empty_ground_truth = {}
        items_df = pd.DataFrame({
            'item_id': [1, 2, 3],
            'category': ['A', 'B', 'C'],
            'brand': ['X', 'Y', 'Z']
        })
        
        empty_results = self.metrics.evaluate_recommendations(
            empty_user_recs, empty_ground_truth, items_df
        )
        
        # 验证空数据处理
        for metric_dict in empty_results.values():
            if isinstance(metric_dict, dict) and metric_dict:
                for value in metric_dict.values():
                    if isinstance(value, (int, float)):
                        assert 0 <= value <= 1, "空数据的指标值应该在合理范围内"
        
        # 测试单一用户数据
        single_user_recs = {1: [1, 2, 3, 4, 5]}
        single_ground_truth = {1: [2, 3, 6, 7, 8]}
        
        single_results = self.metrics.evaluate_recommendations(
            single_user_recs, single_ground_truth, items_df, k_values=[3, 5]
        )
        
        # 验证单用户处理
        assert single_results['precision_at_k'][3] > 0, "单用户应该能正确计算精确率"
        assert single_results['recall_at_k'][3] > 0, "单用户应该能正确计算召回率"
        
        # 测试不匹配的用户ID
        mismatched_recs = {1: [1, 2, 3], 2: [4, 5, 6]}
        mismatched_truth = {3: [1, 2], 4: [4, 5]}  # 用户ID不匹配
        
        mismatched_results = self.metrics.evaluate_recommendations(
            mismatched_recs, mismatched_truth, items_df
        )
        
        # 不匹配的情况下应该有合理的处理
        assert isinstance(mismatched_results, dict), "不匹配数据应该返回结果字典"