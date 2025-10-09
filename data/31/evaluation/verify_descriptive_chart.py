#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
描述统计图表验证脚本
"""
import os

def verify_descriptive_chart():
    """验证描述统计图表文件生成"""
    path = 'src/output/figures/descriptive_stats_scale_1.png'
    
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    
    if exists and size > 0:
        print(f'File exists and size > 0: {exists} {size}')
        return True
    else:
        print(f'File missing or empty: {exists} {size}')
        return False

if __name__ == '__main__':
    verify_descriptive_chart()