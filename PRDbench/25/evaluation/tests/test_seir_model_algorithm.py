import unittest
import sys
import os
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.seir_model import SEIRModel


class TestSEIRModelAlgorithm(unittest.TestCase):
    """SEIR模型核心算法测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.N = 10000  # 总人口数
        self.beta = 0.03  # 传播率
        self.sigma = 0.1  # 潜伏期转感染率
        self.gamma = 0.1  # 康复率
        self.days = 160  # 模拟天数
        
    def test_seir_model_core_algorithm(self):
        """测试SEIR模型核心算法实现"""
        # 创建SEIR模型实例（使用默认配置）
        model = SEIRModel()
        
        # 运行模拟并获取结果
        results = model.run_simulation()
        
        # 提取时间序列数据
        S = results['S']
        E = results['E']
        I = results['I']
        R = results['R']
        time = results['time']
        
        # 获取配置参数
        N = model.N
        days = len(time) - 1
        
        # 测试1: 验证数组长度
        self.assertEqual(len(S), days + 1, f"S序列长度应为{days + 1}")
        self.assertEqual(len(E), days + 1, f"E序列长度应为{days + 1}")
        self.assertEqual(len(I), days + 1, f"I序列长度应为{days + 1}")
        self.assertEqual(len(R), days + 1, f"R序列长度应为{days + 1}")
        
        # 测试2: 验证初始条件
        self.assertEqual(S[0], N - 1, f"初始易感者数量应为{N-1}")
        self.assertEqual(E[0], 0, "初始潜伏者数量应为0")
        self.assertEqual(I[0], 1, "初始感染者数量应为1")
        self.assertEqual(R[0], 0, "初始康复者数量应为0")
        
        # 测试3: 验证守恒定律 S(t) + E(t) + I(t) + R(t) = N
        for t in range(len(S)):
            total = S[t] + E[t] + I[t] + R[t]
            self.assertAlmostEqual(total, N, places=6,
                                 msg=f"时间点{t}守恒定律失效: 总和={total}")
        
        # 测试4: 验证单调性
        # S(t)应单调递减
        for t in range(1, len(S)):
            self.assertLessEqual(S[t], S[t-1], f"S(t)在t={t}时违反单调递减性")
        
        # R(t)应单调递增
        for t in range(1, len(R)):
            self.assertGreaterEqual(R[t], R[t-1], f"R(t)在t={t}时违反单调递增性")
        
        # 测试5: 验证SEIR特有的四状态转换逻辑
        # E(t)和I(t)都应先增后减，存在峰值
        E_peak_idx = np.argmax(E)
        I_peak_idx = np.argmax(I)
        
        # 潜伏者峰值应在感染者峰值之前
        self.assertLessEqual(E_peak_idx, I_peak_idx,
                           "潜伏者峰值应在感染者峰值之前或同时出现")
        
        # 测试6: 验证R0对疫情的影响
        R0 = results['R0_basic']
        self.assertGreater(R0, 1, f"R0={R0}应大于1")
        
        # 由于R0 > 1，疫情应大规模爆发
        max_infected = max(I)
        final_attack_rate = R[-1] / N
        
        self.assertGreater(final_attack_rate, 0.8,
                          f"R0>1时最终侵袭率{final_attack_rate:.3f}应>80%")
        
        # 测试7: 验证最终状态
        final_S = S[-1]
        final_E = E[-1]
        final_I = I[-1]
        final_R = R[-1]
        
        # 最终潜伏者和感染者应接近0
        self.assertLess(final_E, 10, "最终潜伏者数量应很小")
        self.assertLess(final_I, 10, "最终感染者数量应很小")
        
        # 最终康复者应占绝大多数
        self.assertGreater(final_R, N * 0.8,
                          f"最终康复者{final_R}应占人口80%以上")
        
        # 测试8: 验证数值稳定性（无NaN或Inf）
        for state, name in [(S, 'S'), (E, 'E'), (I, 'I'), (R, 'R')]:
            self.assertTrue(np.all(np.isfinite(state)), f"{name}序列包含非有限数值")
            self.assertTrue(np.all(state >= 0), f"{name}序列包含负数")
            
        # 测试9: 验证模型基本特征（简化测试）
        # 验证E和I峰值的存在
        E_max = max(E)
        I_max = max(I)
        
        self.assertGreater(E_max, 0, "潜伏者应存在峰值")
        self.assertGreater(I_max, 0, "感染者应存在峰值")
        
        # 验证模型收敛
        self.assertLess(E[-1], E_max * 0.1, "最终潜伏者数量应远小于峰值")
        self.assertLess(I[-1], I_max * 0.1, "最终感染者数量应远小于峰值")
    
    def test_seir_model_basic_properties(self):
        """测试SEIR模型基本特性"""
        # 创建模型实例并运行
        model = SEIRModel()
        results = model.run_simulation()
        
        # 验证结果包含必要的键
        required_keys = ['S', 'E', 'I', 'R', 'time', 'R0_basic']
        for key in required_keys:
            self.assertIn(key, results, f"结果应包含{key}字段")
        
        # 验证R0计算
        R0 = results['R0_basic']
        self.assertGreater(R0, 0, "R0应为正数")
        self.assertIsInstance(R0, (int, float), "R0应为数值类型")


if __name__ == '__main__':
    unittest.main()