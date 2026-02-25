#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from data_manager import DataManager

def test_product_management():
    """测试商品属性管理功能"""
    try:
        data_manager = DataManager()
        
        # 初始化示例数据
        data_manager.initialize_sample_data()
        print("SUCCESS: 示例数据初始化完成")
        
        # 测试添加商品（使用不冲突的ID）
        new_product = {
            'product_id': 301,
            'name': '测试商品',
            'category': '电子产品',
            'price': 999.99,
            'brand': '测试品牌'
        }
        
        result = data_manager.add_product(new_product)
        if result:
            print("SUCCESS: 商品添加成功")
        
        # 测试查看商品列表
        products = data_manager.get_products_list()
        if len(products) >= 5:
            print(f"SUCCESS: 商品列表查看成功，包含{len(products)}个商品")
        
        return True
        
    except Exception as e:
        print(f"ERROR: 商品管理测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_product_management()
    sys.exit(0 if success else 1)
