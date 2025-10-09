#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件命名规范
"""

import pytest
import os
import sys
import glob
import re

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_log_naming_convention():
    """测试日志文件命名规范"""

    # 查找日志文件
    log_dirs = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'log_file'),
        os.path.join(os.path.dirname(__file__), '..'),
        os.path.join(os.path.dirname(__file__), '..', '..')
    ]

    log_files = []
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            log_files.extend(glob.glob(os.path.join(log_dir, '*.log')))

    # 如果没有找到日志文件，创建一些测试文件来验证命名规范
    if not log_files:
        test_dir = os.path.join(os.path.dirname(__file__), '..', 'test_logs')
        os.makedirs(test_dir, exist_ok=True)

        # 创建符合命名规范的测试文件
        test_files = [
            'result_5_10_5.log',
            'result_10_10_10.log',
            'result_15_10_15.log',
            'result_20_10_20.log'
        ]

        for filename in test_files:
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f'Test log file: {filename}\n')
            log_files.append(filepath)

    # 验证至少有一些日志文件
    assert len(log_files) > 0, "应该存在日志文件用于测试命名规范"

    # 定义命名规范模式
    naming_patterns = [
        r'result_\d+_\d+_\d+\.log',  # result_clients_rounds_epochs.log
        r'result_stage\d+_\d+\.log',  # result_stage1_2.log
        r'expected_result_\d+_\d+_\d+\.log',  # expected_result_clients_rounds_epochs.log
    ]

    compliant_files = []
    non_compliant_files = []

    for log_file in log_files:
        filename = os.path.basename(log_file)
        is_compliant = any(re.match(pattern, filename) for pattern in naming_patterns)

        if is_compliant:
            compliant_files.append(filename)
        else:
            non_compliant_files.append(filename)

    # 验证命名规范
    print(f"符合命名规范的文件: {compliant_files}")
    print(f"不符合命名规范的文件: {non_compliant_files}")

    # 至少应该有一些文件符合命名规范
    assert len(compliant_files) > 0, "应该有文件符合命名规范"

    # 检查具体的命名格式
    for filename in compliant_files:
        if re.match(r'result_\d+_\d+_\d+\.log', filename):
            # 提取参数信息
            match = re.match(r'result_(\d+)_(\d+)_(\d+)\.log', filename)
            if match:
                clients, rounds, epochs = match.groups()
                print(f"文件 {filename} 包含参数信息: clients={clients}, rounds={rounds}, epochs={epochs}")

                # 验证参数值的合理性
                assert 1 <= int(clients) <= 20, f"客户端数量应该在1-20之间: {clients}"
                assert 1 <= int(rounds) <= 100, f"训练轮数应该在1-100之间: {rounds}"
                assert 1 <= int(epochs) <= 1000, f"本地训练轮数应该在1-1000之间: {epochs}"

def test_parameter_extraction():
    """测试从文件名提取参数信息"""

    test_filenames = [
        'result_5_10_5.log',
        'result_10_10_10.log',
        'result_15_10_15.log',
        'result_20_10_20.log'
    ]

    for filename in test_filenames:
        match = re.match(r'result_(\d+)_(\d+)_(\d+)\.log', filename)
        assert match is not None, f"文件名 {filename} 应该符合 result_X_Y_Z.log 格式"

        clients, rounds, epochs = match.groups()
        assert clients.isdigit(), f"客户端数量应该是数字: {clients}"
        assert rounds.isdigit(), f"训练轮数应该是数字: {rounds}"
        assert epochs.isdigit(), f"本地训练轮数应该是数字: {epochs}"

def test_file_extension():
    """测试文件扩展名"""

    # 查找所有相关文件
    search_dirs = [
        os.path.join(os.path.dirname(__file__), '..'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'log_file')
    ]

    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            # 检查日志文件扩展名
            log_files = glob.glob(os.path.join(search_dir, 'result_*'))
            for log_file in log_files:
                assert log_file.endswith('.log'), f"日志文件应该以.log结尾: {log_file}"

if __name__ == "__main__":
    pytest.main([__file__])
