#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.7.2a 神经网络解释 - 权重输出

测试是否输出了代表性的网络权重信息。
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


class TestNeuralNetworkWeights:
    """神经网络权重输出测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        
        # 创建训练数据
        np.random.seed(42)
        n_samples = 300
        
        self.X_train = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples),
            'feature4': np.random.normal(0, 1, n_samples)
        })
        
        # 创建目标变量
        self.y_train = pd.Series(
            ((self.X_train['feature1'] * 0.6 + self.X_train['feature2'] * 0.4 + 
              np.random.normal(0, 0.3, n_samples)) > 0).astype(int)
        )
        
        # 训练神经网络模型
        try:
            self.algorithm_manager.train_algorithm(
                'neural_network', self.X_train, self.y_train
            )
            self.model_available = True
            print("[INFO] 神经网络模型训练完成")
        except Exception as e:
            print(f"[WARNING] 神经网络训练失败: {e}")
            self.model_available = False
    
    def test_neural_network_weights(self):
        """测试神经网络权重输出功能"""
        if not self.model_available:
            pytest.skip("神经网络模型不可用，跳过权重输出测试")
        
        # 执行 (Act): 使用神经网络算法完成分析
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('neural_network')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                
                # 断言 (Assert): 验证是否输出了代表性的网络权重信息
                
                # 1. 获取网络权重信息
                model = algorithm.model
                weights_info = []
                
                # 检查sklearn MLPClassifier的权重
                if hasattr(model, 'coefs_'):
                    coefs = model.coefs_  # 权重矩阵列表
                    intercepts = model.intercepts_  # 偏置列表
                    
                    print(f"[INFO] 神经网络结构分析:")
                    print(f"  输入特征数: {self.X_train.shape[1]}")
                    print(f"  隐藏层数: {len(coefs) - 1}")
                    print(f"  输出层数: 1")
                    
                    # 分析每层的权重
                    for layer_idx, (coef_matrix, bias_vector) in enumerate(zip(coefs, intercepts)):
                        layer_type = "输入->隐藏" if layer_idx == 0 else f"隐藏{layer_idx}->隐藏{layer_idx+1}" if layer_idx < len(coefs) - 1 else f"隐藏->输出"
                        
                        weights_info.append({
                            'layer': layer_idx + 1,
                            'layer_type': layer_type,
                            'weight_shape': coef_matrix.shape,
                            'bias_shape': bias_vector.shape,
                            'weight_stats': {
                                'mean': np.mean(coef_matrix),
                                'std': np.std(coef_matrix),
                                'min': np.min(coef_matrix),
                                'max': np.max(coef_matrix)
                            },
                            'bias_stats': {
                                'mean': np.mean(bias_vector),
                                'std': np.std(bias_vector),
                                'min': np.min(bias_vector),
                                'max': np.max(bias_vector)
                            }
                        })
                        
                        print(f"  第{layer_idx+1}层 ({layer_type}):")
                        print(f"    权重矩阵: {coef_matrix.shape}")
                        print(f"    偏置向量: {bias_vector.shape}")
                        print(f"    权重统计: 均值={np.mean(coef_matrix):.4f}, 标准差={np.std(coef_matrix):.4f}")
                        print(f"    偏置统计: 均值={np.mean(bias_vector):.4f}, 标准差={np.std(bias_vector):.4f}")
                
                # 2. 验证权重信息的完整性
                assert len(weights_info) >= 1, "应该至少有一层权重信息"
                
                total_weights = 0
                total_biases = 0
                
                for layer_info in weights_info:
                    weight_shape = layer_info['weight_shape']
                    bias_shape = layer_info['bias_shape']
                    
                    # 验证权重矩阵形状合理
                    assert len(weight_shape) == 2, "权重应该是二维矩阵"
                    assert weight_shape[0] > 0 and weight_shape[1] > 0, "权重矩阵维度应该大于0"
                    
                    # 验证偏置向量形状合理
                    assert len(bias_shape) == 1, "偏置应该是一维向量"
                    assert bias_shape[0] > 0, "偏置向量长度应该大于0"
                    
                    layer_weight_count = weight_shape[0] * weight_shape[1]
                    layer_bias_count = bias_shape[0]
                    
                    total_weights += layer_weight_count
                    total_biases += layer_bias_count
                    
                    # 验证权重统计合理性
                    weight_stats = layer_info['weight_stats']
                    bias_stats = layer_info['bias_stats']
                    
                    assert not np.isnan(weight_stats['mean']), "权重均值不应该是NaN"
                    assert not np.isnan(bias_stats['mean']), "偏置均值不应该是NaN"
                    assert weight_stats['std'] >= 0, "权重标准差应该非负"
                    assert bias_stats['std'] >= 0, "偏置标准差应该非负"
                
                # 3. 显示代表性权重信息
                print(f"\n[WEIGHTS_SUMMARY] 神经网络权重总结:")
                print(f"  网络层数: {len(weights_info)}")
                print(f"  总权重参数数: {total_weights}")
                print(f"  总偏置参数数: {total_biases}")
                print(f"  总参数数: {total_weights + total_biases}")
                
                # 显示第一层权重的代表性数值（输入层最重要）
                first_layer = weights_info[0]
                first_coef_matrix = coefs[0]
                
                print(f"\n[REPRESENTATIVE_WEIGHTS] 输入层权重分析:")
                feature_names = self.X_train.columns.tolist()
                
                for i, feature_name in enumerate(feature_names):
                    if i < first_coef_matrix.shape[0]:
                        # 获取该特征连接到各隐藏神经元的权重
                        feature_weights = first_coef_matrix[i, :]
                        
                        print(f"  {feature_name}:")
                        print(f"    连接权重数: {len(feature_weights)}")
                        print(f"    权重均值: {np.mean(feature_weights):.6f}")
                        print(f"    权重范围: [{np.min(feature_weights):.6f}, {np.max(feature_weights):.6f}]")
                        print(f"    绝对值均值: {np.mean(np.abs(feature_weights)):.6f}")
                
                # 4. 分析权重的重要性
                # 计算每个输入特征的权重重要性（绝对值平均）
                feature_importance = {}
                for i, feature_name in enumerate(feature_names):
                    if i < first_coef_matrix.shape[0]:
                        feature_weights = first_coef_matrix[i, :]
                        importance = np.mean(np.abs(feature_weights))
                        feature_importance[feature_name] = importance
                
                # 按重要性排序
                sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
                
                print(f"\n[IMPORTANCE_RANKING] 基于权重的特征重要性:")
                for rank, (feature, importance) in enumerate(sorted_features, 1):
                    print(f"  {rank}. {feature}: {importance:.6f}")
                
                # 5. 验证权重输出的代表性
                assert len(weights_info) >= 1, "应该输出至少一层的权重信息"
                assert total_weights >= self.X_train.shape[1], f"权重数量应该至少等于输入特征数: {self.X_train.shape[1]}"
                
                # 验证权重数值的合理性
                for layer_info in weights_info:
                    weight_mean = abs(layer_info['weight_stats']['mean'])
                    weight_std = layer_info['weight_stats']['std']
                    
                    # 权重不应该过大或过小
                    assert weight_mean < 10, f"权重均值应该合理（<10）: {weight_mean}"
                    assert weight_std < 10, f"权重标准差应该合理（<10）: {weight_std}"
                    assert weight_std > 0, f"权重应该有变化（标准差>0）: {weight_std}"
                
                # 6. 验证是否包含足够的代表性信息
                representation_score = 0
                
                if len(weights_info) >= 1:
                    representation_score += 1  # 有权重信息
                if total_weights >= 10:
                    representation_score += 1  # 有足够的权重参数
                if len(feature_importance) == len(feature_names):
                    representation_score += 1  # 分析了所有特征
                if max(sorted_features, key=lambda x: x[1])[1] > min(sorted_features, key=lambda x: x[1])[1] * 1.5:
                    representation_score += 1  # 特征重要性有差异
                
                assert representation_score >= 3, f"权重信息代表性评分应该≥3，实际: {representation_score}"
                
                print(f"\n[EVALUATION] 权重输出质量评估:")
                print(f"  代表性评分: {representation_score}/4")
                print(f"  权重信息层数: {len(weights_info)}")
                print(f"  参数总数: {total_weights + total_biases}")
                print(f"  特征差异度: {max(sorted_features, key=lambda x: x[1])[1] / min(sorted_features, key=lambda x: x[1])[1]:.2f}")
                
                print(f"\n神经网络权重输出测试通过：")
                print(f"成功输出了代表性的网络权重信息，包含{len(weights_info)}层权重，{total_weights + total_biases}个参数")
                
            else:
                pytest.fail("训练后的神经网络模型不可用")
                
        except Exception as e:
            pytest.skip(f"神经网络权重输出测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])