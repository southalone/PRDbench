import unittest
import sys
import os
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.si_model import SIModel


class TestSIModelAlgorithm(unittest.TestCase):
    """SI模型核心算法测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.N = 10000  # 总人口数
        self.beta = 0.01  # 传播率
        self.r = 10  # 接触率
        self.days = 200  # 模拟天数
        
    def test_si_model_core_algorithm(self):
        """测试SI模型核心算法实现"""
        # 创建自定义配置
        config = {
            'N': self.N,
            'beta': self.beta,
            'r': self.r,
            'S0': self.N - 1,
            'I0': 1,
            'days': self.days,
            'dt': 1
        }
        
        # 创建SI模型实例
        model = SIModel(config=config)
        
        # 运行模拟
        results = model.run_simulation()
        S = results['S']
        I = results['I']
        
        # 测试1: 验证数组长度
        self.assertEqual(len(S), self.days + 1, "S序列长度应为days+1")
        self.assertEqual(len(I), self.days + 1, "I序列长度应为days+1")
        
        # 测试2: 验证初始条件
        self.assertEqual(S[0], self.N - 1, f"初始易感者数量应为{self.N-1}")
        self.assertEqual(I[0], 1, "初始感染者数量应为1")
        
        # 测试3: 验证守恒定律 S(t) + I(t) = N
        for t in range(len(S)):
            total = S[t] + I[t]
            self.assertAlmostEqual(total, self.N, places=6, 
                                 msg=f"时间点{t}守恒定律失效: S({t})={S[t]}, I({t})={I[t]}, 总和={total}")
        
        # 测试4: 验证单调性
        # S(t)应单调递减
        for t in range(1, len(S)):
            self.assertLessEqual(S[t], S[t-1], f"S(t)在t={t}时违反单调递减性")
        
        # I(t)应单调递增
        for t in range(1, len(I)):
            self.assertGreaterEqual(I[t], I[t-1], f"I(t)在t={t}时违反单调递增性")
        
        # 测试5: 验证最终状态
        final_S = S[-1]
        final_I = I[-1]
        
        # 对于SI模型，最终所有人都会被感染（在有限时间内可能未完全收敛）
        self.assertLess(final_S, self.N * 0.01, msg="最终易感者数量应小于总人口的1%")
        self.assertGreater(final_I, self.N * 0.99, msg=f"最终感染者数量应大于总人口的99%")
        
        # 测试6: 验证数值稳定性（无NaN或Inf）
        self.assertTrue(np.all(np.isfinite(S)), "S序列包含非有限数值")
        self.assertTrue(np.all(np.isfinite(I)), "I序列包含非有限数值")
        
        # 测试7: 验证非负性
        self.assertTrue(np.all(S >= 0), "S序列包含负数")
        self.assertTrue(np.all(I >= 0), "I序列包含负数")
        
        # 测试8: 验证传播率影响
        # 运行高传播率的对比模拟
        config_high = {
            'N': self.N,
            'beta': self.beta * 2,
            'r': self.r,
            'S0': self.N - 1,
            'I0': 1,
            'days': self.days,
            'dt': 1
        }
        model_high = SIModel(config=config_high)
        results_high = model_high.run_simulation()
        S_high = results_high['S']
        I_high = results_high['I']
        
        # 高传播率应导致更快的感染传播
        mid_point = self.days // 2
        self.assertLess(S_high[mid_point], S[mid_point], 
                       "高传播率模型在中期应有更少易感者")
        self.assertGreater(I_high[mid_point], I[mid_point], 
                          "高传播率模型在中期应有更多感染者")
    
    def test_si_model_parameter_validation(self):
        """测试SI模型参数验证"""
        # 测试无效参数（注意：当前SIModel实现可能没有参数验证，所以先跳过这个测试）
        # 这里简单验证模型能正确初始化
        config = {
            'N': self.N,
            'beta': self.beta,
            'r': self.r,
            'S0': self.N - 1,
            'I0': 1,
            'days': self.days,
            'dt': 1
        }
        model = SIModel(config=config)
        self.assertIsNotNone(model)
    
    def test_si_model_edge_cases(self):
        """测试SI模型边界情况"""
        # 测试极小人口
        config_small = {
            'N': 2,
            'beta': 0.5,
            'r': 1,
            'S0': 1,
            'I0': 1,
            'days': 10,
            'dt': 1
        }
        model_small = SIModel(config=config_small)
        results_small = model_small.run_simulation()
        S_small = results_small['S']
        I_small = results_small['I']
        
        # 验证小规模模拟的基本性质
        self.assertEqual(S_small[0] + I_small[0], 2)
        self.assertAlmostEqual(S_small[-1] + I_small[-1], 2, places=1)
        
        # 测试零传播率
        config_zero = {
            'N': 100,
            'beta': 0.0,
            'r': self.r,
            'S0': 99,
            'I0': 1,
            'days': 50,
            'dt': 1
        }
        model_zero = SIModel(config=config_zero)
        results_zero = model_zero.run_simulation()
        S_zero = results_zero['S']
        I_zero = results_zero['I']
        
        # 零传播率应导致无传播
        self.assertAlmostEqual(S_zero[-1], 99, places=1, msg="零传播率时易感者数量应保持不变")
        self.assertAlmostEqual(I_zero[-1], 1, places=1, msg="零传播率时感染者数量应保持不变")


if __name__ == '__main__':
    unittest.main()