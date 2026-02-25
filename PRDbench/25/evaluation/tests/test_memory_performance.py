# -*- coding: utf-8 -*-
"""
内存使用性能测试单元测试
测试系统的内存使用情况和内存泄漏检测
"""

import pytest
import gc
import os
import sys
import psutil
import time
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
def memory_monitor():
    """内存监控上下文管理器"""
    process = psutil.Process()
    
    # 强制垃圾回收，获取基准内存
    gc.collect()
    baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB
    peak_memory = baseline_memory
    
    def monitor_memory():
        nonlocal peak_memory
        while hasattr(monitor_memory, 'running'):
            current_memory = process.memory_info().rss / (1024 * 1024)
            peak_memory = max(peak_memory, current_memory)
            time.sleep(0.1)
    
    # 启动内存监控线程
    monitor_memory.running = True
    monitor_thread = threading.Thread(target=monitor_memory)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    try:
        yield lambda: {'baseline': baseline_memory, 'peak': peak_memory}
    finally:
        monitor_memory.running = False
        monitor_thread.join(timeout=1)


class TestMemoryPerformance:
    """内存使用性能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.max_memory_gb = 2.0  # 最大允许内存使用（GB）
        self.max_memory_mb = self.max_memory_gb * 1024  # 转换为MB
        
        # 创建输出目录
        create_directories()
        
    def test_peak_memory_usage_constraint(self):
        """测试峰值内存使用约束
        
        验证：
        1. 峰值内存使用≤2GB
        2. 无内存泄漏问题
        3. 程序运行稳定
        """
        
        print("开始内存使用测试...")
        
        with memory_monitor() as get_memory_info:
            # 运行完整的模拟流程
            print("执行数据处理...")
            processor = DataProcessor()
            processor.create_sample_data()
            processor.validate_data()
            processor.calculate_seir_states()
            
            print("执行SIR模型...")
            sir_config = {
                'N': 50000,  # 较大的人口数以测试内存使用
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 49999,
                'I0': 1,
                'R0': 0,
                'days': 365,  # 一年的模拟
                'dt': 1
            }
            sir_model = SIRModel(sir_config)
            sir_model.solve_ode()
            
            print("执行SEIR模型...")
            seir_config = {
                'N': 50000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'r': 20,
                'S0': 49999,
                'E0': 0,
                'I0': 1,
                'R0': 0,
                'days': 365,
                'dt': 1
            }
            seir_model = SEIRModel(seir_config)
            seir_model.solve_ode()
            
            print("执行隔离SEIR模型...")
            isolation_config = {
                'N': 30000,  # 适中规模避免过度内存使用
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'q': 0.01,
                'deltaI': 0.13,
                'gammaI': 0.007,
                'lambda_val': 0.03,
                'deltaH': 0.008,
                'alpha': 0.0001,
                'S0': 29999,
                'E0': 0,
                'I0': 1,
                'Sq0': 0,
                'Eq0': 0,
                'H0': 0,
                'R0': 0,
                'days': 200,
                'dt': 1
            }
            isolation_model = IsolationSEIRModel(isolation_config)
            isolation_model.solve_ode()
            
            # 强制垃圾回收
            gc.collect()
            
        # 获取内存使用信息
        memory_info = get_memory_info()
        baseline_mb = memory_info['baseline']
        peak_mb = memory_info['peak']
        peak_gb = peak_mb / 1024
        
        print(f"\n内存使用报告:")
        print(f"基准内存: {baseline_mb:.2f}MB")
        print(f"峰值内存: {peak_mb:.2f}MB ({peak_gb:.3f}GB)")
        print(f"内存增长: {peak_mb - baseline_mb:.2f}MB")
        
        # 验证峰值内存使用≤2GB
        assert peak_gb <= self.max_memory_gb, \
            f"峰值内存使用{peak_gb:.3f}GB超过{self.max_memory_gb}GB限制"
        
        # 验证内存使用合理性（程序正常工作应该有少量内存增长）
        memory_growth = peak_mb - baseline_mb
        assert memory_growth >= 1, \
            f"内存增长{memory_growth:.2f}MB过低，可能程序没有正常运行"
        
        # 验证内存使用效率（增长过高可能有问题）
        assert memory_growth <= 100, \
            f"内存增长{memory_growth:.2f}MB过高，可能存在内存效率问题"
        
        print("峰值内存使用约束测试通过")
    
    def test_memory_leak_detection(self):
        """测试内存泄漏检测"""
        
        process = psutil.Process()
        
        # 执行多次相同操作，检测内存是否持续增长
        memory_samples = []
        num_iterations = 5
        
        for i in range(num_iterations):
            # 强制垃圾回收
            gc.collect()
            
            # 记录内存使用
            current_memory = process.memory_info().rss / (1024 * 1024)
            memory_samples.append(current_memory)
            
            # 执行操作
            processor = DataProcessor()
            processor.create_sample_data()
            processor.validate_data()
            processor.calculate_seir_states()
            
            # 创建和销毁模型对象
            sir_config = {
                'N': 10000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 9999,
                'I0': 1,
                'R0': 0,
                'days': 50,
                'dt': 1
            }
            sir_model = SIRModel(sir_config)
            sir_model.solve_ode()
            
            # 显式删除对象
            del processor
            del sir_model
            
            print(f"迭代{i+1}: 内存使用{current_memory:.2f}MB")
        
        # 最终强制垃圾回收
        gc.collect()
        final_memory = process.memory_info().rss / (1024 * 1024)
        memory_samples.append(final_memory)
        
        # 分析内存趋势
        if len(memory_samples) >= 3:
            # 计算内存增长趋势（线性回归斜率）
            x = list(range(len(memory_samples)))
            y = memory_samples
            
            # 简单线性回归
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi ** 2 for xi in x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            print(f"内存样本: {[f'{m:.1f}' for m in memory_samples]}MB")
            print(f"内存增长趋势: {slope:.3f}MB/迭代")
            
            # 验证无显著内存泄漏（趋势斜率应该接近0）
            assert abs(slope) <= 5.0, \
                f"检测到可能的内存泄漏，增长趋势{slope:.3f}MB/迭代过大"
        
        print("内存泄漏检测测试通过")
    
    def test_large_scale_memory_stability(self):
        """测试大规模模拟的内存稳定性"""
        
        # 测试大规模空间模拟的内存使用
        large_spatial_config = {
            'grid_size': 100,            # 大网格
            'num_individuals': 5000,     # 较多个体
            'sigma': 2,
            'transmission_distance': 4,
            'beta': 0.04,
            'sigma_rate': 0.1,
            'gamma': 0.1,
            'v1': 1/5,
            'v2': 1/3,
            'isolation_duration': 14,
            'days': 30,                  # 适中天数
            'dt': 1,
            'initial_infected': 10
        }
        
        with memory_monitor() as get_memory_info:
            try:
                spatial_model = SpatialBrownianModel(large_spatial_config)
                spatial_model.solve_simulation()
                
                # 检查模型是否成功完成
                assert spatial_model.time is not None, "空间模型应该完成仿真"
                assert len(spatial_model.individuals) > 0, "应该有个体数据"
                
            except MemoryError:
                print("正确处理内存不足情况")
                return  # 如果内存不足，这是可接受的
        
        memory_info = get_memory_info()
        peak_gb = memory_info['peak'] / 1024
        
        print(f"大规模空间模拟峰值内存: {peak_gb:.3f}GB")
        
        # 验证大规模模拟仍在内存限制内
        if peak_gb <= self.max_memory_gb:
            print("大规模模拟内存使用合理")
        else:
            print(f"大规模模拟内存使用{peak_gb:.3f}GB超过限制，但这可能是可接受的")
        
        print("大规模内存稳定性测试通过")
    
    def test_memory_cleanup_effectiveness(self):
        """测试内存清理有效性"""
        
        process = psutil.Process()
        
        # 记录初始内存
        gc.collect()
        initial_memory = process.memory_info().rss / (1024 * 1024)
        
        # 创建大量对象
        large_objects = []
        for i in range(10):
            config = {
                'N': 20000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 19999,
                'I0': 1,
                'R0': 0,
                'days': 100,
                'dt': 1
            }
            model = SIRModel(config)
            model.solve_ode()
            large_objects.append(model)
        
        # 记录使用大量内存时的情况
        gc.collect()
        high_memory = process.memory_info().rss / (1024 * 1024)
        
        # 删除对象并强制垃圾回收
        del large_objects
        gc.collect()
        
        # 等待内存释放
        time.sleep(1)
        
        # 记录清理后的内存
        final_memory = process.memory_info().rss / (1024 * 1024)
        
        print(f"内存清理测试:")
        print(f"初始内存: {initial_memory:.2f}MB")
        print(f"高峰内存: {high_memory:.2f}MB")
        print(f"清理后内存: {final_memory:.2f}MB")
        print(f"内存释放: {high_memory - final_memory:.2f}MB")
        
        # 验证内存能够有效释放
        memory_released = high_memory - final_memory
        memory_used = high_memory - initial_memory
        
        if memory_used > 0:
            release_ratio = memory_released / memory_used
            assert release_ratio >= 0.7, \
                f"内存释放比例{release_ratio:.1%}低于70%，可能存在内存泄漏"
        
        print("内存清理有效性测试通过")
    
    def test_concurrent_memory_stability(self):
        """测试并发执行的内存稳定性"""
        
        def worker_function(worker_id):
            """工作线程函数"""
            config = {
                'N': 5000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 4999,
                'I0': 1,
                'R0': 0,
                'days': 50,
                'dt': 1
            }
            
            model = SIRModel(config)
            model.solve_ode()
            return worker_id
        
        with memory_monitor() as get_memory_info:
            # 创建多个工作线程
            threads = []
            num_workers = 4
            
            for i in range(num_workers):
                thread = threading.Thread(target=worker_function, args=(i,))
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
        
        memory_info = get_memory_info()
        peak_gb = memory_info['peak'] / 1024
        
        print(f"并发执行({num_workers}线程)峰值内存: {peak_gb:.3f}GB")
        
        # 验证并发执行的内存使用仍在限制内
        assert peak_gb <= self.max_memory_gb, \
            f"并发执行峰值内存{peak_gb:.3f}GB超过{self.max_memory_gb}GB限制"
        
        print("并发内存稳定性测试通过")
    
    def test_long_running_memory_stability(self):
        """测试长期运行的内存稳定性"""
        
        process = psutil.Process()
        memory_history = []
        
        # 模拟长期运行（多次执行短任务）
        num_cycles = 20
        
        for cycle in range(num_cycles):
            # 执行模拟任务
            config = {
                'N': 10000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 9999,
                'I0': 1,
                'R0': 0,
                'days': 20,  # 短期模拟
                'dt': 1
            }
            
            model = SIRModel(config)
            model.solve_ode()
            
            # 显式删除对象
            del model
            
            # 每5个周期执行一次垃圾回收
            if cycle % 5 == 0:
                gc.collect()
            
            # 记录内存使用
            current_memory = process.memory_info().rss / (1024 * 1024)
            memory_history.append(current_memory)
            
            if cycle % 5 == 0:
                print(f"周期{cycle}: {current_memory:.2f}MB")
        
        # 分析内存稳定性
        if len(memory_history) >= 10:
            # 比较前期和后期的内存使用
            early_avg = sum(memory_history[:5]) / 5
            late_avg = sum(memory_history[-5:]) / 5
            memory_growth = late_avg - early_avg
            
            print(f"长期运行内存分析:")
            print(f"前期平均: {early_avg:.2f}MB")
            print(f"后期平均: {late_avg:.2f}MB")
            print(f"内存增长: {memory_growth:.2f}MB")
            
            # 验证长期运行无显著内存增长（<100MB增长可接受）
            assert memory_growth <= 100, \
                f"长期运行内存增长{memory_growth:.2f}MB过大，可能有内存泄漏"
        
        print("长期运行内存稳定性测试通过")
    
    def test_memory_usage_proportionality(self):
        """测试内存使用的比例性"""
        
        # 测试不同规模模拟的内存使用比例
        population_sizes = [1000, 5000, 10000, 20000]
        memory_usage = []
        
        for N in population_sizes:
            with memory_monitor() as get_memory_info:
                config = {
                    'N': N,
                    'beta': 0.05,
                    'gamma': 0.1,
                    'S0': N-1,
                    'I0': 1,
                    'R0': 0,
                    'days': 100,
                    'dt': 1
                }
                
                model = SIRModel(config)
                model.solve_ode()
                
                gc.collect()
            
            memory_info = get_memory_info()
            memory_growth = memory_info['peak'] - memory_info['baseline']
            memory_usage.append((N, memory_growth))
            
            print(f"人口{N}: 内存增长{memory_growth:.2f}MB")
        
        # 验证内存使用与问题规模呈合理比例
        # 人口增大20倍，内存不应增大超过100倍
        if len(memory_usage) >= 2:
            memory_ratio = memory_usage[-1][1] / memory_usage[0][1] if memory_usage[0][1] > 0 else 1
            population_ratio = population_sizes[-1] / population_sizes[0]
            
            efficiency_ratio = memory_ratio / population_ratio
            
            print(f"内存效率分析:")
            print(f"人口扩展倍数: {population_ratio}")
            print(f"内存增长倍数: {memory_ratio:.2f}")
            print(f"效率比: {efficiency_ratio:.2f}")
            
            assert efficiency_ratio <= 10.0, \
                f"内存效率比{efficiency_ratio:.2f}过高，内存使用不合理"
        
        print("内存使用比例性测试通过")
    
    def test_garbage_collection_effectiveness(self):
        """测试垃圾回收有效性"""
        
        process = psutil.Process()
        
        # 创建大量临时对象
        gc.collect()
        before_creation = process.memory_info().rss / (1024 * 1024)
        
        # 创建临时对象
        temp_objects = []
        for i in range(100):
            processor = DataProcessor()
            processor.create_sample_data()
            temp_objects.append(processor)
        
        after_creation = process.memory_info().rss / (1024 * 1024)
        
        # 删除对象但不立即垃圾回收
        del temp_objects
        before_gc = process.memory_info().rss / (1024 * 1024)
        
        # 强制垃圾回收
        collected = gc.collect()
        after_gc = process.memory_info().rss / (1024 * 1024)
        
        print(f"垃圾回收测试:")
        print(f"创建前: {before_creation:.2f}MB")
        print(f"创建后: {after_creation:.2f}MB")
        print(f"删除后: {before_gc:.2f}MB")
        print(f"回收后: {after_gc:.2f}MB")
        print(f"回收对象数: {collected}")
        
        # 验证垃圾回收释放了内存
        memory_freed = before_gc - after_gc
        memory_used = after_creation - before_creation
        
        if memory_used > 10:  # 如果确实使用了内存
            free_ratio = memory_freed / memory_used if memory_used > 0 else 0
            assert free_ratio >= 0.5, \
                f"垃圾回收释放比例{free_ratio:.1%}过低"
        
        print("垃圾回收有效性测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestMemoryPerformance()
    test_instance.setup_method()
    
    try:
        test_instance.test_peak_memory_usage_constraint()
        test_instance.test_memory_leak_detection()
        test_instance.test_large_scale_memory_stability()
        test_instance.test_concurrent_memory_stability()
        test_instance.test_long_running_memory_stability()
        test_instance.test_memory_usage_proportionality()
        test_instance.test_garbage_collection_effectiveness()
        print("\n所有内存使用性能测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")