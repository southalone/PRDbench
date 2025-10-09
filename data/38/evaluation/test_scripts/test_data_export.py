#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from data_manager import DataManager
import pandas as pd

def test_csv_export():
    """测试CSV数据导出功能"""
    try:
        data_manager = DataManager()
        
        # 创建测试数据
        test_users = pd.DataFrame({
            'user_id': [1, 2, 3, 4, 5],
            'age': [25, 30, 28, 35, 22],
            'gender': ['M', 'F', 'M', 'F', 'M'],
            'registration_date': ['2023-01-01'] * 5
        })
        
        # 导出数据
        output_path = '../evaluation/exported_users.csv'
        result = data_manager.export_csv_data(test_users, output_path)
        
        if os.path.exists(output_path):
            print("SUCCESS: CSV数据导出成功")
            print(f"导出文件: {output_path}")
            print(f"导出记录数: {len(test_users)}")
            return True
        else:
            print("ERROR: CSV数据导出失败")
            return False
            
    except Exception as e:
        print(f"ERROR: 导出过程出错: {e}")
        return False

if __name__ == "__main__":
    success = test_csv_export()
    sys.exit(0 if success else 1)
