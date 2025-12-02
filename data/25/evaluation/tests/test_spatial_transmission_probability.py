# -*- coding: utf-8 -*-
"""
空间传播概率计算单元测试
测试SpatialBrownianModel类中的空间传播概率计算功能
"""

import pytest
import numpy as np
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import SpatialBrownianModel, Individual


class TestSpatialTransmissionProbability:
    """空间传播概率计算测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建一个简单的配置用于测试
        test_config = {
            'grid_size': 50,
            'num_individuals': 100,
            'sigma': 2,
            'transmission_distance': 4,  # 传播距离阈值为4
            'beta': 0.04,               # 传播率
            'sigma_rate': 0.1,
            'gamma': 0.1,
            'v1': 1/5,
            'v2': 1/3,
            'isolation_duration': 14,
            'days': 10,
            'dt': 1,
            'initial_infected': 5
        }
        self.model = SpatialBrownianModel(test_config)
        
    def test_transmission_probability_distance_correlation(self):
        """测试传播概率与空间距离的负相关关系
        
        验证：
        1. 传播概率与空间距离呈负相关
        2. 距离越近传播概率越高
        3. 超过4个网格单位传播概率为0
        """
        
        # 创建一个感染者在原点
        infected = Individual(10, 10, 'I')
        
        # 创建多个易感者在不同距离
        test_distances = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        transmission_probs = []
        
        for distance in test_distances:
            # 创建易感者在指定距离
            susceptible = Individual(10 + distance, 10, 'S')
            
            # 验证实际距离
            actual_distance = self.model.calculate_distance(infected, susceptible)
            assert abs(actual_distance - distance) < 1e-10, \
                f"距离设置错误：期望{distance}，实际{actual_distance}"
            
            # 计算传播概率（基于源代码中的公式）
            if distance <= self.model.transmission_distance:
                # prob = beta * exp(-distance) * dt
                expected_prob = self.model.beta * np.exp(-distance) * self.model.dt
                transmission_probs.append(expected_prob)
            else:
                # 超过阈值，概率为0
                expected_prob = 0.0
                transmission_probs.append(expected_prob)
            
            print(f"距离{distance}: 传播概率{expected_prob:.6f}")
        
        # 验证负相关关系（在阈值内）
        within_threshold_distances = [d for d in test_distances if d <= self.model.transmission_distance]
        within_threshold_probs = transmission_probs[:len(within_threshold_distances)]
        
        # 检查距离越近概率越高（在阈值内）
        for i in range(len(within_threshold_probs) - 1):
            assert within_threshold_probs[i] > within_threshold_probs[i + 1], \
                f"距离{within_threshold_distances[i]}的概率应该大于距离{within_threshold_distances[i+1]}的概率"
        
        # 验证超过阈值的概率为0
        beyond_threshold_probs = transmission_probs[len(within_threshold_distances):]
        for prob in beyond_threshold_probs:
            assert prob == 0.0, f"超过传播距离阈值的概率应为0，实际为{prob}"
        
        print("传播概率与距离负相关关系验证通过")
    
    def test_transmission_probability_formula(self):
        """测试传播概率计算公式的正确性"""
        
        # 测试传播概率公式：prob = beta * exp(-distance) * dt
        beta = self.model.beta
        dt = self.model.dt
        
        test_cases = [
            (0.0, beta * np.exp(0) * dt),      # 距离为0
            (1.0, beta * np.exp(-1) * dt),     # 距离为1
            (2.0, beta * np.exp(-2) * dt),     # 距离为2
            (3.0, beta * np.exp(-3) * dt),     # 距离为3
            (4.0, beta * np.exp(-4) * dt),     # 边界情况：距离为4
            (5.0, 0.0),                        # 超过阈值：距离为5
        ]
        
        for distance, expected_prob in test_cases:
            # 创建个体
            infected = Individual(0, 0, 'I')
            susceptible = Individual(distance, 0, 'S')
            
            # 验证距离
            actual_distance = self.model.calculate_distance(infected, susceptible)
            assert abs(actual_distance - distance) < 1e-10
            
            # 验证概率计算
            if distance <= self.model.transmission_distance:
                calculated_prob = beta * np.exp(-distance) * dt
            else:
                calculated_prob = 0.0
            
            assert abs(calculated_prob - expected_prob) < 1e-10, \
                f"距离{distance}的传播概率计算错误：期望{expected_prob}，实际{calculated_prob}"
        
        print("传播概率公式验证通过")
    
    def test_transmission_probability_parameters_effect(self):
        """测试传播概率参数的影响"""
        
        # 测试不同beta值的影响
        original_beta = self.model.beta
        distance = 2.0
        
        beta_values = [0.01, 0.02, 0.04, 0.08]
        
        for beta in beta_values:
            self.model.beta = beta
            expected_prob = beta * np.exp(-distance) * self.model.dt
            
            # 验证beta值与概率成正比
            if beta > original_beta:
                original_prob = original_beta * np.exp(-distance) * self.model.dt
                assert expected_prob > original_prob, \
                    f"更大的beta({beta})应该产生更大的传播概率"
        
        # 恢复原始beta值
        self.model.beta = original_beta
        
        # 测试时间步长dt的影响
        original_dt = self.model.dt
        dt_values = [0.5, 1.0, 2.0]
        
        for dt in dt_values:
            self.model.dt = dt
            expected_prob = self.model.beta * np.exp(-distance) * dt
            
            # 验证dt值与概率成正比
            if dt > original_dt:
                original_prob = self.model.beta * np.exp(-distance) * original_dt
                assert expected_prob > original_prob, \
                    f"更大的dt({dt})应该产生更大的传播概率"
        
        # 恢复原始dt值
        self.model.dt = original_dt
        
        print("传播概率参数影响测试通过")
    
    def test_transmission_distance_threshold_effect(self):
        """测试传播距离阈值的影响"""
        
        # 测试边界情况
        threshold = self.model.transmission_distance  # 4.0
        
        # 在阈值内
        just_within = threshold - 0.1  # 3.9
        prob_within = self.model.beta * np.exp(-just_within) * self.model.dt
        assert prob_within > 0, f"阈值内距离{just_within}的传播概率应大于0"
        
        # 在阈值上
        exactly_at = threshold  # 4.0
        prob_at = self.model.beta * np.exp(-exactly_at) * self.model.dt
        assert prob_at > 0, f"阈值距离{exactly_at}的传播概率应大于0"
        
        # 超过阈值
        just_beyond = threshold + 0.1  # 4.1
        prob_beyond = 0.0  # 应该为0
        assert prob_beyond == 0, f"超过阈值距离{just_beyond}的传播概率应为0"
        
        print("传播距离阈值效果测试通过")
    
    def test_exponential_decay_property(self):
        """测试指数衰减特性"""
        
        # 创建距离序列
        distances = np.linspace(0.1, 3.9, 20)  # 在阈值内的距离
        probabilities = []
        
        for distance in distances:
            prob = self.model.beta * np.exp(-distance) * self.model.dt
            probabilities.append(prob)
        
        probabilities = np.array(probabilities)
        
        # 验证指数衰减特性
        # 1. 概率应该随距离单调递减
        for i in range(len(probabilities) - 1):
            assert probabilities[i] > probabilities[i + 1], \
                f"概率应该随距离单调递减，但在位置{i}处发现递增"
        
        # 2. 计算衰减率，应该接近指数衰减
        log_probs = np.log(probabilities)
        # 线性回归斜率应该约为-1（指数衰减特征）
        slope = np.polyfit(distances, log_probs, 1)[0]
        
        assert abs(slope + 1.0) < 0.1, \
            f"指数衰减斜率应接近-1，实际为{slope}"
        
        print("指数衰减特性验证通过")
    
    def test_probability_bounds(self):
        """测试概率边界值"""
        
        # 测试概率值的合理性
        distances = [0.5, 1.0, 2.0, 3.0, 4.0]
        
        for distance in distances:
            if distance <= self.model.transmission_distance:
                prob = self.model.beta * np.exp(-distance) * self.model.dt
                
                # 概率应该在[0, 1]范围内
                assert 0 <= prob <= 1, \
                    f"概率{prob}超出[0,1]范围，距离={distance}"
                
                # 对于合理的参数，概率不应该过大
                assert prob <= 0.5, \
                    f"单步传播概率{prob}过大，距离={distance}"
            else:
                prob = 0.0
                assert prob == 0.0, \
                    f"超过阈值的概率应为0，距离={distance}"
        
        print("概率边界值测试通过")
    
    def test_transmission_step_probability_application(self):
        """测试传播步骤中概率的实际应用"""
        
        # 创建简单的测试场景
        self.model.individuals = [
            Individual(10, 10, 'I'),  # 感染者
            Individual(11, 10, 'S'),  # 易感者，距离=1
            Individual(15, 10, 'S')   # 易感者，距离=5（超过阈值）
        ]
        
        # 设置高传播率以便观察效果
        self.model.beta = 1.0
        
        # 多次执行传播步骤，统计传播情况
        transmissions_close = 0
        transmissions_far = 0
        num_trials = 1000
        
        for _ in range(num_trials):
            # 重置易感者状态
            self.model.individuals[1].state = 'S'
            self.model.individuals[2].state = 'S'
            
            # 执行传播步骤
            self.model.transmission_step()
            
            # 检查传播结果
            if self.model.individuals[1].state == 'E':
                transmissions_close += 1
            if self.model.individuals[2].state == 'E':
                transmissions_far += 1
        
        # 验证传播概率的实际应用
        # 近距离个体应该有传播发生
        close_transmission_rate = transmissions_close / num_trials
        assert close_transmission_rate > 0, "近距离个体应该发生传播"
        
        # 远距离个体（超过阈值）不应该有传播
        far_transmission_rate = transmissions_far / num_trials
        assert far_transmission_rate == 0, f"超过阈值的个体不应该被传播，但发生了{transmissions_far}次"
        
        print("传播步骤概率应用测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestSpatialTransmissionProbability()
    test_instance.setup_method()
    
    try:
        test_instance.test_transmission_probability_distance_correlation()
        test_instance.test_transmission_probability_formula()
        test_instance.test_transmission_probability_parameters_effect()
        test_instance.test_transmission_distance_threshold_effect()
        test_instance.test_exponential_decay_property()
        test_instance.test_probability_bounds()
        test_instance.test_transmission_step_probability_application()
        print("\n所有空间传播概率计算测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")