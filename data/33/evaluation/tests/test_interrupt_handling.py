#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中断处理功能
"""

import pytest
import signal
import subprocess
import time
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_ctrl_c_interrupt():
    """测试Ctrl+C中断支持"""
    # 启动主程序进程
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,  # 无缓冲
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # 读取初始输出直到看到主菜单
        output_buffer = ""
        start_time = time.time()
        while "请选择功能 (1-6):" not in output_buffer and time.time() - start_time < 10:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        if "请选择功能 (1-6):" not in output_buffer:
            pytest.fail("程序没有显示主菜单")

        # 发送输入启动离线联邦学习
        process.stdin.write("1\n")
        process.stdin.flush()

        # 等待参数配置提示
        while "请输入客户端数量" not in output_buffer and time.time() - start_time < 15:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        # 发送参数
        process.stdin.write("5\n10\n5\n0.01\n")
        process.stdin.flush()

        # 等待训练开始
        while "开始训练" not in output_buffer and time.time() - start_time < 20:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        # 等待一点时间让训练开始
        time.sleep(1)

        # 发送SIGINT信号（相当于Ctrl+C）
        process.send_signal(signal.SIGINT)

        # 等待程序响应
        try:
            stdout, stderr = process.communicate(timeout=5)
            full_output = output_buffer + stdout + stderr
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            full_output = output_buffer + stdout + stderr

        # 验证程序优雅退出
        interrupt_keywords = ["中断", "interrupt", "被用户中断", "KeyboardInterrupt", "检测到中断信号", "优雅退出"]
        has_interrupt_message = any(keyword in full_output for keyword in interrupt_keywords)

        # 验证程序能够退出并显示中断信息
        assert process.returncode is not None, "程序应该已经退出"
        assert has_interrupt_message, f"应该显示中断信息，实际输出: {full_output}"

        # 打印输出用于调试
        print(f"程序输出: {full_output}")
        print(f"返回码: {process.returncode}")
        print(f"找到中断信息: {has_interrupt_message}")

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("程序没有在预期时间内响应中断信号")
    except Exception as e:
        process.kill()
        pytest.fail(f"测试过程中发生错误: {e}")

def test_graceful_shutdown():
    """测试优雅关闭功能"""
    # 启动主程序进程
    process = subprocess.Popen(
        ['python', 'src/main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,  # 无缓冲
        cwd=os.path.join(os.path.dirname(__file__), '..', '..')
    )

    try:
        # 读取初始输出直到看到主菜单
        output_buffer = ""
        start_time = time.time()
        while "请选择功能 (1-6):" not in output_buffer and time.time() - start_time < 10:
            try:
                char = process.stdout.read(1)
                if char:
                    output_buffer += char
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

        if "请选择功能 (1-6):" not in output_buffer:
            pytest.fail("程序没有显示主菜单")

        # 发送退出命令
        process.stdin.write("6\n")
        process.stdin.flush()

        # 等待程序退出
        stdout, stderr = process.communicate(timeout=5)
        full_output = output_buffer + stdout + stderr

        # 验证程序正常退出
        assert process.returncode == 0, "程序应该正常退出"
        assert "再见" in full_output, "应该显示退出信息"

    except subprocess.TimeoutExpired:
        process.kill()
        pytest.fail("程序没有在预期时间内正常退出")
    except Exception as e:
        process.kill()
        pytest.fail(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
