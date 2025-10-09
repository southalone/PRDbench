# -*- coding: utf-8 -*-
"""
隔离效果数值验证单元测试
测试隔离机制对感染传播的数值影响
"""

import pytest
import numpy as np
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.isolation_seir_model import IsolationSEIRModel


class TestIsolationEffectiveness:
    """隔离效果数值验证测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 基准配置（无隔离）
        self.base_config = {
            'N': 10000,
            'beta': 0.3,                 # 增加传播率使疫情能够传播
            'sigma': 0.2,                # 增加潜伏期转换率
            'gamma': 0.1,
            'q': 0.0,                    # 无隔离
            'deltaI': 0.0,
            'gammaI': 0.0,
            'lambda_val': 0.0,
            'deltaH': 0.0,
            'alpha': 0.0,
            'S0': 9990,                  # 减少初始易感者，增加初始感染者
            'E0': 5,                     # 增加初始潜伏者
            'I0': 5,                     # 增加初始感染者
            'Sq0': 0,
            'Eq0': 0,
            'H0': 0,
            'R0': 0,
            'days': 100,                 # 增加模拟天数
            'dt': 1
        }
        
        # 隔离配置
        self.isolation_config = self.base_config.copy()
        self.isolation_config.update({
            'q': 0.01,                   # 增加隔离率
            'deltaI': 0.13,              # 住院率
            'gammaI': 0.007,             # 住院康复率
            'lambda_val': 0.03,          # 隔离传播率
            'deltaH': 0.008,             # 出院率
            'alpha': 0.0001              # 死亡率
        })
        
    def test_isolation_reduces_infection_peak(self):
        """测试隔离措施显著降低感染峰值
        
        验证：
        1. 隔离措施显著降低感染峰值（相比无隔离情况降低≥30%）
        2. 隔离人群数量合理增长
        """
        
        # 运行无隔离模型
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        # 运行隔离模型
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # 计算感染峰值
        base_peak = np.max(base_model.I)
        isolation_peak = np.max(isolation_model.I)
        
        # 计算峰值降低率
        reduction_rate = (base_peak - isolation_peak) / base_peak
        
        print(f"无隔离感染峰值: {base_peak:.0f}")
        print(f"隔离感染峰值: {isolation_peak:.0f}")
        print(f"峰值降低率: {reduction_rate:.1%}")
        
        # 验证隔离措施显著降低感染峰值（≥30%）
        assert reduction_rate >= 0.30, \
            f"隔离措施应降低感染峰值≥30%，实际降低{reduction_rate:.1%}"
        
        # 验证隔离人群数量合理增长
        max_hospitalized = np.max(isolation_model.H)
        max_isolated_susceptible = np.max(isolation_model.Sq)
        max_isolated_exposed = np.max(isolation_model.Eq)
        
        total_isolated = max_hospitalized + max_isolated_susceptible + max_isolated_exposed
        
        # 隔离人群应该占总人口的合理比例
        isolation_rate = total_isolated / self.isolation_config['N']
        assert 0.001 <= isolation_rate <= 0.8, \
            f"隔离人群比例{isolation_rate:.1%}不在合理范围[0.1%, 80%]内"
        
        print(f"最大住院人数: {max_hospitalized:.0f}")
        print(f"最大隔离易感者: {max_isolated_susceptible:.0f}")
        print(f"最大隔离潜伏者: {max_isolated_exposed:.0f}")
        print(f"总隔离人群比例: {isolation_rate:.1%}")
        
        print("隔离效果数值验证测试通过")
    
    def test_isolation_delays_epidemic_progression(self):
        """测试隔离措施延缓疫情发展"""
        
        # 运行两个模型
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # 找到感染峰值出现的时间
        base_peak_time = np.argmax(base_model.I)
        isolation_peak_time = np.argmax(isolation_model.I)
        
        print(f"无隔离峰值时间: 第{base_peak_time}天")
        print(f"隔离峰值时间: 第{isolation_peak_time}天")
        
        # 隔离应该延缓疫情高峰
        time_delay = isolation_peak_time - base_peak_time
        assert time_delay >= 0, \
            f"隔离措施应延缓疫情高峰，但提前了{-time_delay}天"
        
        print(f"疫情高峰延缓: {time_delay}天")
        
        # 验证最终累积感染率降低
        base_final_attack_rate = (self.base_config['N'] - base_model.S[-1]) / self.base_config['N']
        isolation_final_attack_rate = (self.isolation_config['N'] - isolation_model.S[-1]) / self.isolation_config['N']
        
        attack_rate_reduction = base_final_attack_rate - isolation_final_attack_rate
        
        print(f"无隔离最终侵袭率: {base_final_attack_rate:.1%}")
        print(f"隔离最终侵袭率: {isolation_final_attack_rate:.1%}")
        print(f"侵袭率降低: {attack_rate_reduction:.1%}")
        
        assert attack_rate_reduction >= 0, \
            "隔离措施应该降低最终侵袭率"
        
        print("疫情发展延缓测试通过")
    
    def test_isolation_compartments_dynamics(self):
        """测试隔离舱室的动态变化"""
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # 验证隔离舱室的合理性
        # 1. 隔离易感者数量
        Sq = isolation_model.Sq
        assert np.all(Sq >= 0), "隔离易感者数量不能为负"
        assert np.max(Sq) > 0, "隔离易感者数量应该有增长"
        
        # 2. 隔离潜伏者数量
        Eq = isolation_model.Eq
        assert np.all(Eq >= 0), "隔离潜伏者数量不能为负"
        
        # 3. 住院者数量
        H = isolation_model.H
        assert np.all(H >= 0), "住院者数量不能为负"
        assert np.max(H) > 0, "住院者数量应该有增长"
        
        # 4. 验证舱室总和守恒
        total_population = isolation_model.S + isolation_model.Sq + isolation_model.E + isolation_model.Eq + isolation_model.I + isolation_model.H + isolation_model.R
        expected_total = self.isolation_config['N']
        
        for t in range(len(total_population)):
            assert abs(total_population[t] - expected_total) < 1e-6, \
                f"第{t}天人口总数不守恒: {total_population[t]} ≠ {expected_total}"
        
        print("隔离舱室动态变化测试通过")
    
    def test_isolation_parameters_sensitivity(self):
        """测试隔离参数的敏感性"""
        
        # 测试不同隔离率的影响
        isolation_rates = [0.0, 0.000001, 0.00001, 0.0001]
        peak_infections = []
        
        for q in isolation_rates:
            config = self.base_config.copy()
            config.update({
                'q': q,
                'deltaI': 0.13,
                'gammaI': 0.007,
                'lambda_val': 0.03,
                'deltaH': 0.008,
                'alpha': 0.0001
            })
            
            model = IsolationSEIRModel(config)
            model.solve_ode()
            peak_infections.append(np.max(model.I))
        
        # 验证隔离率越高，感染峰值越低
        for i in range(len(isolation_rates) - 1):
            if isolation_rates[i+1] > isolation_rates[i]:
                assert peak_infections[i+1] <= peak_infections[i], \
                    f"更高的隔离率应该导致更低的感染峰值"
        
        print("隔离参数敏感性测试通过")
    
    def test_isolation_effectiveness_metrics(self):
        """测试隔离效果的量化指标"""
        
        # 运行基准和隔离模型
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # 计算多个效果指标
        metrics = {}
        
        # 1. 峰值降低率
        base_peak = np.max(base_model.I)
        isolation_peak = np.max(isolation_model.I)
        metrics['peak_reduction'] = (base_peak - isolation_peak) / base_peak
        
        # 2. 最终侵袭率降低
        base_attack_rate = (self.base_config['N'] - base_model.S[-1]) / self.base_config['N']
        isolation_attack_rate = (self.isolation_config['N'] - isolation_model.S[-1]) / self.isolation_config['N']
        metrics['attack_rate_reduction'] = base_attack_rate - isolation_attack_rate
        
        # 3. 疫情持续时间变化
        # 定义疫情结束为感染者数量低于初始值
        base_duration = len(base_model.I)
        isolation_duration = len(isolation_model.I)
        metrics['duration_change'] = isolation_duration - base_duration
        
        # 4. 累积感染人数降低
        base_cumulative = np.sum(np.diff(np.concatenate([[0], base_model.R])))
        isolation_cumulative = np.sum(np.diff(np.concatenate([[0], isolation_model.R])))
        metrics['cumulative_reduction'] = (base_cumulative - isolation_cumulative) / base_cumulative
        
        # 验证指标合理性
        assert metrics['peak_reduction'] >= 0.30, \
            f"峰值降低率{metrics['peak_reduction']:.1%}应≥30%"
        
        assert metrics['attack_rate_reduction'] >= 0, \
            f"侵袭率应该降低，实际变化{metrics['attack_rate_reduction']:.1%}"
        
        print(f"隔离效果指标:")
        print(f"  峰值降低率: {metrics['peak_reduction']:.1%}")
        print(f"  侵袭率降低: {metrics['attack_rate_reduction']:.1%}")
        print(f"  持续时间变化: {metrics['duration_change']}天")
        print(f"  累积感染降低: {metrics['cumulative_reduction']:.1%}")
        
        print("隔离效果量化指标测试通过")
    
    def test_isolation_cost_benefit_analysis(self):
        """测试隔离措施的成本效益分析"""
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # 计算隔离"成本"（隔离的人数）
        total_isolated_person_days = (
            np.sum(isolation_model.Sq) +  # 隔离易感者人天
            np.sum(isolation_model.Eq) +  # 隔离潜伏者人天
            np.sum(isolation_model.H)     # 住院者人天
        )
        
        # 计算隔离"收益"（避免的感染）
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        base_final_infected = self.base_config['N'] - base_model.S[-1]
        isolation_final_infected = self.isolation_config['N'] - isolation_model.S[-1]
        infections_prevented = base_final_infected - isolation_final_infected
        
        # 计算效益比
        if total_isolated_person_days > 0:
            cost_effectiveness = infections_prevented / (total_isolated_person_days / len(isolation_model.S))
            
            # 成本效益应该合理（每隔离一个人天应该能预防合理数量的感染）
            assert cost_effectiveness > 0, "隔离措施应该有正面效益"
            
            print(f"隔离人天数: {total_isolated_person_days:.0f}")
            print(f"预防感染数: {infections_prevented:.0f}")
            print(f"成本效益比: {cost_effectiveness:.3f}")
        
        print("隔离成本效益分析测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestIsolationEffectiveness()
    test_instance.setup_method()
    
    try:
        test_instance.test_isolation_reduces_infection_peak()
        test_instance.test_isolation_delays_epidemic_progression()
        test_instance.test_isolation_compartments_dynamics()
        test_instance.test_isolation_parameters_sensitivity()
        test_instance.test_isolation_effectiveness_metrics()
        test_instance.test_isolation_cost_benefit_analysis()
        print("\n所有隔离效果数值验证测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")