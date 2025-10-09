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

def test_csv_import():
    """测试CSV数据导入功能"""
    try:
        data_manager = DataManager()
        # 直接调用导入功能
        result = data_manager.import_csv_data('../evaluation/test_users.csv', data_type='users')
        if result is not None and not result.empty:
            print("SUCCESS: CSV数据导入成功")
            print(f"导入记录数: {len(result)}")
            return True
        else:
            print("ERROR: CSV数据导入失败")
            return False
    except Exception as e:
        print(f"ERROR: 导入过程出错: {e}")
        return False

if __name__ == "__main__":
    success = test_csv_import()
    sys.exit(0 if success else 1)
