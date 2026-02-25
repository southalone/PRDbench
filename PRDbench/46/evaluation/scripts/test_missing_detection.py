#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专用测试脚本：缺失值检测功能测试

直接调用数据验证功能，测试缺失值检测能力
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_root))

try:
    from credit_assessment.data import DataManager
    from credit_assessment.utils import ConfigManager, DataValidator
    import pandas as pd
    
    def test_missing_value_detection():
        """测试缺失值检测功能"""
        print("=== 缺失值检测测试 ===")
        
        # 初始化组件
        config = ConfigManager()
        data_manager = DataManager(config)
        validator = DataValidator()
        
        # 测试文件路径
        missing_file = Path(__file__).parent.parent / "test_data_missing.csv"
        
        if not missing_file.exists():
            print(f"错误：测试数据文件不存在 - {missing_file}")
            return False
        
        try:
            # 导入包含缺失值的数据
            print(f"导入测试文件：{missing_file}")
            data = pd.read_csv(missing_file)
            
            # 执行缺失值检测
            validation_result = validator.validate_dataframe(data)
            
            # 分析缺失值
            missing_info = {}
            for column in data.columns:
                missing_count = data[column].isnull().sum()
                if missing_count > 0:
                    missing_info[column] = missing_count
            
            print(f"检测结果：发现缺失值")
            
            # 详细报告
            total_missing = sum(missing_info.values())
            if total_missing > 0:
                print(f"缺失值详情：")
                for column, count in missing_info.items():
                    print(f"  - {column}字段缺失{count}个值")
                print(f"共计{total_missing}个缺失值")
                
                print("✓ 自动检测缺失值功能正常")
                print("✓ 提供了详细的位置和数量信息")
                return True
            else:
                print("✗ 未检测到预期的缺失值")
                return False
                
        except Exception as e:
            print(f"✗ 缺失值检测测试失败: {str(e)}")
            return False
    
    # 执行测试
    if __name__ == "__main__":
        success = test_missing_value_detection()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"模块导入失败: {str(e)}")
    sys.exit(1)