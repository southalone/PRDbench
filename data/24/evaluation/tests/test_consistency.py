import pytest
import pandas as pd
import numpy as np
import subprocess
import sys
import os
import re

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def test_centroid_consistency():
    """测试单重心法多次运行结果的一致性"""
    
    # 切换到项目根目录
    root_dir = os.path.join(os.path.dirname(__file__), '../..')
    
    def run_centroid_script():
        """运行单重心法脚本并提取坐标"""
        result = subprocess.run(
            ['python', 'src/单重心法.py'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if result.returncode != 0:
            raise Exception(f"脚本执行失败: {result.stderr}")
        
        # 从输出中提取经度和纬度
        output = result.stdout
        longitude_match = re.search(r'Centroid Longitude:\s*([\d.-]+)', output)
        latitude_match = re.search(r'Centroid Latitude:\s*([\d.-]+)', output)
        
        if not longitude_match or not latitude_match:
            raise Exception(f"无法从输出中提取坐标: {output}")
        
        longitude = float(longitude_match.group(1))
        latitude = float(latitude_match.group(1))
        
        return longitude, latitude
    
    # 第一次运行
    lon1, lat1 = run_centroid_script()
    
    # 第二次运行
    lon2, lat2 = run_centroid_script()
    
    # 验证两次运行结果的一致性（精确到小数点后6位）
    lon_diff = abs(lon1 - lon2)
    lat_diff = abs(lat1 - lat2)
    
    tolerance = 1e-6  # 小数点后6位的容差
    
    assert lon_diff < tolerance, f"经度一致性测试失败: {lon1} vs {lon2}, 差异={lon_diff}"
    assert lat_diff < tolerance, f"纬度一致性测试失败: {lat1} vs {lat2}, 差异={lat_diff}"
    
    print(f"一致性测试通过: 第一次({lon1:.6f}, {lat1:.6f}), 第二次({lon2:.6f}, {lat2:.6f})")