#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试在线联邦学习功能
"""

import pytest
import subprocess
import time
import os
import sys
import socket
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_client_connection_display():
    """测试客户端连接数显示"""

    # 启动主程序进程
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # 发送输入启动在线联邦学习
        input_data = "2\n8080\n9000\n3\n6\n"
        stdout, stderr = process.communicate(input=input_data, timeout=15)

        # 验证是否显示客户端连接信息
        output = stdout + stderr
        connection_patterns = [
            "Client 1 connected",
            "Client 2 connected",
            "Client 3 connected",
            "connected"
        ]

        has_connection_display = any(pattern in output for pattern in connection_patterns)
        assert has_connection_display, f"应该显示客户端连接信息，实际输出: {output}"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("程序没有在预期时间内完成")
    except Exception as e:
        process.kill()
        pytest.fail(f"测试过程中发生错误: {e}")

def test_client_ready_status():
    """测试客户端就绪状态显示"""

    # 启动主程序进程
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # 发送输入启动在线联邦学习
        input_data = "2\n8080\n9000\n5\n6\n"
        stdout, stderr = process.communicate(input=input_data, timeout=15)

        # 验证是否显示客户端就绪状态信息
        output = stdout + stderr
        ready_patterns = [
            "1/5 clients ready",
            "2/5 clients ready",
            "3/5 clients ready",
            "4/5 clients ready",
            "5/5 clients ready",
            "clients ready"
        ]

        has_ready_display = any(pattern in output for pattern in ready_patterns)
        assert has_ready_display, f"应该显示客户端就绪状态信息，实际输出: {output}"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("程序没有在预期时间内完成")
    except Exception as e:
        process.kill()
        pytest.fail(f"测试过程中发生错误: {e}")

def test_port_configuration():
    """测试端口配置功能"""

    # 启动主程序进程
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # 测试不同端口配置
        input_data = "2\n8080\n9000\n2\n6\n"
        stdout, stderr = process.communicate(input=input_data, timeout=10)

        # 验证端口配置是否被接受
        output = stdout + stderr
        port_patterns = [
            "8080",
            "9000",
            "接收端口",
            "发送端口"
        ]

        has_port_config = any(pattern in output for pattern in port_patterns)
        assert has_port_config, f"应该显示端口配置信息，实际输出: {output}"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("程序没有在预期时间内完成")
    except Exception as e:
        process.kill()
        pytest.fail(f"测试过程中发生错误: {e}")

def test_invalid_port_handling():
    """测试无效端口处理"""

    # 启动主程序进程
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # 发送无效端口号
        input_data = "2\n99999\n8080\n9000\n2\n6\n"  # 无效端口号
        stdout, stderr = process.communicate(input=input_data, timeout=10)

        # 验证是否显示错误信息
        output = stdout + stderr
        assert "错误" in output, "应该显示端口错误信息"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("程序没有在预期时间内完成")
    except Exception as e:
        process.kill()
        pytest.fail(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
