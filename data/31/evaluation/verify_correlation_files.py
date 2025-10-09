#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相关热力图文件验证脚本
"""
import os
import glob

def verify_correlation_files():
    """验证相关热力图文件生成"""
    files = glob.glob('src/output/figures/correlation_*.png')
    
    if files:
        print(f'Correlation heatmap files generated: {len(files)} {"files" if len(files) != 1 else "file"}')
        for f in files:
            if os.path.getsize(f) > 0:
                print(f'  {f}: {os.path.getsize(f)} bytes')
        return True
    else:
        print('No correlation files found: 0 files')
        return False

if __name__ == '__main__':
    verify_correlation_files()