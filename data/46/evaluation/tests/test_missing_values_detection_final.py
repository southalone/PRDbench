#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.1.2a 数据校验 - 缺失值检测 (最终修复版)
"""

import sys
import os
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

# 添加项目路径 - 使用绝对路径
current_dir = Path(__file__).parent.parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# 直接导入，不使用try-except和pytest.skip
from credit_assessment.data.data_manager import DataManager
from credit_assessment.utils.config_manager import ConfigManager


def test_missing_values_detection():
    """测试缺失值检测功能"""
    # 创建配置管理器和数据管理器
    config = ConfigManager()
    data_manager = DataManager(config)
    
    # 创建包含缺失值的测试数据
    np.random.seed(42)
    n_samples = 120
    
    ages = np.random.randint(20, 80, n_samples).astype(float)
    incomes = np.random.randint(20000, 200000, n_samples).astype(float)
    credit_scores = np.random.randint(300, 850, n_samples).astype(float)
    employment_years = np.random.randint(0, 40, n_samples).astype(float)
    targets = np.random.choice([0, 1], n_samples)
    
    # 在age和income字段中添加缺失值（满足至少2个字段包含缺失值的要求）
    missing_age_indices = np.random.choice(n_samples, int(n_samples * 0.15), replace=False)
    missing_income_indices = np.random.choice(n_samples, int(n_samples * 0.12), replace=False)
    
    ages[missing_age_indices] = np.nan
    incomes[missing_income_indices] = np.nan
    
    test_data = pd.DataFrame({
        'age': ages,
        'income': incomes,
        'credit_score': credit_scores,
        'employment_years': employment_years,
        'target': targets
    })
    
    # 创建临时CSV文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    test_data.to_csv(temp_file.name, index=False, encoding='utf-8')
    temp_file.close()
    
    try:
        # 执行 (Act): 导入包含缺失值的测试文件
        df = data_manager.import_data(temp_file.name)
        
        # 验证数据导入成功
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 120
        assert len(df.columns) == 5
        
        # 验证缺失值存在
        missing_count = df.isnull().sum()
        age_missing = missing_count['age']
        income_missing = missing_count['income']
        
        assert age_missing > 0, f"age字段应该有缺失值，实际: {age_missing}"
        assert income_missing > 0, f"income字段应该有缺失值，实际: {income_missing}"
        
        # 验证至少2个字段有缺失值
        fields_with_missing = (missing_count > 0).sum()
        assert fields_with_missing >= 2, f"至少2个字段应该有缺失值，实际: {fields_with_missing}"
        
        print(f"缺失值检测测试通过: age缺失{age_missing}个, income缺失{income_missing}个")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


if __name__ == "__main__":
    test_missing_values_detection()
    print("测试完成!")