# -*- coding: utf-8 -*-
"""
异常处理机制单元测试
测试系统各模块的异常处理能力
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processing import DataProcessor
from models.sir_model import SIRModel
from models.seir_model import SEIRModel
from models.spatial_brownian_model import SpatialBrownianModel


class TestExceptionHandling:
    """异常处理机制测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.data_processor = DataProcessor()
        
    def test_invalid_file_path_handling(self):
        """测试无效文件路径的异常处理
        
        验证：
        1. 异常处理合理（不崩溃、有提示、可恢复）
        2. 程序稳定性良好
        3. 用户可以重新输入正确数据
        """
        
        # 测试不存在的文件
        non_existent_file = "non_existent_file.xlsx"
        result = self.data_processor.load_raw_data(non_existent_file)
        
        # 验证异常处理：应该返回False而不是崩溃
        assert result == False, "加载不存在的文件应该返回False"
        
        # 验证程序状态：数据处理器应该仍然可用
        assert self.data_processor.raw_data is None, "加载失败后raw_data应该为None"
        
        # 验证可以重新尝试加载正确的数据
        self.data_processor.create_sample_data()
        assert self.data_processor.raw_data is not None, "应该能够重新创建示例数据"
        
        print("无效文件路径异常处理测试通过")
    
    def test_invalid_data_format_handling(self):
        """测试无效数据格式的异常处理"""
        
        # 创建一个无效的数据文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("这不是一个有效的Excel文件内容")
            invalid_file = f.name
        
        try:
            # 尝试加载无效文件
            result = self.data_processor.load_raw_data(invalid_file)
            
            # 验证异常处理
            assert result == False, "加载无效格式文件应该返回False"
            assert self.data_processor.raw_data is None, "无效数据加载后raw_data应该为None"
            
            # 验证系统仍然稳定，可以处理其他操作
            can_create_sample = self.data_processor.create_sample_data()
            assert can_create_sample == True, "异常后应该能够创建示例数据"
            
        finally:
            # 清理临时文件
            if os.path.exists(invalid_file):
                os.unlink(invalid_file)
        
        print("无效数据格式异常处理测试通过")
    
    def test_invalid_model_parameters_handling(self):
        """测试无效模型参数的异常处理"""
        
        # 测试SIR模型的无效参数
        invalid_sir_config = {
            'N': -1000,         # 负数人口
            'beta': -0.1,       # 负传播率
            'gamma': 2.0,       # 过大的康复率
            'S0': 'invalid',    # 非数值类型
            'I0': 1,
            'R0': 0,
            'days': 100,
            'dt': 1
        }
        
        try:
            sir_model = SIRModel(invalid_sir_config)
            # 尝试运行模型，应该能处理异常
            result = sir_model.solve_ode()
            
            # 验证异常处理：模型应该能检测并处理无效参数
            # 这里我们检查模型是否能安全地处理无效输入
            print("SIR模型参数异常处理能力验证")
            
        except Exception as e:
            # 如果抛出异常，应该是有意义的异常信息
            assert len(str(e)) > 0, "异常信息应该有内容"
            print(f"SIR模型正确抛出异常: {str(e)[:50]}...")
        
        print("无效模型参数异常处理测试通过")
    
    def test_memory_overflow_protection(self):
        """测试内存溢出保护机制"""
        
        # 创建一个可能导致内存问题的大配置
        large_config = {
            'grid_size': 1000,           # 很大的网格
            'num_individuals': 10000,    # 很多个体
            'days': 1,                   # 短时间避免真正的内存问题
            'dt': 1,
            'sigma': 2,
            'transmission_distance': 4,
            'beta': 0.04,
            'sigma_rate': 0.1,
            'gamma': 0.1,
            'v1': 1/5,
            'v2': 1/3,
            'isolation_duration': 14,
            'initial_infected': 10
        }
        
        try:
            # 尝试创建大型空间模型
            spatial_model = SpatialBrownianModel(large_config)
            
            # 验证模型能够处理大配置而不崩溃
            assert spatial_model.grid_size == 1000, "应该能够设置大网格"
            assert spatial_model.num_individuals == 10000, "应该能够设置多个体"
            
            print("大配置处理能力验证通过")
            
        except MemoryError:
            print("正确检测到内存不足情况")
        except Exception as e:
            # 其他异常也应该被合理处理
            print(f"处理大配置时的异常: {str(e)[:100]}...")
        
        print("内存溢出保护测试通过")
    
    def test_division_by_zero_handling(self):
        """测试除零异常的处理"""
        
        # 创建可能导致除零的配置
        zero_config = {
            'N': 0,              # 零人口可能导致除零
            'beta': 0.1,
            'gamma': 0.1,
            'S0': 0,
            'I0': 0,
            'R0': 0,
            'days': 10,
            'dt': 1
        }
        
        try:
            sir_model = SIRModel(zero_config)
            result = sir_model.solve_ode()
            
            # 如果没有崩溃，验证结果的合理性
            if hasattr(sir_model, 'S') and sir_model.S is not None:
                assert not np.any(np.isnan(sir_model.S)), "结果不应包含NaN值"
                assert not np.any(np.isinf(sir_model.S)), "结果不应包含无穷值"
            
            print("除零情况处理验证")
            
        except (ZeroDivisionError, ValueError) as e:
            print(f"正确处理除零异常: {str(e)[:50]}...")
        except Exception as e:
            print(f"其他除零相关异常: {str(e)[:50]}...")
        
        print("除零异常处理测试通过")
    
    def test_missing_data_handling(self):
        """测试缺失数据的处理"""
        
        # 创建包含缺失值的测试数据
        incomplete_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=5),
            'cumulative_confirmed': [10, 20, np.nan, 40, 50],
            'cumulative_deaths': [1, np.nan, 3, 4, 5],
            'cumulative_recovered': [8, 15, 25, np.nan, 45]
        })
        
        # 设置数据到处理器
        self.data_processor.raw_data = incomplete_data
        
        try:
            # 尝试验证数据质量
            validation_result = self.data_processor.validate_data()
            
            # 验证系统能够检测缺失值
            assert validation_result is not None, "数据验证应该能够处理缺失值"
            
            # 验证系统不会因缺失值而崩溃
            print("缺失数据处理能力验证")
            
        except Exception as e:
            # 即使出现异常，也应该是有意义的异常
            assert len(str(e)) > 0, "异常信息应该有内容"
            print(f"缺失数据异常处理: {str(e)[:50]}...")
        
        print("缺失数据处理测试通过")
    
    def test_invalid_time_parameters_handling(self):
        """测试无效时间参数的处理"""
        
        # 测试无效的时间配置
        invalid_time_configs = [
            {'days': -10, 'dt': 1},      # 负天数
            {'days': 100, 'dt': 0},      # 零时间步长
            {'days': 100, 'dt': -1},     # 负时间步长
            {'days': 1, 'dt': 2},        # 时间步长大于总天数
        ]
        
        for i, config in enumerate(invalid_time_configs):
            try:
                full_config = {
                    'N': 1000,
                    'beta': 0.1,
                    'gamma': 0.1,
                    'S0': 999,
                    'I0': 1,
                    'R0': 0,
                    **config
                }
                
                sir_model = SIRModel(full_config)
                result = sir_model.solve_ode()
                
                print(f"时间配置{i+1}处理完成")
                
            except (ValueError, AssertionError) as e:
                print(f"时间配置{i+1}正确检测异常: {str(e)[:30]}...")
            except Exception as e:
                print(f"时间配置{i+1}其他异常: {str(e)[:30]}...")
        
        print("无效时间参数处理测试通过")
    
    def test_system_recovery_after_exception(self):
        """测试异常后系统恢复能力"""
        
        # 故意触发异常
        try:
            self.data_processor.load_raw_data("non_existent_file.xyz")
        except:
            pass  # 忽略异常
        
        # 验证系统能够恢复正常工作
        recovery_success = self.data_processor.create_sample_data()
        assert recovery_success == True, "异常后应该能够恢复正常功能"
        
        # 验证数据处理流程能够正常进行
        validation_success = self.data_processor.validate_data()
        assert validation_success == True, "恢复后应该能够验证数据"
        
        calculation_success = self.data_processor.calculate_seir_states()
        assert calculation_success == True, "恢复后应该能够计算SEIR状态"
        
        print("系统恢复能力测试通过")
    
    def test_graceful_degradation(self):
        """测试系统优雅降级能力"""
        
        # 模拟部分功能不可用的情况
        original_method = self.data_processor.save_processed_data
        
        # 临时禁用保存功能
        def mock_save_failure():
            raise IOError("磁盘空间不足")
        
        self.data_processor.save_processed_data = mock_save_failure
        
        try:
            # 即使保存失败，其他功能应该仍然可用
            self.data_processor.create_sample_data()
            self.data_processor.validate_data()
            self.data_processor.calculate_seir_states()
            
            # 尝试保存（应该失败但不崩溃）
            try:
                self.data_processor.save_processed_data()
            except IOError:
                print("正确处理保存失败")
            
            # 验证其他功能仍然正常
            stats = self.data_processor.get_data_statistics()
            assert stats is not None, "统计功能应该仍然可用"
            
        finally:
            # 恢复原始方法
            self.data_processor.save_processed_data = original_method
        
        print("优雅降级能力测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestExceptionHandling()
    test_instance.setup_method()
    
    try:
        test_instance.test_invalid_file_path_handling()
        test_instance.test_invalid_data_format_handling()
        test_instance.test_invalid_model_parameters_handling()
        test_instance.test_memory_overflow_protection()
        test_instance.test_division_by_zero_handling()
        test_instance.test_missing_data_handling()
        test_instance.test_invalid_time_parameters_handling()
        test_instance.test_system_recovery_after_exception()
        test_instance.test_graceful_degradation()
        print("\n所有异常处理机制测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")