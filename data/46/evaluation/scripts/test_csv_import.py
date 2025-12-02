#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专用测试脚本：CSV数据导入功能测试

直接调用DataManager的import_data方法，避免菜单导航冗余
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_root))

try:
    from credit_assessment.data import DataManager
    from credit_assessment.utils import ConfigManager
    
    def test_csv_import():
        """测试CSV格式导入功能"""
        print("=== CSV数据导入测试 ===")
        
        # 初始化数据管理器
        config = ConfigManager()
        data_manager = DataManager(config)
        
        # 测试文件路径
        csv_file = Path(__file__).parent.parent / "test_data_csv.csv"
        
        if not csv_file.exists():
            print(f"错误：测试数据文件不存在 - {csv_file}")
            return False
        
        try:
            # 执行CSV导入
            print(f"导入文件：{csv_file}")
            data = data_manager.import_data(csv_file, validate=True, encoding='utf-8')
            
            # 验证导入结果
            if data is not None:
                row_count = len(data)
                col_count = len(data.columns)
                print(f"数据导入成功! 共 {row_count} 行，{col_count} 列")
                
                # 显示列名
                print(f"列名: {list(data.columns)}")
                
                # 验证数据行数
                if row_count >= 10:
                    print("✓ CSV格式支持正常")
                    print("✓ 数据行数符合要求")
                    return True
                else:
                    print("✗ 数据行数不足")
                    return False
            else:
                print("✗ 数据导入失败")
                return False
                
        except Exception as e:
            print(f"✗ CSV导入测试失败: {str(e)}")
            return False
    
    # 执行测试
    if __name__ == "__main__":
        success = test_csv_import()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"模块导入失败: {str(e)}")
    print("请确保项目结构正确")
    sys.exit(1)