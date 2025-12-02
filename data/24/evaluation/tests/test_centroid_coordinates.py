import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def test_centroid_in_anhui_range():
    """测试单重心法计算的重心坐标是否在安徽省地理范围内"""
    
    # 读取数据文件
    data_path = os.path.join(os.path.dirname(__file__), '../../src/聚类之后.xlsx')
    data = pd.read_excel(data_path)
    
    # 提取经度、纬度和权重列
    longitudes = data.iloc[:, 1].values
    latitudes = data.iloc[:, 2].values
    weights = data.iloc[:, 3].values.astype(float)
    
    # 归一化权重
    weights /= np.sum(weights)
    
    # 计算重心
    center_longitude = np.dot(longitudes, weights)
    center_latitude = np.dot(latitudes, weights)
    
    # 验证重心坐标在安徽省地理范围内
    assert 115 <= center_longitude <= 120, f"重心经度 {center_longitude} 不在安徽省范围内 (115-120)"
    assert 30 <= center_latitude <= 35, f"重心纬度 {center_latitude} 不在安徽省范围内 (30-35)"
    
    print(f"重心坐标验证通过: 经度={center_longitude:.6f}, 纬度={center_latitude:.6f}")