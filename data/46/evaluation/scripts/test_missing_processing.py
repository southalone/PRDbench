#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专用测试脚本：缺失值处理执行功能测试

直接调用数据预处理功能，测试缺失值处理能力
"""

import sys
import os
from pathlib import Path
import pandas as pd

# 添加项目路径
project_root = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_root))

try:
    from credit_assessment.data import DataPreprocessor
    from credit_assessment.utils import ConfigManager
    
    def test_missing_value_processing():
        """测试缺失值处理执行功能"""
        print("=== 缺失值处理执行测试 ===")
        
        # 初始化预处理器
        config = ConfigManager()
        preprocessor = DataPreprocessor(config)
        
        # 加载包含缺失值的测试数据
        missing_file = Path(__file__).parent.parent / "test_data_missing.csv"
        
        if not missing_file.exists():
            print(f"错误：测试数据文件不存在 - {missing_file}")
            return False
        
        try:
            # 读取数据
            print(f"加载测试数据：{missing_file}")
            data = pd.read_csv(missing_file)
            
            print("原始数据缺失值情况：")
            missing_before = data.isnull().sum()
            for column, count in missing_before.items():
                if count > 0:
                    print(f"  - {column}: {count} 个缺失值")
            
            # 使用均值填充策略处理缺失值
            print("\n执行缺失值处理（均值填充）...")
            processed_data = preprocessor.handle_missing_values(data, strategy='mean')
            
            # 验证处理结果
            missing_after = processed_data.isnull().sum()
            total_missing_after = missing_after.sum()
            
            print("\n处理结果统计：")
            print(f"处理前总缺失值: {missing_before.sum()}")
            print(f"处理后总缺失值: {total_missing_after}")
            
            if total_missing_after == 0:
                print("✓ 缺失值处理成功：所有缺失值已被正确填充")
                print("✓ 显示了详细的处理结果统计")
                return True
            else:
                print("✗ 缺失值处理不完整：仍有缺失值存在")
                return False
                
        except Exception as e:
            print(f"✗ 缺失值处理测试失败: {str(e)}")
            return False
    
    # 执行测试
    if __name__ == "__main__":
        success = test_missing_value_processing()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"模块导入失败: {str(e)}")
    sys.exit(1)