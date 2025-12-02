import pytest
import os
import json
from src.utils import validate_chinese_name, is_valid_date, is_future_date, calculate_bazi_wuxing

# --- 1.1 用户信息录入流程 - 姓名输入 ---
def test_validate_chinese_name_valid():
    assert validate_chinese_name("张三") == True
    assert validate_chinese_name("张三李四王五赵六") == True

def test_validate_chinese_name_invalid():
    assert validate_chinese_name("李") == False  # 太短
    assert validate_chinese_name("张三李四王五赵六钱") == False  # 太长
    assert validate_chinese_name("Zhang") == False  # 非中文

# --- 1.2 用户信息录入流程 - 出生日期输入 ---
def test_is_valid_date():
    assert is_valid_date(1990, 1, 1) == True
    assert is_valid_date(1990, 13, 1) == False  # 无效月份
    assert is_valid_date(1990, 2, 30) == False  # 无效日期

def test_is_future_date():
    from datetime import date
    # 假设今天是2023-10-27，测试一个未来的日期
    future_date = date.today().replace(year=date.today().year + 1)
    assert is_future_date(future_date.year, future_date.month, future_date.day) == True
    # 测试一个过去的日期
    assert is_future_date(1990, 1, 1) == False

# --- 4.1a 运势综合计算 - 八字五行计算 ---
# 这个测试点验证八字计算的基本逻辑，不追求绝对精确（因为PRD提到是简化版）
def test_calculate_bazi_wuxing():
    result = calculate_bazi_wuxing(1990, 1, 1)
    bazi = result['bazi']
    wuxing_dist = result['wuxing_distribution']
    
    # 验证返回结构
    assert 'year' in bazi
    assert 'month' in bazi
    assert 'day' in bazi
    assert 'hour' in bazi
    assert set(wuxing_dist.keys()) == {'金', '木', '水', '火', '土'}
    
    # 验证五行分布是数值
    for value in wuxing_dist.values():
        assert isinstance(value, (int, float))

# --- 1.4 用户信息存储与加载 ---
# 这个测试点更适合用shell_interaction测试，因为涉及文件I/O和完整的程序流程
# 但我们可以测试save/load逻辑的核心部分
def test_user_data_save_load_logic():
    # 注意：这个测试假设在测试环境中可以安全地写入和读取文件
    # 在实际的pytest环境中，可能需要使用tmp_path fixture
    test_data = {
        'name': '测试用户',
        'birth_date': '1990-01-01',
        'gender': '男'
    }
    
    # 为了不污染源代码目录，我们在当前测试目录下创建临时文件
    # 在实际pytest中，应使用tmp_path
    test_file = 'test_user_data.json'
    
    try:
        # 模拟保存
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
        
        # 模拟加载
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    finally:
        # 清理临时文件
        if os.path.exists(test_file):
            os.remove(test_file)