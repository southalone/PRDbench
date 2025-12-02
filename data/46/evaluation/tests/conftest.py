#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest configuration file to fix buffer detached issue
"""
import pytest
import gc
import sys
import warnings

def pytest_runtest_setup(item):
    """在每个测试前进行清理"""
    # 强制垃圾回收，避免悬空引用
    gc.collect()
    
    # 确保stdout/stderr状态正常
    if hasattr(sys.stdout, 'flush'):
        try:
            sys.stdout.flush()
        except:
            pass
    if hasattr(sys.stderr, 'flush'):
        try:
            sys.stderr.flush()
        except:
            pass

def pytest_runtest_teardown(item, nextitem):
    """在每个测试后进行清理"""
    # 强制垃圾回收
    gc.collect()