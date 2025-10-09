# -*- coding: utf-8 -*-
"""
运行时间性能测试单元测试
测试系统各模块的运行时间性能
"""

import pytest
import time
import numpy as np
import os
import sys
import psutil
import threading
from contextlib import contextmanager

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processing import DataProcessor
from models.sir_model import SIRModel
from models.seir_model import SEIRModel
from models.isolation_seir_model import IsolationSEIRModel
from models.spatial_brownian_model import SpatialBrownianModel
from utils import create_directories


@contextmanager
def performance_timer():
    """性能计时器上下文管理器"""
    start_time = time.time()
    yield lambda: time.time() - start_time
    end_time = time.time()


class TestRuntimePerformance:
    """运行时间性能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.max_acceptable_time = 30  # 最大可接受运行时间（秒）
        self.long_simulation_days = 200  # 长时间序列模拟天数
        
    def test_complete_simulation_runtime(self):
        """测试完整模拟运行时间
        
        验证：
        1. 单次完整模拟运行时间≤30秒
        2. 支持≥200天长时间序列模拟
        """
        
        print("开始完整模拟性能测试...")
        
        # 确保输出目录存在
        create_directories()
        
        with performance_timer() as get_elapsed:
            # 1. 数据处理性能测试
            print("测试数据处理性能...")
            data_start = time.time()
            
            processor = DataProcessor()
            processor.create_sample_data()
            processor.validate_data()
            processor.calculate_seir_states()
            processor.save_processed_data()
            
            data_time = time.time() - data_start
            print(f"数据处理用时: {data_time:.2f}秒")
            
            # 2. SIR模型性能测试
            print("测试SIR模型性能...")
            sir_start = time.time()
            
            sir_config = {
                'N': 10000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 9999,
                'I0': 1,
                'R0': 0,
                'days': self.long_simulation_days,  # 200天长时间序列
                'dt': 1
            }
            
            sir_model = SIRModel(sir_config)
            sir_model.solve_ode()
            sir_model.plot_results()
            
            sir_time = time.time() - sir_start
            print(f"SIR模型用时: {sir_time:.2f}秒")
            
            # 3. SEIR模型性能测试
            print("测试SEIR模型性能...")
            seir_start = time.time()
            
            seir_config = {
                'N': 10000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'r': 20,                 # 添加接触率参数
                'S0': 9999,
                'E0': 0,
                'I0': 1,
                'R0': 0,
                'days': self.long_simulation_days,  # 200天长时间序列
                'dt': 1
            }
            
            seir_model = SEIRModel(seir_config)
            seir_model.solve_ode()
            seir_model.plot_results()
            
            seir_time = time.time() - seir_start
            print(f"SEIR模型用时: {seir_time:.2f}秒")
            
            # 4. 隔离SEIR模型性能测试（相对复杂）
            print("测试隔离SEIR模型性能...")
            isolation_start = time.time()
            
            isolation_config = {
                'N': 10000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'q': 0.01,
                'deltaI': 0.13,
                'gammaI': 0.007,
                'lambda_val': 0.03,
                'deltaH': 0.008,
                'alpha': 0.0001,
                'S0': 9999,
                'E0': 0,
                'I0': 1,
                'Sq0': 0,
                'Eq0': 0,
                'H0': 0,
                'R0': 0,
                'days': 100,  # 适中的天数
                'dt': 1
            }
            
            isolation_model = IsolationSEIRModel(isolation_config)
            isolation_model.solve_ode()
            isolation_model.plot_results()
            
            isolation_time = time.time() - isolation_start
            print(f"隔离SEIR模型用时: {isolation_time:.2f}秒")
        
        # 计算总运行时间
        total_time = get_elapsed()
        
        print(f"\n性能测试结果:")
        print(f"数据处理: {data_time:.2f}秒")
        print(f"SIR模型({self.long_simulation_days}天): {sir_time:.2f}秒")
        print(f"SEIR模型({self.long_simulation_days}天): {seir_time:.2f}秒")
        print(f"隔离SEIR模型(100天): {isolation_time:.2f}秒")
        print(f"总运行时间: {total_time:.2f}秒")
        
        # 验证性能要求
        assert total_time <= self.max_acceptable_time, \
            f"完整模拟运行时间{total_time:.2f}秒超过限制{self.max_acceptable_time}秒"
        
        # 验证支持长时间序列模拟
        assert sir_config['days'] >= 200, f"应支持≥200天模拟，实际支持{sir_config['days']}天"
        assert seir_config['days'] >= 200, f"应支持≥200天模拟，实际支持{seir_config['days']}天"
        
        print("完整模拟运行时间性能测试通过")
    
    def test_individual_component_performance(self):
        """测试各个组件的单独性能"""
        
        # 测试数据处理组件性能
        with performance_timer() as get_elapsed:
            processor = DataProcessor()
            processor.create_sample_data()
        
        data_creation_time = get_elapsed()
        assert data_creation_time <= 5.0, \
            f"数据创建用时{data_creation_time:.2f}秒超过5秒限制"
        
        # 测试数据验证性能
        with performance_timer() as get_elapsed:
            processor.validate_data()
        
        validation_time = get_elapsed()
        assert validation_time <= 2.0, \
            f"数据验证用时{validation_time:.2f}秒超过2秒限制"
        
        # 测试SEIR状态计算性能
        with performance_timer() as get_elapsed:
            processor.calculate_seir_states()
        
        calculation_time = get_elapsed()
        assert calculation_time <= 3.0, \
            f"SEIR计算用时{calculation_time:.2f}秒超过3秒限制"
        
        print(f"组件性能测试:")
        print(f"数据创建: {data_creation_time:.2f}秒")
        print(f"数据验证: {validation_time:.2f}秒")
        print(f"SEIR计算: {calculation_time:.2f}秒")
        
        print("组件性能测试通过")
    
    def test_scalability_performance(self):
        """测试系统扩展性能（不同规模数据）"""
        
        population_sizes = [1000, 5000, 10000, 20000]
        performance_results = []
        
        for N in population_sizes:
            config = {
                'N': N,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': N-1,
                'I0': 1,
                'R0': 0,
                'days': 50,  # 固定天数以比较扩展性
                'dt': 1
            }
            
            with performance_timer() as get_elapsed:
                model = SIRModel(config)
                model.solve_ode()
            
            runtime = get_elapsed()
            performance_results.append((N, runtime))
            print(f"人口{N}: {runtime:.2f}秒")
        
        # 验证扩展性合理（时间复杂度不应过高）
        # 人口增加20倍，时间不应增加超过100倍
        time_ratio = performance_results[-1][1] / performance_results[0][1]
        population_ratio = population_sizes[-1] / population_sizes[0]
        
        efficiency_ratio = time_ratio / population_ratio
        
        print(f"扩展性分析:")
        print(f"人口扩展倍数: {population_ratio}")
        print(f"时间增长倍数: {time_ratio:.2f}")
        print(f"效率比: {efficiency_ratio:.2f}")
        
        assert efficiency_ratio <= 5.0, \
            f"扩展性效率比{efficiency_ratio:.2f}过高，系统扩展性不佳"
        
        print("扩展性能测试通过")
    
    def test_long_duration_simulation_performance(self):
        """测试长时间模拟的性能稳定性"""
        
        # 测试不同天数的模拟性能
        day_configs = [50, 100, 200, 365]  # 包含一年的模拟
        
        for days in day_configs:
            config = {
                'N': 10000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'S0': 9999,
                'E0': 0,
                'I0': 1,
                'R0': 0,
                'days': days,
                'dt': 1
            }
            
            with performance_timer() as get_elapsed:
                model = SEIRModel(config)
                model.solve_ode()
            
            runtime = get_elapsed()
            time_per_day = runtime / days
            
            print(f"{days}天模拟: {runtime:.2f}秒 (每天{time_per_day:.4f}秒)")
            
            # 验证时间复杂度基本线性
            assert time_per_day <= 0.1, \
                f"{days}天模拟每天用时{time_per_day:.4f}秒过长"
            
            # 验证长时间模拟仍在可接受范围内
            if days >= 200:
                assert runtime <= self.max_acceptable_time, \
                    f"{days}天模拟用时{runtime:.2f}秒超过{self.max_acceptable_time}秒限制"
        
        print("长时间模拟性能测试通过")
    
    def test_concurrent_performance(self):
        """测试并发性能（多个模型同时运行）"""
        
        def run_sir_model(model_id):
            """运行SIR模型的函数"""
            config = {
                'N': 5000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 4999,
                'I0': 1,
                'R0': 0,
                'days': 100,
                'dt': 1
            }
            
            model = SIRModel(config)
            start_time = time.time()
            model.solve_ode()
            end_time = time.time()
            
            return model_id, end_time - start_time
        
        # 测试顺序执行
        sequential_start = time.time()
        sequential_results = []
        for i in range(3):
            model_id, runtime = run_sir_model(i)
            sequential_results.append(runtime)
        sequential_total = time.time() - sequential_start
        
        # 测试并发执行
        concurrent_start = time.time()
        threads = []
        concurrent_results = []
        
        def thread_wrapper(model_id):
            result = run_sir_model(model_id)
            concurrent_results.append(result[1])
        
        for i in range(3):
            thread = threading.Thread(target=thread_wrapper, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        concurrent_total = time.time() - concurrent_start
        
        print(f"性能对比:")
        print(f"顺序执行: {sequential_total:.2f}秒")
        print(f"并发执行: {concurrent_total:.2f}秒")
        print(f"加速比: {sequential_total/concurrent_total:.2f}x")
        
        # 验证并发执行有性能提升（至少节省20%时间）
        speedup = sequential_total / concurrent_total
        assert speedup >= 1.2, f"并发执行加速比{speedup:.2f}低于1.2"
        
        print("并发性能测试通过")
    
    def test_performance_consistency(self):
        """测试性能一致性（多次运行结果稳定）"""
        
        config = {
            'N': 10000,
            'beta': 0.05,
            'gamma': 0.1,
            'S0': 9999,
            'I0': 1,
            'R0': 0,
            'days': 100,
            'dt': 1
        }
        
        # 多次运行相同配置
        runtimes = []
        num_runs = 5
        
        for run in range(num_runs):
            with performance_timer() as get_elapsed:
                model = SIRModel(config)
                model.solve_ode()
            
            runtime = get_elapsed()
            runtimes.append(runtime)
            print(f"第{run+1}次运行: {runtime:.2f}秒")
        
        # 计算性能统计
        mean_time = np.mean(runtimes)
        std_time = np.std(runtimes)
        cv = std_time / mean_time  # 变异系数
        
        print(f"性能统计:")
        print(f"平均时间: {mean_time:.2f}秒")
        print(f"标准差: {std_time:.2f}秒")
        print(f"变异系数: {cv:.2f}")
        
        # 验证性能一致性（变异系数应小于20%）
        assert cv <= 0.2, f"性能变异系数{cv:.2f}过高，性能不稳定"
        
        # 验证所有运行都在可接受时间内
        for i, runtime in enumerate(runtimes):
            assert runtime <= self.max_acceptable_time, \
                f"第{i+1}次运行用时{runtime:.2f}秒超过限制"
        
        print("性能一致性测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestRuntimePerformance()
    test_instance.setup_method()
    
    try:
        test_instance.test_complete_simulation_runtime()
        test_instance.test_individual_component_performance()
        test_instance.test_scalability_performance()
        test_instance.test_long_duration_simulation_performance()
        test_instance.test_concurrent_performance()
        test_instance.test_performance_consistency()
        print("\n所有运行时间性能测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")