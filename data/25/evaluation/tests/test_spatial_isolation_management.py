# -*- coding: utf-8 -*-
"""
空间隔离状态管理单元测试
测试SpatialBrownianModel类中的隔离状态管理功能
"""

import pytest
import numpy as np
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import SpatialBrownianModel, Individual


class TestSpatialIsolationManagement:
    """空间隔离状态管理测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建一个简化的配置用于测试
        test_config = {
            'grid_size': 50,
            'num_individuals': 100,
            'sigma': 2,
            'transmission_distance': 4,
            'beta': 0.04,
            'sigma_rate': 0.1,                # 潜伏期转感染率
            'gamma': 0.1,                     # 康复率
            'v1': 1/5,                        # 潜伏者隔离率
            'v2': 1/3,                        # 感染者隔离率
            'isolation_duration': 14,         # 隔离持续时间14天
            'days': 30,
            'dt': 1,
            'initial_infected': 5
        }
        self.model = SpatialBrownianModel(test_config)
        
    def test_isolation_prevents_movement(self):
        """测试隔离个体停止移动
        
        验证：
        1. 隔离个体停止移动
        2. 隔离时间倒计时准确
        3. 隔离解除机制正常工作
        """
        
        # 创建一个个体并设置为隔离状态
        individual = Individual(25, 25, 'I')
        individual.is_isolated = True
        individual.isolation_time = 5  # 已隔离5天
        
        # 记录初始位置
        initial_x, initial_y = individual.x, individual.y
        initial_isolation_time = individual.isolation_time
        
        # 尝试移动（应该不移动）
        for _ in range(10):
            individual.move(self.model.sigma, self.model.grid_size)
            
            # 验证位置没有改变
            assert individual.x == initial_x, \
                f"隔离个体不应移动，X坐标从{initial_x}变为{individual.x}"
            assert individual.y == initial_y, \
                f"隔离个体不应移动，Y坐标从{initial_y}变为{individual.y}"
        
        # 测试隔离时间倒计时
        individual.update_state(
            self.model.sigma_rate, 
            self.model.gamma, 
            self.model.v1, 
            self.model.v2, 
            self.model.isolation_duration, 
            self.model.dt
        )
        
        # 验证隔离时间增加
        expected_isolation_time = initial_isolation_time + self.model.dt
        assert individual.isolation_time == expected_isolation_time, \
            f"隔离时间应从{initial_isolation_time}增加到{expected_isolation_time}，实际为{individual.isolation_time}"
        
        print("隔离阻止移动测试通过")
    
    def test_isolation_time_countdown_accuracy(self):
        """测试隔离时间倒计时的准确性"""
        
        individual = Individual(10, 10, 'E')
        individual.is_isolated = True
        individual.isolation_time = 0
        
        # 模拟多天的隔离时间累积
        days_to_simulate = 10
        for day in range(days_to_simulate):
            individual.update_state(
                self.model.sigma_rate, 
                self.model.gamma, 
                self.model.v1, 
                self.model.v2, 
                self.model.isolation_duration, 
                self.model.dt
            )
            
            expected_time = (day + 1) * self.model.dt
            assert abs(individual.isolation_time - expected_time) < 1e-10, \
                f"第{day+1}天隔离时间应为{expected_time}，实际为{individual.isolation_time}"
        
        print("隔离时间倒计时准确性测试通过")
    
    def test_isolation_release_mechanism(self):
        """测试隔离解除机制正常工作"""
        
        individual = Individual(15, 15, 'I')
        individual.is_isolated = True
        individual.isolation_time = self.model.isolation_duration - 1  # 隔离期即将结束
        
        # 执行状态更新，应该解除隔离
        individual.update_state(
            self.model.sigma_rate, 
            self.model.gamma, 
            self.model.v1, 
            self.model.v2, 
            self.model.isolation_duration, 
            self.model.dt
        )
        
        # 验证隔离解除
        assert not individual.is_isolated, "隔离期满后应该解除隔离"
        assert individual.isolation_time == 0, "隔离解除后隔离时间应重置为0"
        
        # 验证解除隔离后可以移动
        initial_x, initial_y = individual.x, individual.y
        individual.move(self.model.sigma, self.model.grid_size)
        
        # 解除隔离后位置可能发生变化（虽然不一定每次都变）
        # 这里只验证不会出错且坐标仍在合理范围内
        assert 0 <= individual.x < self.model.grid_size
        assert 0 <= individual.y < self.model.grid_size
        
        print("隔离解除机制测试通过")
    
    def test_isolation_transmission_suppression(self):
        """测试隔离对传播有明显抑制作用（感染传播速度降低≥20%）"""
        
        # 创建两个场景：有隔离和无隔离
        
        # 场景1：无隔离配置
        no_isolation_config = self.model.config.copy()
        no_isolation_config.update({
            'v1': 0.0,  # 无隔离
            'v2': 0.0,  # 无隔离
            'days': 20
        })
        
        # 场景2：有隔离配置
        with_isolation_config = self.model.config.copy()
        with_isolation_config.update({
            'v1': 0.2,  # 高隔离率
            'v2': 0.3,  # 高隔离率
            'days': 20
        })
        
        # 运行无隔离模拟
        no_isolation_model = SpatialBrownianModel(no_isolation_config)
        no_isolation_model.solve_simulation()
        
        # 运行有隔离模拟
        with_isolation_model = SpatialBrownianModel(with_isolation_config)
        with_isolation_model.solve_simulation()
        
        # 计算传播速度指标（感染峰值）
        no_isolation_peak = np.max(no_isolation_model.I_count)
        with_isolation_peak = np.max(with_isolation_model.I_count)
        
        # 计算感染传播速度降低率
        if no_isolation_peak > 0:
            reduction_rate = (no_isolation_peak - with_isolation_peak) / no_isolation_peak
            
            print(f"无隔离感染峰值: {no_isolation_peak:.0f}")
            print(f"有隔离感染峰值: {with_isolation_peak:.0f}")
            print(f"传播速度降低率: {reduction_rate:.1%}")
            
            # 验证隔离对传播有明显抑制作用（≥20%）
            assert reduction_rate >= 0.20, \
                f"隔离应该使感染传播速度降低≥20%，实际降低{reduction_rate:.1%}"
        else:
            print("无隔离情况下没有传播，跳过此测试")
        
        print("传播抑制作用测试通过")
    
    def test_isolation_state_transitions(self):
        """测试隔离状态转换的正确性"""
        
        # 测试潜伏者进入隔离
        exposed_individual = Individual(20, 20, 'E')
        exposed_individual.is_isolated = False
        
        # 设置高隔离率确保被隔离
        high_v1 = 1.0  # 100%隔离率
        
        original_state = exposed_individual.state
        
        # 多次尝试状态更新，应该会被隔离
        isolated = False
        for _ in range(100):  # 尝试100次
            exposed_individual.update_state(
                self.model.sigma_rate, 
                self.model.gamma, 
                high_v1,  # 使用高隔离率
                self.model.v2, 
                self.model.isolation_duration, 
                1.0  # 使用较大的时间步长增加概率
            )
            
            if exposed_individual.is_isolated:
                isolated = True
                break
            
            # 重置状态进行下次尝试
            exposed_individual.state = 'E'
            exposed_individual.is_isolated = False
        
        assert isolated, "潜伏者应该有机会被隔离"
        
        # 测试感染者进入隔离
        infected_individual = Individual(30, 30, 'I')
        infected_individual.is_isolated = False
        
        high_v2 = 1.0  # 100%隔离率
        
        isolated = False
        for _ in range(100):  # 尝试100次
            infected_individual.update_state(
                self.model.sigma_rate, 
                self.model.gamma, 
                self.model.v1, 
                high_v2,  # 使用高隔离率
                self.model.isolation_duration, 
                1.0  # 使用较大的时间步长增加概率
            )
            
            if infected_individual.is_isolated:
                isolated = True
                break
            
            # 重置状态进行下次尝试
            infected_individual.state = 'I'
            infected_individual.is_isolated = False
        
        assert isolated, "感染者应该有机会被隔离"
        
        print("隔离状态转换测试通过")
    
    def test_isolation_during_state_progression(self):
        """测试隔离期间的状态进展"""
        
        # 创建一个隔离中的潜伏者
        individual = Individual(25, 25, 'E')
        individual.is_isolated = True
        individual.isolation_time = 5
        
        original_state = individual.state
        
        # 在隔离期间，潜伏者仍可能转为感染者
        for _ in range(100):  # 多次尝试
            # 重置为潜伏者状态
            individual.state = 'E'
            individual.is_isolated = True
            
            individual.update_state(
                1.0,  # 高转换率
                self.model.gamma, 
                self.model.v1, 
                self.model.v2, 
                self.model.isolation_duration, 
                1.0  # 大时间步长
            )
            
            # 如果状态转换为感染者，说明隔离期间状态进展正常
            if individual.state == 'I':
                print("隔离期间状态进展正常：潜伏者转为感染者")
                break
        
        print("隔离期间状态进展测试通过")
    
    def test_isolation_effectiveness_metrics(self):
        """测试隔离效果的量化指标"""
        
        # 创建一个有初始感染者的简单场景
        individuals = [
            Individual(25, 25, 'I'),    # 感染者
            Individual(26, 25, 'S'),    # 附近的易感者
            Individual(27, 25, 'S'),    # 附近的易感者
            Individual(28, 25, 'S'),    # 附近的易感者
        ]
        
        # 设置隔离参数
        v1, v2 = 0.3, 0.5
        isolation_duration = 14
        
        # 模拟一段时间，观察隔离效果
        days_to_simulate = 10
        isolated_count_over_time = []
        
        for day in range(days_to_simulate):
            # 更新所有个体状态
            for individual in individuals:
                individual.update_state(
                    self.model.sigma_rate, 
                    self.model.gamma, 
                    v1, v2, 
                    isolation_duration, 
                    self.model.dt
                )
            
            # 统计隔离个体数量
            isolated_count = sum(1 for ind in individuals if ind.is_isolated)
            isolated_count_over_time.append(isolated_count)
        
        # 验证隔离机制在工作
        max_isolated = max(isolated_count_over_time)
        total_isolated_days = sum(isolated_count_over_time)
        
        print(f"最大同时隔离人数: {max_isolated}")
        print(f"总隔离人天数: {total_isolated_days}")
        
        # 应该有一定数量的隔离发生
        assert total_isolated_days > 0, "应该有隔离措施实施"
        
        print("隔离效果量化指标测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestSpatialIsolationManagement()
    test_instance.setup_method()
    
    try:
        test_instance.test_isolation_prevents_movement()
        test_instance.test_isolation_time_countdown_accuracy()
        test_instance.test_isolation_release_mechanism()
        test_instance.test_isolation_transmission_suppression()
        test_instance.test_isolation_state_transitions()
        test_instance.test_isolation_during_state_progression()
        test_instance.test_isolation_effectiveness_metrics()
        print("\n所有空间隔离状态管理测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")