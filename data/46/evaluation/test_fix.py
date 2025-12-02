#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复效果的脚本
"""

import sys
import os
sys.path.insert(0, '../src')

from credit_assessment.data.data_manager import DataManager
from credit_assessment.utils import ConfigManager

def test_data_import():
    """测试数据导入功能"""
    print("=" * 50)
    print("测试数据导入功能")
    print("=" * 50)
    
    try:
        # 创建数据管理器
        config = ConfigManager()
        dm = DataManager(config)
        
        # 测试导入异常数据
        print("正在导入测试数据: test_data_anomaly.csv")
        df = dm.import_data('test_data_anomaly.csv', validate=True, encoding='utf-8')
        
        print(f"[SUCCESS] 成功导入数据: {df.shape[0]}行 {df.shape[1]}列")
        print(f"列名: {list(df.columns)}")
        print("\n前5行数据:")
        print(df.head())
        
        # 获取验证报告
        validation_report = dm.validate_current_data()
        print(f"\n验证结果: {validation_report['validation_summary']}")
        
        if validation_report.get('warnings'):
            print("\n[WARNING] 警告信息:")
            for warning in validation_report['warnings']:
                print(f"  - {warning}")
                
        if validation_report.get('suggestions'):
            print("\n[INFO] 建议信息:")
            for suggestion in validation_report['suggestions']:
                print(f"  - {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logger():
    """测试日志功能"""
    print("\n" + "=" * 50)
    print("测试日志功能")
    print("=" * 50)
    
    try:
        from credit_assessment.utils.logger import setup_logger
        logger = setup_logger("test_logger")
        logger.info("测试日志信息")
        logger.warning("测试警告信息")
        print("[SUCCESS] 日志功能正常")
        return True
    except Exception as e:
        print(f"[ERROR] 日志功能异常: {e}")
        return False

if __name__ == "__main__":
    print("开始测试修复效果...")
    
    # 测试日志功能
    logger_ok = test_logger()
    
    # 测试数据导入功能
    import_ok = test_data_import()
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"日志功能: {'[PASS]' if logger_ok else '[FAIL]'}")
    print(f"数据导入: {'[PASS]' if import_ok else '[FAIL]'}")
    
    if logger_ok and import_ok:
        print("\n[SUCCESS] 所有功能测试通过！问题已修复。")
    else:
        print("\n[WARNING] 仍有问题需要解决。")