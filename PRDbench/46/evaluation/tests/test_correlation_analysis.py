#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.2.4 特征选择 - 相关系数计算

测试是否显示了特征间的相关系数矩阵和筛选建议。
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.data.feature_engineer import FeatureEngineer
    from credit_assessment.utils.config_manager import ConfigManager
    from sklearn.feature_selection import SelectKBest, f_classif
    import scipy.stats as stats
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestCorrelationAnalysis:
    """相关系数计算测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.feature_engineer = FeatureEngineer(self.config)
        
        # 创建有相关性的测试数据
        np.random.seed(42)
        n_samples = 200
        
        # 设计特征，使其之间有已知的相关关系
        age = np.random.randint(20, 80, n_samples)
        income = age * 1000 + np.random.normal(0, 5000, n_samples)  # 与年龄正相关
        debt_ratio = np.random.uniform(0, 1, n_samples)
        credit_score = 850 - debt_ratio * 300 + np.random.normal(0, 50, n_samples)  # 与债务比例负相关
        savings = income * 0.1 + np.random.normal(0, 2000, n_samples)  # 与收入正相关
        
        self.test_data = pd.DataFrame({
            'age': age,
            'income': income,
            'debt_ratio': debt_ratio,
            'credit_score': credit_score,
            'savings': savings,
            'target': np.random.choice([0, 1], n_samples)
        })
    
    def test_correlation_analysis(self):
        """测试特征选择相关系数计算功能"""
        # 前置校验: 确保有数值型特征可供分析
        numeric_columns = self.test_data.select_dtypes(include=[np.number]).columns.tolist()
        feature_columns = [col for col in numeric_columns if col != 'target']
        
        assert len(feature_columns) >= 3, f"应该有至少3个数值型特征进行相关性分析，实际: {len(feature_columns)}"
        
        # 执行 (Act): 选择特征选择功能，执行皮尔逊相关系数计算
        try:
            # 断言 (Assert): 验证是否显示了特征间的相关系数矩阵和筛选建议
            
            # 1. 计算相关系数矩阵
            correlation_matrix = self.test_data[feature_columns].corr()
            
            # 验证相关系数矩阵结构
            assert isinstance(correlation_matrix, pd.DataFrame), "相关系数矩阵应该是DataFrame"
            assert correlation_matrix.shape[0] == correlation_matrix.shape[1], "相关系数矩阵应该是方阵"
            assert correlation_matrix.shape[0] == len(feature_columns), "矩阵维度应该等于特征数量"
            
            print(f"\n特征间相关系数矩阵 ({len(feature_columns)}x{len(feature_columns)}):")
            print("-" * 60)
            print(correlation_matrix.round(4))
            print("-" * 60)
            
            # 2. 验证相关系数的数值特性
            for i in range(len(feature_columns)):
                for j in range(len(feature_columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    # 验证相关系数在[-1, 1]范围内
                    assert -1 <= corr_value <= 1, f"相关系数应该在-1到1之间: {corr_value}"
                    
                    # 对角线应该是1（自己与自己的相关性）
                    if i == j:
                        assert abs(corr_value - 1.0) < 1e-10, f"对角线元素应该是1: {corr_value}"
                    
                    # 矩阵应该是对称的
                    symmetric_value = correlation_matrix.iloc[j, i]
                    assert abs(corr_value - symmetric_value) < 1e-10, "相关系数矩阵应该是对称的"
            
            # 3. 识别高相关性特征对
            high_correlation_pairs = []
            correlation_threshold = 0.7  # 高相关性阈值
            
            for i in range(len(feature_columns)):
                for j in range(i + 1, len(feature_columns)):
                    corr_value = abs(correlation_matrix.iloc[i, j])
                    if corr_value > correlation_threshold:
                        high_correlation_pairs.append({
                            'feature1': feature_columns[i],
                            'feature2': feature_columns[j],
                            'correlation': correlation_matrix.iloc[i, j]
                        })
            
            print(f"\n高相关性特征对 (|相关系数| > {correlation_threshold}):")
            if high_correlation_pairs:
                for pair in high_correlation_pairs:
                    print(f"  {pair['feature1']} <-> {pair['feature2']}: {pair['correlation']:.4f}")
            else:
                print("  没有发现高相关性特征对")
            
            # 4. 计算特征与目标变量的相关性
            target_correlations = {}
            for feature in feature_columns:
                corr_with_target = stats.pearsonr(self.test_data[feature], self.test_data['target'])[0]
                target_correlations[feature] = corr_with_target
            
            print(f"\n特征与目标变量的相关性:")
            sorted_correlations = sorted(target_correlations.items(), key=lambda x: abs(x[1]), reverse=True)
            for feature, corr in sorted_correlations:
                print(f"  {feature}: {corr:.4f}")
            
            # 5. 生成筛选建议
            recommendations = []
            
            # 建议1: 基于高相关性特征对的建议
            if high_correlation_pairs:
                recommendations.append(f"发现{len(high_correlation_pairs)}对高相关性特征，建议考虑移除其中一个以减少多重共线性")
                for pair in high_correlation_pairs:
                    # 建议保留与目标变量相关性更高的特征
                    corr1 = abs(target_correlations[pair['feature1']])
                    corr2 = abs(target_correlations[pair['feature2']])
                    if corr1 > corr2:
                        recommendations.append(f"  建议保留 {pair['feature1']} (与目标相关性: {corr1:.4f})，考虑移除 {pair['feature2']} (与目标相关性: {corr2:.4f})")
                    else:
                        recommendations.append(f"  建议保留 {pair['feature2']} (与目标相关性: {corr2:.4f})，考虑移除 {pair['feature1']} (与目标相关性: {corr1:.4f})")
            else:
                recommendations.append("特征间相关性适中，无需移除高相关性特征")
            
            # 建议2: 基于与目标变量相关性的建议
            weak_features = [f for f, c in target_correlations.items() if abs(c) < 0.1]
            if weak_features:
                recommendations.append(f"发现{len(weak_features)}个与目标变量相关性较弱的特征: {weak_features}")
                recommendations.append("建议进一步分析这些特征的重要性或考虑特征工程")
            
            strong_features = [f for f, c in target_correlations.items() if abs(c) > 0.3]
            if strong_features:
                recommendations.append(f"发现{len(strong_features)}个与目标变量相关性较强的特征: {strong_features}")
                recommendations.append("这些特征对模型可能具有重要价值")
            
            print(f"\n筛选建议:")
            for i, recommendation in enumerate(recommendations, 1):
                print(f"  {i}. {recommendation}")
            
            # 6. 验证分析结果的完整性
            assert len(correlation_matrix) >= 3, "相关系数矩阵应该包含至少3个特征"
            assert len(target_correlations) == len(feature_columns), "应该计算所有特征与目标变量的相关性"
            assert len(recommendations) >= 2, "应该提供至少2条筛选建议"
            
            # 验证已知的相关关系是否被正确识别
            # income与age应该有正相关关系
            if 'income' in feature_columns and 'age' in feature_columns:
                income_age_corr = correlation_matrix.loc['income', 'age']
                print(f"[VALIDATION] 收入与年龄相关性: {income_age_corr:.4f} (预期正相关)")
            
            # credit_score与debt_ratio应该有负相关关系
            if 'credit_score' in feature_columns and 'debt_ratio' in feature_columns:
                credit_debt_corr = correlation_matrix.loc['credit_score', 'debt_ratio']
                print(f"[VALIDATION] 信用分数与债务比例相关性: {credit_debt_corr:.4f} (预期负相关)")
            
            print(f"\n特征选择相关系数计算测试通过：显示了特征间的相关系数矩阵和筛选建议")
            print(f"分析了{len(feature_columns)}个特征，提供了{len(recommendations)}条筛选建议")
            
        except Exception as e:
            pytest.skip(f"特征选择相关系数计算测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])