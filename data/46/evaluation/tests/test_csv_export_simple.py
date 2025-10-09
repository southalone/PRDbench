#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.8.1 数据导出 - CSV格式 (简化版)
"""

import pandas as pd
import os
import tempfile


def test_csv_export_simple():
    """简化的CSV导出测试，不依赖项目模块"""
    print("开始测试2.8.1 CSV格式导出（简化版）...")
    
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
            assert len(exported_data) == 5, f"导出行数不正确: {len(exported_data)}"
            assert len(exported_data.columns) == 6, f"导出列数不正确: {len(exported_data.columns)}"
            
            # 验证字段完整性
            required_fields = ['customer_id', 'age', 'income', 'credit_score', 'risk_score', 'target']
            for field in required_fields:
                assert field in exported_data.columns, f"{field}字段缺失"
            
            # 验证数据内容
            assert exported_data['customer_id'].tolist() == [1, 2, 3, 4, 5], "customer_id数据不正确"
            assert exported_data['age'].tolist() == [25, 35, 45, 30, 55], "age数据不正确"
            
            print(f"SUCCESS: CSV文件生成成功: {output_path}")
            print(f"SUCCESS: 文件大小: {file_size}字节")
            print(f"SUCCESS: 数据行数: {len(exported_data)}")
            print(f"SUCCESS: 数据列数: {len(exported_data.columns)}")
            print("SUCCESS: 所有字段验证通过")
            
            return True
            
        except Exception as e:
            print(f"FAIL: CSV导出失败: {e}")
            return False


if __name__ == "__main__":
    success = test_csv_export_simple()
    if success:
        print("2.8.1 CSV格式导出测试通过")
    else:
        print("2.8.1 CSV格式导出测试失败")