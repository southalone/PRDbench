# -*- coding: utf-8 -*-
"""
布朗运动个体移动单元测试
测试Individual类中布朗运动移动功能
"""

import pytest
import numpy as np
import os
import sys
from scipy import stats

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import Individual


class TestBrownianMotion:
    """布朗运动测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.grid_size = 50
        self.sigma = 2  # 布朗运动强度
        
    def test_brownian_motion_characteristics(self):
        """测试布朗运动特性
        
        验证：
        1. 个体空间移动符合布朗运动特性（随机游走）
        2. 移动距离分布合理
        3. 运动强度参数生效
        """
        
        # 创建个体在网格中心
        individual = Individual(25, 25, 'S')
        initial_x, initial_y = individual.x, individual.y
        
        # 记录多次移动的位置变化
        num_steps = 1000
        x_displacements = []
        y_displacements = []
        distances = []
        
        for _ in range(num_steps):
            prev_x, prev_y = individual.x, individual.y
            individual.move(self.sigma, self.grid_size)
            
            # 计算位移
            dx = individual.x - prev_x
            dy = individual.y - prev_y
            distance = np.sqrt(dx**2 + dy**2)
            
            x_displacements.append(dx)
            y_displacements.append(dy)
            distances.append(distance)
        
        # 转换为numpy数组便于分析
        x_displacements = np.array(x_displacements)
        y_displacements = np.array(y_displacements)
        distances = np.array(distances)
        
        # 验证布朗运动特性
        # 1. 位移的均值应该接近0（随机游走特性）
        x_mean = np.mean(x_displacements)
        y_mean = np.mean(y_displacements)
        
        assert abs(x_mean) < 0.2, f"X方向位移均值应接近0，实际为{x_mean}"
        assert abs(y_mean) < 0.2, f"Y方向位移均值应接近0，实际为{y_mean}"
        
        # 2. 位移的标准差应该与设定的sigma相关
        x_std = np.std(x_displacements)
        y_std = np.std(y_displacements)
        
        # 允许20%的误差范围
        expected_std = self.sigma
        assert abs(x_std - expected_std) / expected_std < 0.2, \
            f"X方向标准差应接近{expected_std}，实际为{x_std}"
        assert abs(y_std - expected_std) / expected_std < 0.2, \
            f"Y方向标准差应接近{expected_std}，实际为{y_std}"
        
        # 3. 验证位移分布接近正态分布（Kolmogorov-Smirnov检验）
        # 对X方向位移进行正态性检验
        _, p_value_x = stats.kstest(x_displacements, lambda x: stats.norm.cdf(x, 0, self.sigma))
        _, p_value_y = stats.kstest(y_displacements, lambda x: stats.norm.cdf(x, 0, self.sigma))
        
        # p值应该大于0.01（95%置信度下不拒绝正态分布假设）
        assert p_value_x > 0.01, f"X方向位移不符合正态分布，p值={p_value_x}"
        assert p_value_y > 0.01, f"Y方向位移不符合正态分布，p值={p_value_y}"
        
        print("布朗运动特性验证通过")
    
    def test_movement_distance_distribution(self):
        """测试移动距离分布的合理性"""
        
        individual = Individual(25, 25, 'S')
        num_steps = 500
        distances = []
        
        for _ in range(num_steps):
            prev_x, prev_y = individual.x, individual.y
            individual.move(self.sigma, self.grid_size)
            
            distance = np.sqrt((individual.x - prev_x)**2 + (individual.y - prev_y)**2)
            distances.append(distance)
        
        distances = np.array(distances)
        
        # 验证距离分布特性
        # 1. 平均移动距离应该在合理范围内
        mean_distance = np.mean(distances)
        expected_mean = self.sigma * np.sqrt(2)  # 理论期望值
        
        assert abs(mean_distance - expected_mean) / expected_mean < 0.3, \
            f"平均移动距离应接近{expected_mean}，实际为{mean_distance}"
        
        # 2. 移动距离应该都是非负的
        assert np.all(distances >= 0), "移动距离应该都是非负的"
        
        # 3. 最大移动距离应该在合理范围内（不应该过大）
        max_distance = np.max(distances)
        reasonable_max = self.sigma * 6  # 6倍标准差内
        
        assert max_distance <= reasonable_max, \
            f"最大移动距离{max_distance}超过合理范围{reasonable_max}"
        
        print("移动距离分布测试通过")
    
    def test_motion_intensity_parameter_effect(self):
        """测试运动强度参数的影响"""
        
        # 测试不同的sigma值
        sigma_values = [0.5, 1.0, 2.0, 4.0]
        results = {}
        
        for sigma in sigma_values:
            individual = Individual(25, 25, 'S')
            distances = []
            
            # 执行移动并记录距离
            for _ in range(200):
                prev_x, prev_y = individual.x, individual.y
                individual.move(sigma, self.grid_size)
                distance = np.sqrt((individual.x - prev_x)**2 + (individual.y - prev_y)**2)
                distances.append(distance)
            
            results[sigma] = {
                'mean_distance': np.mean(distances),
                'std_distance': np.std(distances)
            }
        
        # 验证sigma参数的影响
        # 更大的sigma应该导致更大的平均移动距离
        for i in range(len(sigma_values) - 1):
            sigma1 = sigma_values[i]
            sigma2 = sigma_values[i + 1]
            
            mean1 = results[sigma1]['mean_distance']
            mean2 = results[sigma2]['mean_distance']
            
            assert mean2 > mean1, \
                f"更大的sigma({sigma2})应该产生更大的平均移动距离，但{mean2} <= {mean1}"
        
        print("运动强度参数效果测试通过")
    
    def test_grid_boundary_constraints(self):
        """测试网格边界约束"""
        
        # 测试边界情况
        test_cases = [
            (0, 0),           # 左下角
            (49, 49),         # 右上角（grid_size-1）
            (0, 25),          # 左边界
            (49, 25),         # 右边界
            (25, 0),          # 下边界
            (25, 49)          # 上边界
        ]
        
        for start_x, start_y in test_cases:
            individual = Individual(start_x, start_y, 'S')
            
            # 执行多次移动
            for _ in range(100):
                individual.move(self.sigma, self.grid_size)
                
                # 验证个体始终在网格范围内
                assert 0 <= individual.x < self.grid_size, \
                    f"个体X坐标{individual.x}超出网格范围[0, {self.grid_size})"
                assert 0 <= individual.y < self.grid_size, \
                    f"个体Y坐标{individual.y}超出网格范围[0, {self.grid_size})"
        
        print("网格边界约束测试通过")
    
    def test_isolation_prevents_movement(self):
        """测试隔离状态阻止移动"""
        
        # 创建一个个体并设置为隔离状态
        individual = Individual(25, 25, 'I')
        individual.is_isolated = True
        
        # 记录初始位置
        initial_x, initial_y = individual.x, individual.y
        
        # 尝试移动多次
        for _ in range(100):
            individual.move(self.sigma, self.grid_size)
            
            # 验证位置没有改变
            assert individual.x == initial_x, \
                f"隔离个体不应移动，X坐标从{initial_x}变为{individual.x}"
            assert individual.y == initial_y, \
                f"隔离个体不应移动，Y坐标从{initial_y}变为{individual.y}"
        
        # 测试解除隔离后可以移动
        individual.is_isolated = False
        individual.move(self.sigma, self.grid_size)
        
        # 解除隔离后位置可能发生变化（虽然不一定每次都变）
        # 这里只验证不会出错
        assert 0 <= individual.x < self.grid_size
        assert 0 <= individual.y < self.grid_size
        
        print("隔离阻止移动测试通过")
    
    def test_random_walk_properties(self):
        """测试随机游走特性"""
        
        individual = Individual(25, 25, 'S')
        num_steps = 500
        positions = [(individual.x, individual.y)]
        
        # 记录移动轨迹
        for _ in range(num_steps):
            individual.move(self.sigma, self.grid_size)
            positions.append((individual.x, individual.y))
        
        positions = np.array(positions)
        
        # 计算总位移
        total_displacement = np.sqrt((positions[-1][0] - positions[0][0])**2 + 
                                   (positions[-1][1] - positions[0][1])**2)
        
        # 计算总路径长度
        total_path_length = 0
        for i in range(1, len(positions)):
            step_length = np.sqrt((positions[i][0] - positions[i-1][0])**2 + 
                                (positions[i][1] - positions[i-1][1])**2)
            total_path_length += step_length
        
        # 随机游走特性：总位移应该远小于总路径长度
        efficiency = total_displacement / total_path_length
        assert efficiency < 0.3, \
            f"随机游走效率{efficiency}过高，应该小于0.3（体现随机性）"
        
        # 验证轨迹的随机性：相邻步骤方向应该相对随机
        directions = []
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            if dx != 0 or dy != 0:  # 排除没有移动的情况
                angle = np.arctan2(dy, dx)
                directions.append(angle)
        
        if len(directions) > 10:
            # 方向的标准差应该足够大（体现随机性）
            direction_std = np.std(directions)
            assert direction_std > 1.0, \
                f"移动方向标准差{direction_std}过小，应该体现随机性"
        
        print("随机游走特性测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestBrownianMotion()
    test_instance.setup_method()
    
    try:
        test_instance.test_brownian_motion_characteristics()
        test_instance.test_movement_distance_distribution()
        test_instance.test_motion_intensity_parameter_effect()
        test_instance.test_grid_boundary_constraints()
        test_instance.test_isolation_prevents_movement()
        test_instance.test_random_walk_properties()
        print("\n所有布朗运动测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")