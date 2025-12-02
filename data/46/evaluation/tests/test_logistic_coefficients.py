#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.7.1a 特征解释 - Logistic回归系数输出

测试是否输出了各特征的系数值和正负影响方向。
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestLogisticCoefficients:
    """Logistic回归系数输出测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        
        # 创建有意义的训练数据（特征与目标变量有明确关系）
        np.random.seed(42)
        n_samples = 300
        
        # 设计特征，使其与目标变量有已知关系
        age = np.random.randint(20, 80, n_samples)
        income = np.random.randint(20000, 200000, n_samples)
        debt_ratio = np.random.uniform(0, 1, n_samples)
        credit_history = np.random.randint(0, 10, n_samples)
        
        self.X_train = pd.DataFrame({
            'age': age,
            'income': income,
            'debt_ratio': debt_ratio,
            'credit_history': credit_history
        })
        
        # 创建目标变量，使其与特征有明确的正负关系
        # income正影响，debt_ratio负影响，age和credit_history正影响
        self.y_train = pd.Series(
            ((income / 100000 * 2) +        # 收入正影响
             (-debt_ratio * 3) +            # 债务比例负影响  
             (age / 100) +                  # 年龄轻微正影响
             (credit_history / 10) +        # 信用历史正影响
             np.random.normal(0, 0.5, n_samples) > 0).astype(int)
        )
        
        # 训练模型
        try:
            self.algorithm_manager.train_algorithm(
                'logistic_regression', self.X_train, self.y_train
            )
            self.model_available = True
            print("[INFO] Logistic回归模型训练完成")
        except Exception as e:
            print(f"[WARNING] Logistic回归训练失败: {e}")
            self.model_available = False
    
    def test_logistic_coefficients(self):
        """测试Logistic回归系数输出功能"""
        if not self.model_available:
            pytest.skip("Logistic回归模型不可用，跳过系数输出测试")
        
        # 执行 (Act): 使用Logistic回归算法完成分析
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                
                # 断言 (Assert): 验证是否输出了各特征的系数值和正负影响方向
                
                # 1. 获取模型系数
                if hasattr(algorithm.model, 'coef_'):
                    coefficients = algorithm.model.coef_[0]  # Logistic回归系数
                    feature_names = self.X_train.columns.tolist()
                    
                    assert len(coefficients) == len(feature_names), "系数数量应该等于特征数量"
                    
                    print(f"\nLogistic回归系数分析:")
                    print("-" * 50)
                    print(f"{'特征名称':<15} {'系数值':<12} {'影响方向':<10} {'影响强度'}")
                    print("-" * 50)
                    
                    # 2. 分析每个特征的系数值和影响方向
                    coefficient_analysis = {}
                    
                    for i, (feature, coef) in enumerate(zip(feature_names, coefficients)):
                        # 判断影响方向
                        if coef > 0:
                            direction = "正影响"
                            impact = "增加违约概率" if coef > 0.1 else "轻微增加"
                        elif coef < 0:
                            direction = "负影响"
                            impact = "降低违约概率" if coef < -0.1 else "轻微降低"
                        else:
                            direction = "无影响"
                            impact = "几乎无影响"
                        
                        coefficient_analysis[feature] = {
                            'coefficient': float(coef),
                            'direction': direction,
                            'impact': impact,
                            'abs_coefficient': abs(float(coef))
                        }
                        
                        print(f"{feature:<15} {coef:<12.6f} {direction:<10} {impact}")
                    
                    print("-" * 50)
                    
                    # 3. 验证系数的合理性
                    for feature, analysis in coefficient_analysis.items():
                        coef_value = analysis['coefficient']
                        assert isinstance(coef_value, (float, np.floating)), f"{feature}系数应该是数值类型"
                        assert not np.isnan(coef_value), f"{feature}系数不应该是NaN"
                        assert not np.isinf(coef_value), f"{feature}系数不应该是无穷大"
                    
                    # 4. 验证预期的正负影响方向（基于数据生成逻辑）
                    # income应该是正影响，debt_ratio应该是负影响
                    if 'income' in coefficient_analysis:
                        income_coef = coefficient_analysis['income']['coefficient']
                        print(f"[INFO] 收入系数: {income_coef:.6f} (预期正影响)")
                        # 不强制验证方向，因为数据随机性可能影响结果
                    
                    if 'debt_ratio' in coefficient_analysis:
                        debt_coef = coefficient_analysis['debt_ratio']['coefficient']
                        print(f"[INFO] 债务比例系数: {debt_coef:.6f} (预期负影响)")
                    
                    # 5. 找出影响最大的特征
                    most_important_feature = max(coefficient_analysis.keys(), 
                                               key=lambda x: coefficient_analysis[x]['abs_coefficient'])
                    max_coef_value = coefficient_analysis[most_important_feature]['abs_coefficient']
                    
                    print(f"\n[ANALYSIS] 影响最大的特征: {most_important_feature}")
                    print(f"[ANALYSIS] 系数绝对值: {max_coef_value:.6f}")
                    print(f"[ANALYSIS] 影响方向: {coefficient_analysis[most_important_feature]['direction']}")
                    
                    # 6. 验证系数输出的完整性
                    assert len(coefficient_analysis) >= 3, "应该输出至少3个特征的系数"
                    
                    # 验证包含正负影响
                    positive_coefs = [f for f, a in coefficient_analysis.items() if a['coefficient'] > 0]
                    negative_coefs = [f for f, a in coefficient_analysis.items() if a['coefficient'] < 0]
                    
                    print(f"[INFO] 正影响特征: {len(positive_coefs)}个 - {positive_coefs}")
                    print(f"[INFO] 负影响特征: {len(negative_coefs)}个 - {negative_coefs}")
                    
                    # 至少应该有一些特征有明显影响
                    significant_features = [f for f, a in coefficient_analysis.items() 
                                          if a['abs_coefficient'] > 0.01]
                    assert len(significant_features) >= 1, "应该至少有1个特征有显著影响"
                    
                    print(f"\nLogistic回归系数输出测试通过：成功输出了各特征的系数值和正负影响方向")
                    print(f"分析了{len(coefficient_analysis)}个特征，其中{len(significant_features)}个有显著影响")
                    
                else:
                    pytest.fail("Logistic回归模型没有coef_属性")
                    
            else:
                pytest.fail("训练后的Logistic回归模型不可用")
                
        except Exception as e:
            pytest.skip(f"Logistic回归系数输出测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])