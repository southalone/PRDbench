# -*- coding: utf-8 -*-
"""
空间距离计算单元测试
测试SpatialBrownianModel类中的空间距离计算功能
"""

import pytest
import numpy as np
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import SpatialBrownianModel, Individual


class TestSpatialDistanceCalculation:
    """空间距离计算测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建一个简单的配置用于测试
        test_config = {
            'grid_size': 50,
            'num_individuals': 100,
            'sigma': 2,
            'transmission_distance': 4,  # 传播距离阈值为4
            'beta': 0.04,
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
        
    def test_spatial_distance_calculation_accuracy(self):
        """测试空间距离计算的准确性
        
        验证：
        1. 空间距离计算正确（欧几里得距离）
        2. 传播距离阈值4个网格单位生效
        3. 超过阈值的个体间不发生传播
        """
        
        # 创建测试个体
        ind1 = Individual(0, 0, 'I')  # 感染者在原点
        ind2 = Individual(3, 4, 'S')  # 易感者在(3,4)位置
        ind3 = Individual(5, 0, 'S')  # 易感者在(5,0)位置
        ind4 = Individual(0, 5, 'S')  # 易感者在(0,5)位置
        
        # 测试欧几里得距离计算正确性
        # 距离应该是 sqrt((3-0)^2 + (4-0)^2) = sqrt(9+16) = sqrt(25) = 5
        distance1 = self.model.calculate_distance(ind1, ind2)
        expected_distance1 = np.sqrt((3-0)**2 + (4-0)**2)
        assert abs(distance1 - expected_distance1) < 1e-10, \
            f"距离计算错误：期望{expected_distance1}，实际{distance1}"
        assert abs(distance1 - 5.0) < 1e-10, \
            f"具体距离计算错误：期望5.0，实际{distance1}"
        
        # 测试其他距离计算
        distance2 = self.model.calculate_distance(ind1, ind3)  # 应该是5
        distance3 = self.model.calculate_distance(ind1, ind4)  # 应该是5
        
        assert abs(distance2 - 5.0) < 1e-10, \
            f"距离计算错误：期望5.0，实际{distance2}"
        assert abs(distance3 - 5.0) < 1e-10, \
            f"距离计算错误：期望5.0，实际{distance3}"
        
        # 验证传播距离阈值设置
        assert self.model.transmission_distance == 4, \
            f"传播距离阈值应为4，实际为{self.model.transmission_distance}"
        
        print("空间距离计算准确性测试通过")
    
    def test_transmission_distance_threshold(self):
        """测试传播距离阈值的生效性"""
        
        # 创建测试场景：一个感染者和多个易感者
        infected = Individual(10, 10, 'I')  # 感染者
        
        # 在阈值内的易感者（距离 < 4）
        close_susceptible1 = Individual(10, 13, 'S')  # 距离 = 3
        close_susceptible2 = Individual(12, 12, 'S')  # 距离 = sqrt(8) ≈ 2.83
        
        # 在阈值边界的易感者（距离 = 4）
        boundary_susceptible = Individual(10, 14, 'S')  # 距离 = 4
        
        # 超过阈值的易感者（距离 > 4）
        far_susceptible1 = Individual(10, 15, 'S')  # 距离 = 5
        far_susceptible2 = Individual(15, 15, 'S')  # 距离 = sqrt(50) ≈ 7.07
        
        # 验证距离计算
        assert self.model.calculate_distance(infected, close_susceptible1) == 3.0
        assert abs(self.model.calculate_distance(infected, close_susceptible2) - np.sqrt(8)) < 1e-10
        assert self.model.calculate_distance(infected, boundary_susceptible) == 4.0
        assert self.model.calculate_distance(infected, far_susceptible1) == 5.0
        assert abs(self.model.calculate_distance(infected, far_susceptible2) - np.sqrt(50)) < 1e-10
        
        # 验证传播距离阈值逻辑
        # 在阈值内的个体应该可能被传播（距离 <= 4）
        assert self.model.calculate_distance(infected, close_susceptible1) <= self.model.transmission_distance
        assert self.model.calculate_distance(infected, close_susceptible2) <= self.model.transmission_distance
        assert self.model.calculate_distance(infected, boundary_susceptible) <= self.model.transmission_distance
        
        # 超过阈值的个体不应该被传播（距离 > 4）
        assert self.model.calculate_distance(infected, far_susceptible1) > self.model.transmission_distance
        assert self.model.calculate_distance(infected, far_susceptible2) > self.model.transmission_distance
        
        print("传播距离阈值测试通过")
    
    def test_distance_calculation_edge_cases(self):
        """测试距离计算的边界情况"""
        
        # 测试相同位置的个体（距离应为0）
        ind1 = Individual(5, 5, 'I')
        ind2 = Individual(5, 5, 'S')
        distance = self.model.calculate_distance(ind1, ind2)
        assert distance == 0.0, f"相同位置的距离应为0，实际为{distance}"
        
        # 测试最大距离（网格对角线）
        ind3 = Individual(0, 0, 'I')
        ind4 = Individual(50, 50, 'S')  # 网格大小为50
        max_distance = self.model.calculate_distance(ind3, ind4)
        expected_max = np.sqrt(50**2 + 50**2)
        assert abs(max_distance - expected_max) < 1e-10, \
            f"最大距离计算错误：期望{expected_max}，实际{max_distance}"
        
        # 测试负坐标（虽然在实际模型中不会出现，但测试函数健壮性）
        ind5 = Individual(-2, -3, 'I')
        ind6 = Individual(1, 1, 'S')
        distance_negative = self.model.calculate_distance(ind5, ind6)
        expected_negative = np.sqrt((1-(-2))**2 + (1-(-3))**2)  # sqrt(9+16) = 5
        assert abs(distance_negative - expected_negative) < 1e-10, \
            f"负坐标距离计算错误：期望{expected_negative}，实际{distance_negative}"
        
        print("边界情况测试通过")
    
    def test_transmission_threshold_in_simulation_context(self):
        """测试在仿真上下文中传播阈值的正确应用"""
        
        # 设置两个个体：一个感染者，一个易感者
        self.model.individuals = [
            Individual(10, 10, 'I'),  # 感染者
            Individual(10, 15, 'S')   # 易感者，距离为5 > 4（阈值）
        ]
        
        # 记录初始状态
        initial_susceptible_state = self.model.individuals[1].state
        assert initial_susceptible_state == 'S', "初始状态应为易感者"
        
        # 模拟一次传播步骤
        # 由于距离超过阈值，不应该发生传播
        original_beta = self.model.beta
        self.model.beta = 1.0  # 设置很高的传播率，确保如果距离允许就会传播
        
        # 执行传播步骤多次，确保不会发生传播
        for _ in range(100):  # 执行多次以排除随机性
            self.model.transmission_step()
            # 由于距离超过阈值，易感者状态不应改变
            assert self.model.individuals[1].state == 'S', \
                "超过传播距离阈值的个体不应被感染"
        
        # 恢复原始传播率
        self.model.beta = original_beta
        
        # 现在测试在阈值内的情况
        self.model.individuals[1].x = 10
        self.model.individuals[1].y = 13  # 距离为3 < 4（阈值）
        self.model.individuals[1].state = 'S'  # 重置为易感者
        
        # 验证距离确实在阈值内
        distance = self.model.calculate_distance(self.model.individuals[0], self.model.individuals[1])
        assert distance <= self.model.transmission_distance, \
            f"测试个体距离{distance}应该小于等于阈值{self.model.transmission_distance}"
        
        print("仿真上下文中传播阈值测试通过")
    
    def test_euclidean_distance_formula(self):
        """验证欧几里得距离公式的正确实现"""
        
        # 创建多个测试案例
        test_cases = [
            # (x1, y1, x2, y2, expected_distance)
            (0, 0, 0, 0, 0.0),           # 同一点
            (0, 0, 1, 0, 1.0),           # 水平距离
            (0, 0, 0, 1, 1.0),           # 垂直距离
            (0, 0, 1, 1, np.sqrt(2)),    # 对角线
            (0, 0, 3, 4, 5.0),           # 3-4-5直角三角形
            (1, 2, 4, 6, 5.0),           # 另一个3-4-5三角形
            (10.5, 20.3, 15.7, 25.9, np.sqrt((15.7-10.5)**2 + (25.9-20.3)**2))  # 小数坐标
        ]
        
        for x1, y1, x2, y2, expected in test_cases:
            ind1 = Individual(x1, y1, 'I')
            ind2 = Individual(x2, y2, 'S')
            
            calculated = self.model.calculate_distance(ind1, ind2)
            assert abs(calculated - expected) < 1e-10, \
                f"距离计算错误：点({x1},{y1})到({x2},{y2})，期望{expected}，实际{calculated}"
        
        print("欧几里得距离公式验证通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestSpatialDistanceCalculation()
    test_instance.setup_method()
    
    try:
        test_instance.test_spatial_distance_calculation_accuracy()
        test_instance.test_transmission_distance_threshold()
        test_instance.test_distance_calculation_edge_cases()
        test_instance.test_transmission_threshold_in_simulation_context()
        test_instance.test_euclidean_distance_formula()
        print("\n所有空间距离计算测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")