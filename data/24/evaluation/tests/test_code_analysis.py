import pytest
import os

def test_standard_scaler_usage():
    """测试聚类算法.py中是否使用了StandardScaler进行坐标标准化"""
    
    # 读取聚类算法.py文件
    code_path = os.path.join(os.path.dirname(__file__), '../../src/聚类算法.py')
    
    with open(code_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含StandardScaler相关代码
    has_standard_scaler = 'StandardScaler' in content
    has_fit_transform = 'fit_transform' in content
    has_import_scaler = 'from sklearn.preprocessing import StandardScaler' in content
    
    assert has_standard_scaler, "代码中未找到StandardScaler"
    assert has_fit_transform, "代码中未找到fit_transform方法"
    assert has_import_scaler, "代码中未导入StandardScaler"
    
    print("StandardScaler使用验证通过")

def test_weight_normalization():
    """测试单重心法.py中是否包含权重归一化处理逻辑"""
    
    # 读取单重心法.py文件
    code_path = os.path.join(os.path.dirname(__file__), '../../src/单重心法.py')
    
    with open(code_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含权重归一化相关代码
    has_weight_normalization = (
        'weights /=' in content or 
        'weights = weights /' in content or 
        'np.sum(weights)' in content
    )
    
    assert has_weight_normalization, "代码中未找到权重归一化处理逻辑"
    
    print("权重归一化处理验证通过")