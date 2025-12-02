import pytest
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def test_cluster_centers_in_anhui_range():
    """测试K-means聚类中心坐标是否在安徽省地理范围内"""
    
    # 读取数据文件
    data_path = os.path.join(os.path.dirname(__file__), '../../src/mdl4.xlsx')
    data = pd.read_excel(data_path)
    
    # 提取经度和纬度列数据
    coordinates = data.iloc[:, 1:].values
    
    # 特征缩放
    scaler = StandardScaler()
    scaled_coordinates = scaler.fit_transform(coordinates)
    
    # 设置聚类数目
    k = 14
    
    # 运行K-means算法
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_coordinates)
    
    # 反向转换聚类中心坐标到原始范围
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    
    # 验证聚类中心坐标在安徽省地理范围内
    valid_centers = 0
    for i, center in enumerate(cluster_centers):
        longitude, latitude = center[0], center[1]
        if 115 <= longitude <= 120 and 30 <= latitude <= 35:
            valid_centers += 1
        print(f"聚类中心 {i+1}: 经度={longitude:.6f}, 纬度={latitude:.6f}")
    
    # 至少12个聚类中心应该在合理范围内
    assert valid_centers >= 12, f"只有 {valid_centers} 个聚类中心在安徽省范围内，少于要求的12个"
    
    print(f"聚类中心坐标验证通过: {valid_centers}/14 个中心在安徽省范围内")