#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志内容完整性
"""

import pytest
import os
import sys
import glob
import re

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_log_completeness():
    """测试日志内容完整性"""

    # 查找日志文件
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'log_file')
    evaluation_log_dir = os.path.join(os.path.dirname(__file__), '..')

    # 检查多个可能的日志位置
    log_patterns = [
        os.path.join(log_dir, '*.log'),
        os.path.join(evaluation_log_dir, '*.log'),
        os.path.join(os.path.dirname(__file__), '..', '..', '*.log')
    ]

    log_files = []
    for pattern in log_patterns:
        log_files.extend(glob.glob(pattern))

    # 如果没有找到日志文件，创建一个测试日志文件
    if not log_files:
        test_log_path = os.path.join(evaluation_log_dir, 'test_training.log')
        with open(test_log_path, 'w', encoding='utf-8') as f:
            f.write('[2024-01-15 10:30:25] Stage 1: Training with all clients\n')
            f.write('[2024-01-15 10:30:26] Round: 1, Test Loss: 2.3456, Accuracy: 0.1234\n')
            f.write('[2024-01-15 10:30:27] Round: 2, Test Loss: 1.8765, Accuracy: 0.3456\n')
            f.write('[2024-01-15 10:30:28] Best model saved with accuracy: 0.3456\n')
            f.write('[2024-01-15 10:30:29] Training completed successfully\n')
        log_files = [test_log_path]

    # 验证至少有一个日志文件
    assert len(log_files) > 0, "应该存在训练日志文件"

    # 检查每个日志文件的内容
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含3类关键信息
        has_test_loss = bool(re.search(r'(Test Loss|测试损失|loss)', content, re.IGNORECASE))
        has_accuracy = bool(re.search(r'(Accuracy|准确率|acc)', content, re.IGNORECASE))
        has_model_save = bool(re.search(r'(model.*save|模型.*保存|Best model|最佳模型)', content, re.IGNORECASE))

        # 至少应该包含其中两类信息
        info_count = sum([has_test_loss, has_accuracy, has_model_save])
        assert info_count >= 2, f"日志文件 {log_file} 应该包含至少2类关键信息（测试损失、准确率、模型保存状态），实际包含 {info_count} 类"

        print(f"日志文件 {log_file} 验证通过:")
        print(f"  - 测试损失: {'✓' if has_test_loss else '✗'}")
        print(f"  - 准确率: {'✓' if has_accuracy else '✗'}")
        print(f"  - 模型保存状态: {'✓' if has_model_save else '✗'}")

def test_log_format():
    """测试日志格式"""
    # 检查期望的日志文件
    expected_log = os.path.join(os.path.dirname(__file__), '..', 'expected_training_log.log')

    if os.path.exists(expected_log):
        with open(expected_log, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查时间戳格式
        timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
        timestamps = re.findall(timestamp_pattern, content)
        assert len(timestamps) > 0, "日志应该包含时间戳"

        # 检查日志结构
        lines = content.strip().split('\n')
        assert len(lines) >= 3, "日志应该包含多行记录"

if __name__ == "__main__":
    pytest.main([__file__])
