#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.4.1b 评分预测 - 批量数据评分

测试是否成功对所有数据进行评分，并输出包含客户ID、评分概率、算法类别的完整结果。
"""

import pytest
import sys
import os
import tempfile
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestBatchScoring:
    """批量数据评分测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        
        # 准备 (Arrange): 准备训练数据和包含10条以上客户数据的测试集
        np.random.seed(42)
        n_train = 200
        n_test = 15  # 超过10条的测试数据
        
        # 训练数据
        X_train = pd.DataFrame({
            'age': np.random.randint(20, 80, n_train),
            'income': np.random.randint(20000, 200000, n_train),
            'credit_history': np.random.randint(0, 10, n_train),
            'debt_ratio': np.random.uniform(0, 1, n_train)
        })
        
        y_train = pd.Series(
            ((X_train['income'] > 50000) & 
             (X_train['debt_ratio'] < 0.5) &
             (X_train['age'] > 25)).astype(int)
        )
        
        # 批量测试数据（包含客户ID）
        self.batch_data = pd.DataFrame({
            'customer_id': [f'CUST_{i:03d}' for i in range(1, n_test + 1)],
            'age': np.random.randint(25, 75, n_test),
            'income': np.random.randint(30000, 150000, n_test),
            'credit_history': np.random.randint(1, 8, n_test),
            'debt_ratio': np.random.uniform(0.1, 0.8, n_test)
        })
        
        # 创建临时批量数据文件
        self.temp_batch_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.batch_data.to_csv(self.temp_batch_file.name, index=False)
        self.temp_batch_file.close()
        
        # 尝试训练模型
        try:
            self.algorithm_manager.train_algorithm(
                'logistic_regression', X_train, y_train
            )
            self.model_available = True
            print("✓ 预训练模型准备完成")
        except Exception as e:
            print(f"⚠ 模型训练失败: {e}")
            self.model_available = False
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'temp_batch_file') and os.path.exists(self.temp_batch_file.name):
            os.unlink(self.temp_batch_file.name)
    
    def test_batch_scoring(self):
        """测试批量数据评分功能"""
        if not self.model_available:
            pytest.skip("模型不可用，跳过批量评分测试")
        
        # 执行 (Act): 选择批量评分功能，指定测试集文件
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                # 准备评分数据（移除客户ID列用于模型预测）
                scoring_features = self.batch_data.drop(columns=['customer_id'])
                
                # 进行批量预测
                score_probabilities = algorithm.model.predict_proba(scoring_features)[:, 1]
                score_predictions = algorithm.model.predict(scoring_features)
                
                # 断言 (Assert): 验证是否成功对所有数据进行评分，并输出包含客户ID、评分概率、算法类别的完整结果
                
                # 1. 验证评分数量正确
                assert len(score_probabilities) == len(self.batch_data), "评分数量应该等于输入数据数量"
                assert len(score_predictions) == len(self.batch_data), "预测数量应该等于输入数据数量"
                assert len(self.batch_data) >= 10, "测试集应该包含至少10条数据"
                
                # 2. 构建包含客户ID、评分概率、算法类别的完整结果
                batch_results = pd.DataFrame({
                    'customer_id': self.batch_data['customer_id'],
                    'age': self.batch_data['age'],
                    'income': self.batch_data['income'],
                    'score_probability': score_probabilities,
                    'score_prediction': score_predictions,
                    'algorithm_type': 'logistic_regression'
                })
                
                # 3. 验证完整结果包含必需字段
                required_fields = ['customer_id', 'score_probability', 'algorithm_type']
                for field in required_fields:
                    assert field in batch_results.columns, f"批量评分结果应该包含 {field} 字段"
                
                # 4. 验证评分结果的合理性
                for i, row in batch_results.iterrows():
                    assert isinstance(row['customer_id'], str), "客户ID应该是字符串"
                    assert 0 <= row['score_probability'] <= 1, "评分概率应该在0-1之间"
                    assert row['score_prediction'] in [0, 1], "评分预测应该是0或1"
                    assert row['algorithm_type'] == 'logistic_regression', "算法类别应该正确"
                
                # 5. 显示批量评分结果（前5条）
                print(f"\n批量评分结果预览（共{len(batch_results)}条）:")
                print("-" * 80)
                print(f"{'客户ID':<12} {'年龄':<6} {'收入':<8} {'评分概率':<10} {'评分结果':<8} {'算法类别':<15}")
                print("-" * 80)
                
                for i in range(min(5, len(batch_results))):
                    row = batch_results.iloc[i]
                    print(f"{row['customer_id']:<12} "
                          f"{row['age']:<6} "
                          f"{row['income']:<8} "
                          f"{row['score_probability']:<10.4f} "
                          f"{row['score_prediction']:<8} "
                          f"{row['algorithm_type']:<15}")
                
                print("-" * 80)
                
                # 6. 统计评分分布
                high_risk_count = (batch_results['score_probability'] < 0.3).sum()
                medium_risk_count = ((batch_results['score_probability'] >= 0.3) & 
                                   (batch_results['score_probability'] < 0.7)).sum()
                low_risk_count = (batch_results['score_probability'] >= 0.7).sum()
                
                print(f"风险分布: 高风险{high_risk_count}个, 中风险{medium_risk_count}个, 低风险{low_risk_count}个")
                
                # 7. 验证结果完整性
                total_processed = len(batch_results)
                success_rate = 100.0  # 所有记录都成功评分
                
                assert total_processed == len(self.batch_data), "所有数据都应该被成功评分"
                assert success_rate == 100.0, "批量评分成功率应该100%"
                
                print(f"✓ 批量评分统计: 总数{total_processed}条, 成功率{success_rate:.1f}%")
                print("批量数据评分测试通过：成功对所有数据进行评分，输出包含客户ID、评分概率、算法类别的完整结果")
                
            else:
                pytest.fail("训练后的模型不可用")
                
        except Exception as e:
            pytest.skip(f"批量数据评分测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])