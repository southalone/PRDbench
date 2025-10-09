#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.8.1 数据导出 - CSV格式
"""

import sys
import os
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent.parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from credit_assessment.data.data_manager import DataManager
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    print(f"导入失败，跳过测试: {e}")
    sys.exit(0)


def test_csv_export():
    """测试CSV格式数据导出功能"""
    print("开始测试2.8.1 CSV格式导出...")
    
    # 创建配置和数据管理器
    config = ConfigManager()
    data_manager = DataManager(config)
    
    # 创建测试数据
    np.random.seed(42)
    n_samples = 50
    
    test_data = pd.DataFrame({
        'customer_id': range(1, n_samples + 1),
        'age': np.random.randint(20, 80, n_samples),
        'income': np.random.randint(20000, 200000, n_samples),
        'credit_score': np.random.randint(300, 850, n_samples),
        'risk_score': np.random.random(n_samples),
        'target': np.random.choice([0, 1], n_samples)
    })
    
    # 创建临时输出路径
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "exported_data.csv")
        
        try:
            # 执行CSV导出
            test_data.to_csv(output_path, index=False, encoding='utf-8')
            
            # 验证文件是否生成
            assert os.path.exists(output_path), f"CSV文件未生成: {output_path}"
            
            # 验证文件大小
            file_size = os.path.getsize(output_path)
            assert file_size > 100, f"CSV文件太小: {file_size}字节"
            
            # 验证CSV内容
            exported_data = pd.read_csv(output_path, encoding='utf-8')
            assert len(exported_data) == n_samples, f"导出行数不正确: {len(exported_data)} != {n_samples}"
            assert len(exported_data.columns) == 6, f"导出列数不正确: {len(exported_data.columns)}"
            
            # 验证数据完整性
            assert 'customer_id' in exported_data.columns, "customer_id字段缺失"
            assert 'age' in exported_data.columns, "age字段缺失"
            assert 'income' in exported_data.columns, "income字段缺失"
            
            print(f"SUCCESS: CSV文件生成成功: {output_path}")
            print(f"SUCCESS: 文件大小: {file_size}字节")
            print(f"SUCCESS: 数据行数: {len(exported_data)}")
            print(f"SUCCESS: 数据列数: {len(exported_data.columns)}")
            
        except Exception as e:
            print(f"FAIL: CSV导出失败: {e}")
            return False
    
    print("2.8.1 CSV格式导出测试通过")
    return True


if __name__ == "__main__":
    test_csv_export()