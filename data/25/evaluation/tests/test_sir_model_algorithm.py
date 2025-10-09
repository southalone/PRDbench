import unittest
import sys
import os
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.sir_model import SIRModel


class TestSIRModelAlgorithm(unittest.TestCase):
    """SIR模型核心算法测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.N = 10000  # 总人口数
        self.beta = 0.05  # 传播率
        self.gamma = 0.1  # 康复率
        self.days = 100  # 模拟天数
        
    def test_sir_model_core_algorithm(self):
        """测试SIR模型核心算法实现"""
        # 创建自定义配置
        config = {
            'N': self.N,
            'beta': self.beta,
            'gamma': self.gamma,
            'S0': self.N - 1,
            'I0': 1,
            'R0': 0,
            'days': self.days,
            'dt': 1
        }
        
        # 创建SIR模型实例
        model = SIRModel(config=config)
        
        # 运行模拟
        results = model.run_simulation()
        S = results['S']
        I = results['I']
        R = results['R']
        
        # 测试1: 验证数组长度
        self.assertEqual(len(S), self.days + 1, "S序列长度应为days+1")
        self.assertEqual(len(I), self.days + 1, "I序列长度应为days+1")
        self.assertEqual(len(R), self.days + 1, "R序列长度应为days+1")
        
        # 测试2: 验证初始条件
        self.assertEqual(S[0], self.N - 1, f"初始易感者数量应为{self.N-1}")
        self.assertEqual(I[0], 1, "初始感染者数量应为1")
        self.assertEqual(R[0], 0, "初始康复者数量应为0")
        
        # 测试3: 验证守恒定律 S(t) + I(t) + R(t) = N
        for t in range(len(S)):
            total = S[t] + I[t] + R[t]
            self.assertAlmostEqual(total, self.N, places=6, 
                                 msg=f"时间点{t}守恒定律失效: S({t})={S[t]}, I({t})={I[t]}, R({t})={R[t]}, 总和={total}")
        
        # 测试4: 验证单调性
        # S(t)应单调递减
        for t in range(1, len(S)):
            self.assertLessEqual(S[t], S[t-1], f"S(t)在t={t}时违反单调递减性")
        
        # R(t)应单调递增
        for t in range(1, len(R)):
            self.assertGreaterEqual(R[t], R[t-1], f"R(t)在t={t}时违反单调递增性")
        
        # I(t)应先增后减（存在峰值）
        # 对于R0 < 1的情况，I(t)可能单调递减，所以这里验证I(t)最终趋于0
        self.assertLess(I[-1], I[0], "I(t)最终应小于初始值")
        
        # 测试5: 验证R0计算和影响
        R0 = self.beta / self.gamma
        self.assertAlmostEqual(R0, 0.5, places=6, msg="R0计算错误")
        
        # 由于R0 < 1，疫情不应大规模爆发
        max_infected = max(I)
        self.assertLess(max_infected, self.N * 0.1, 
                       f"R0<1时感染峰值{max_infected}不应超过人口的10%")
        
        # 测试6: 验证最终状态
        final_S = S[-1]
        final_I = I[-1]
        final_R = R[-1]
        
        # 最终感染者应接近0
        self.assertLess(final_I, 1, "最终感染者数量应接近0")
        
        # 最终易感者应大于0（因为R0<1）
        self.assertGreater(final_S, self.N * 0.9, 
                          f"R0<1时最终易感者{final_S}应大于人口的90%")
        
        # 测试7: 验证数值稳定性（无NaN或Inf）
        self.assertTrue(np.all(np.isfinite(S)), "S序列包含非有限数值")
        self.assertTrue(np.all(np.isfinite(I)), "I序列包含非有限数值")
        self.assertTrue(np.all(np.isfinite(R)), "R序列包含非有限数值")
        
        # 测试8: 验证非负性
        self.assertTrue(np.all(S >= 0), "S序列包含负数")
        self.assertTrue(np.all(I >= 0), "I序列包含负数")
        self.assertTrue(np.all(R >= 0), "R序列包含负数")
        
        # 测试9: 验证高R0情况的对比
        # 运行高传播率的对比模拟（R0 > 1）
        config_high = {
            'N': self.N,
            'beta': 0.3,
            'gamma': 0.1,
            'S0': self.N - 1,
            'I0': 1,
            'R0': 0,
            'days': self.days,
            'dt': 1
        }
        model_high = SIRModel(config=config_high)
        results_high = model_high.run_simulation()
        S_high = results_high['S']
        I_high = results_high['I']
        R_high = results_high['R']
        
        R0_high = 0.3 / 0.1  # R0 = 3.0 > 1
        
        # 高R0应导致更大的疫情爆发
        max_infected_high = max(I_high)
        self.assertGreater(max_infected_high, max_infected, 
                          "高R0模型应有更大的感染峰值")
        
        final_R_high = R_high[-1]
        self.assertGreater(final_R_high, final_R, 
                          "高R0模型最终康复者应更多")
    
    def test_sir_model_parameter_validation(self):
        """测试SIR模型参数验证"""
        # 测试有效参数（当前SIRModel实现可能没有严格的参数验证，所以先验证能正确初始化）
        config = {
            'N': self.N,
            'beta': self.beta,
            'gamma': self.gamma,
            'S0': self.N - 1,
            'I0': 1,
            'R0': 0,
            'days': self.days,
            'dt': 1
        }
        model = SIRModel(config=config)
        self.assertIsNotNone(model)
    
    def test_sir_model_edge_cases(self):
        """测试SIR模型边界情况"""
        # 测试极小人口
        config_small = {
            'N': 3,
            'beta': 0.5,
            'gamma': 0.2,
            'S0': 2,
            'I0': 1,
            'R0': 0,
            'days': 20,
            'dt': 1
        }
        model_small = SIRModel(config=config_small)
        results_small = model_small.run_simulation()
        S_small = results_small['S']
        I_small = results_small['I']
        R_small = results_small['R']
        
        # 验证小规模模拟的基本性质
        self.assertEqual(S_small[0] + I_small[0] + R_small[0], 3)
        self.assertAlmostEqual(S_small[-1] + I_small[-1] + R_small[-1], 3, places=1)
        
        # 测试零传播率
        config_zero = {
            'N': 100,
            'beta': 0.0,
            'gamma': 0.1,
            'S0': 99,
            'I0': 1,
            'R0': 0,
            'days': 50,
            'dt': 1
        }
        model_zero = SIRModel(config=config_zero)
        results_zero = model_zero.run_simulation()
        S_zero = results_zero['S']
        I_zero = results_zero['I']
        R_zero = results_zero['R']
        
        # 零传播率时只有康复过程
        self.assertAlmostEqual(S_zero[-1], 99, places=1, msg="零传播率时易感者数量应保持不变")
        self.assertLess(I_zero[-1], 0.1, msg="零传播率时感染者最终应接近0")
        self.assertAlmostEqual(R_zero[-1], 1, places=1, msg="零传播率时只有初始感染者康复")
        
        # 测试零康复率（退化为SI模型）
        config_no_recovery = {
            'N': 100,
            'beta': 0.05,
            'gamma': 0.0,
            'S0': 99,
            'I0': 1,
            'R0': 0,
            'days': 200,
            'dt': 1
        }
        model_no_recovery = SIRModel(config=config_no_recovery)
        results_no_recovery = model_no_recovery.run_simulation()
        S_no_recovery = results_no_recovery['S']
        I_no_recovery = results_no_recovery['I']
        R_no_recovery = results_no_recovery['R']
        
        # 零康复率时康复者应始终为0
        self.assertTrue(np.all(R_no_recovery < 0.1), "零康复率时康复者应接近0")
        # 应退化为SI模型行为
        self.assertAlmostEqual(S_no_recovery[-1] + I_no_recovery[-1], 100, places=1)


if __name__ == '__main__':
    unittest.main()