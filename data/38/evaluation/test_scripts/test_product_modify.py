#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2.1.2c 商品属性管理-修改商品属性 专项测试
严格按照description的4步验证标准
"""
import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from recommendation_system import RecommendationSystem
from main import RecommendationSystemCLI

def test_product_modify():
    """测试商品属性修改功能"""
    
    print("=" * 70)
    print("2.1.2c 商品属性管理-修改商品属性 - 完整严格测试")
    print("=" * 70)
    
    try:
        # 1. 前置校验：检查商品管理界面是否存在修改选项
        print("\n1. 前置校验：检查商品管理界面是否存在修改选项...")
        cli = RecommendationSystemCLI()
        
        # 检查CLI是否有修改商品的方法
        if hasattr(cli, 'modify_product'):
            print("✓ 前置校验通过：商品管理界面存在修改商品功能")
            frontend_check = True
        else:
            print("✗ 前置校验失败：未找到修改商品功能")
            frontend_check = False
        
        # 2. 准备：选择已存在商品，准备修改价格和类别信息  
        print("\n2. 准备：确保系统中有可修改的商品...")
        system = RecommendationSystem()
        
        # 加载数据
        system.data_manager.initialize_sample_data()
        system.load_data(force_reload=True)
        
        # 获取第一个商品作为测试目标
        products_df = system.data_manager.load_products()
        if len(products_df) > 0:
            test_product_id = products_df.iloc[0]['product_id']
            original_product = products_df[products_df['product_id'] == test_product_id].iloc[0]
            print(f"✓ 准备成功：选择商品ID {test_product_id} 进行修改测试")
            print(f"  原始信息：{original_product['name']}, 类别:{original_product['category']}, 价格:{original_product['price']}")
            prepare_success = True
        else:
            print("✗ 准备失败：系统中无可用商品")
            prepare_success = False
            test_product_id = None
            
        # 3. 执行：调用修改功能，更改商品价格和类别
        print(f"\n3. 执行：修改商品ID {test_product_id} 的价格和类别...")
        execute_success = False
        
        if prepare_success and test_product_id:
            # 准备修改数据
            new_updates = {
                'category': '修改后类别',
                'price': original_product['price'] + 100.0
            }
            
            # 直接调用数据管理器的修改方法
            result = system.data_manager.update_product(test_product_id, new_updates)
            
            if result:
                print(f"✓ 执行成功：商品 {test_product_id} 修改完成")
                print(f"  修改内容：类别 -> {new_updates['category']}, 价格 -> {new_updates['price']}")
                execute_success = True
            else:
                print(f"✗ 执行失败：商品修改操作未成功")
        
        # 4. 断言：验证修改后的商品信息正确更新
        print(f"\n4. 断言：验证商品信息是否正确更新...")
        assert_success = False
        
        if execute_success:
            # 重新加载数据验证修改结果
            updated_products = system.data_manager.load_products()
            updated_product = updated_products[updated_products['product_id'] == test_product_id]
            
            if len(updated_product) > 0:
                updated_product = updated_product.iloc[0]
                category_updated = updated_product['category'] == '修改后类别'
                price_updated = abs(updated_product['price'] - (original_product['price'] + 100.0)) < 0.01
                
                if category_updated and price_updated:
                    print(f"✓ 断言成功：商品信息正确更新")
                    print(f"  验证结果：类别已更新为'{updated_product['category']}'，价格已更新为{updated_product['price']}")
                    assert_success = True
                else:
                    print(f"✗ 断言失败：修改信息未正确保存")
                    print(f"  类别更新：{category_updated}, 价格更新：{price_updated}")
            else:
                print(f"✗ 断言失败：修改后无法找到商品记录")
        
        # 测试结果评估
        print("\n" + "=" * 60)
        print("严格测试结果评估")
        print("=" * 60)
        
        results = {
            "前置校验（界面检查）": "PASS" if frontend_check else "FAIL",
            "准备阶段（商品选择）": "PASS" if prepare_success else "FAIL", 
            "执行阶段（修改功能）": "PASS" if execute_success else "FAIL",
            "断言阶段（信息更新）": "PASS" if assert_success else "FAIL"
        }
        
        for step, result in results.items():
            print(f"{step}: {result}")
        
        pass_count = sum(1 for r in results.values() if r == "PASS")
        
        if pass_count == 4:
            print(f"\n✅ 2.1.2c 商品属性修改 - 测试完全通过 (2分)")
            return True
        elif pass_count >= 2:
            print(f"\n⚠️ 2.1.2c 商品属性修改 - 测试部分通过 (1分)")
            print(f"  通过项目：{pass_count}/4")
            return False
        else:
            print(f"\n❌ 2.1.2c 商品属性修改 - 测试失败 (0分)")
            print(f"  通过项目：{pass_count}/4")
            return False
            
    except Exception as e:
        print(f"\nERROR: 商品修改测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_product_modify()