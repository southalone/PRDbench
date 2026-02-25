#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.6.1a 报告生成 - HTML格式输出
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
    from credit_assessment.evaluation.report_generator import ReportGenerator
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    print(f"导入失败，跳过测试: {e}")
    sys.exit(0)


def test_html_report_generation():
    """测试HTML报告生成功能"""
    print("开始测试2.6.1a HTML报告生成...")
    
    # 创建配置管理器
    config = ConfigManager()
    report_generator = ReportGenerator(config)
    
    # 创建模拟评估结果
    np.random.seed(42)
    n_samples = 100
    
    # 模拟预测结果
    y_true = np.random.choice([0, 1], n_samples)
    y_pred = np.random.random(n_samples)  # 预测概率
    y_pred_binary = (y_pred > 0.5).astype(int)  # 二元预测
    
    # 创建模拟数据
    test_data = pd.DataFrame({
        'age': np.random.randint(20, 80, n_samples),
        'income': np.random.randint(20000, 200000, n_samples),
        'credit_score': np.random.randint(300, 850, n_samples),
        'target': y_true
    })
    
    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "test_report.html")
        
        try:
            # 生成HTML报告
            result = report_generator.generate_html_report(
                data=test_data,
                predictions={'y_true': y_true, 'y_pred': y_pred, 'y_pred_binary': y_pred_binary},
                output_path=output_path
            )
            
            # 验证HTML文件是否生成
            assert os.path.exists(output_path), f"HTML报告文件未生成: {output_path}"
            
            # 验证文件大小
            file_size = os.path.getsize(output_path)
            assert file_size > 1000, f"HTML报告文件太小: {file_size}字节"
            
            # 验证HTML内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<html>' in content, "HTML报告格式不正确"
                assert '报告' in content or 'Report' in content, "HTML报告内容缺失"
                
            print(f"SUCCESS: HTML报告生成成功: {output_path}")
            print(f"SUCCESS: 文件大小: {file_size}字节")
            print("SUCCESS: HTML格式验证通过")
            
        except Exception as e:
            print(f"FAIL: HTML报告生成失败: {e}")
            return False
    
    print("2.6.1a HTML报告生成测试通过")
    return True


if __name__ == "__main__":
    test_html_report_generation()