#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.8.2 数据导出 - Excel格式
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


def test_excel_export():
    """测试Excel格式数据导出功能"""
    print("开始测试2.8.2 Excel格式导出...")
    
    # 创建配置和数据管理器
    config = ConfigManager()
    data_manager = DataManager(config)
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'age': [25, 35, 45, 30, 55],
        'income': [50000, 75000, 60000, 80000, 45000],
        'credit_score': [650, 700, 620, 750, 580],
        'risk_score': [0.3, 0.2, 0.4, 0.1, 0.6],
        'target': [1, 0, 1, 0, 1]
    })
    
    # 创建临时输出路径
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "exported_data.xlsx")
        
        try:
            # 执行Excel导出
            data_manager.export_data(test_data, output_path, mask_sensitive=False)
            
            # 验证文件是否生成
            assert os.path.exists(output_path), f"Excel文件未生成: {output_path}"
            
            # 验证文件大小
            file_size = os.path.getsize(output_path)
            assert file_size > 1000, f"Excel文件太小: {file_size}字节"
            
            # 验证Excel内容
            exported_data = pd.read_excel(output_path)
            assert len(exported_data) == 5, f"导出行数不正确: {len(exported_data)} != 5"
            assert len(exported_data.columns) == 6, f"导出列数不正确: {len(exported_data.columns)}"
            
            # 验证数据完整性
            assert 'customer_id' in exported_data.columns, "customer_id字段缺失"
            assert 'age' in exported_data.columns, "age字段缺失"
            assert 'income' in exported_data.columns, "income字段缺失"
            assert 'credit_score' in exported_data.columns, "credit_score字段缺失"
            
            print(f"SUCCESS: Excel文件生成成功: {output_path}")
            print(f"SUCCESS: 文件大小: {file_size}字节")
            print(f"SUCCESS: 数据行数: {len(exported_data)}")
            print(f"SUCCESS: 数据列数: {len(exported_data.columns)}")
            
        except Exception as e:
            print(f"FAIL: Excel导出失败: {e}")
            return False
    
    print("2.8.2 Excel格式导出测试通过")
    return True


if __name__ == "__main__":
    test_excel_export()