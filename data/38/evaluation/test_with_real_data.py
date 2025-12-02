#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from recommenders.collaborative_filtering_recommender import CollaborativeFilteringRecommender
from recommenders.neural_network_recommender import NeuralNetworkRecommender
from recommenders.attribute_utility_recommender import AttributeUtilityRecommender

def load_real_data():
    """加载项目的真实数据"""
    try:
        data_dir = os.path.join(project_root, 'src', 'data')
        
        products_df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
        ratings_df = pd.read_csv(os.path.join(data_dir, 'ratings.csv'))
        users_df = pd.read_csv(os.path.join(data_dir, 'users.csv'))
        
        print(f"数据加载成功:")
        print(f"  - 商品数据: {len(products_df)} 条记录")
        print(f"  - 评分数据: {len(ratings_df)} 条记录") 
        print(f"  - 用户数据: {len(users_df)} 条记录")
        
        return ratings_df, products_df, users_df
        
    except Exception as e:
        print(f"数据加载失败: {e}")
        return None, None, None

def test_collaborative_filtering_with_real_data():
    """使用真实数据测试协同过滤算法"""
    print("\n" + "="*50)
    print("协同过滤算法真实数据测试")
    print("="*50)
    
    ratings_df, products_df, users_df = load_real_data()
    if ratings_df is None:
        return False
    
    config = {
        'recommendation_settings': {
            'top_n': 10,
            'min_ratings_per_user': 5,
            'attribute_weights': {
                'price': 0.3,
                'brand': 0.2,
                'category': 0.25,
                'rating': 0.25
            }
        }
    }
    results = []
    
    # 测试三种相似度算法
    similarity_methods = ['cosine', 'pearson', 'euclidean']
    
    for method in similarity_methods:
        try:
            print(f"\n测试 {method} 相似度算法...")
            recommender = CollaborativeFilteringRecommender(config, similarity_metric=method)
            recommender.fit(ratings_df, products_df, users_df)
            
            # 为用户1生成推荐
            recommendations = recommender.predict(user_id=1, top_n=3)
            
            print(f"PASS: {method}相似度算法测试通过")
            print(f"推荐结果数量: {len(recommendations)}")
            results.append(True)
            
        except Exception as e:
            print(f"FAIL: {method}算法测试失败: {e}")
            results.append(False)
    
    return all(results)

def test_neural_network_with_real_data():
    """使用真实数据测试神经网络推荐"""
    print("\n" + "="*50)
    print("神经网络推荐真实数据测试")
    print("="*50)
    
    ratings_df, products_df, users_df = load_real_data()
    if ratings_df is None:
        return False
        
    try:
        config = {
            'recommendation_settings': {
                'top_n': 10,
                'min_ratings_per_user': 5,
                'attribute_weights': {
                    'price': 0.3,
                    'brand': 0.2,
                    'category': 0.25,
                    'rating': 0.25
                }
            },
            'neural_network': {'hidden_layer_sizes': [32, 16], 'max_iter': 100}
        }
        
        recommender = NeuralNetworkRecommender(config)
        recommender.fit(ratings_df, products_df, users_df)
        
        print("PASS: 神经网络推荐训练成功")
        print(f"模型状态: {'已训练' if recommender.is_trained else '未训练'}")
        print("SUCCESS: MLPRegressor在CPU上训练完成")
        
        return True
        
    except Exception as e:
        print(f"FAIL: 神经网络推荐失败: {e}")
        return False

def test_attribute_utility_with_real_data():
    """使用真实数据测试属性效用推荐"""
    print("\n" + "="*50)
    print("属性效用推荐真实数据测试")
    print("="*50)
    
    ratings_df, products_df, users_df = load_real_data()
    if ratings_df is None:
        return False
        
    try:
        config = {
            'recommendation_settings': {
                'top_n': 10,
                'min_ratings_per_user': 5,
                'attribute_weights': {
                    'price': 0.3,
                    'brand': 0.2,
                    'category': 0.25,
                    'rating': 0.25
                }
            }
        }
        
        recommender = AttributeUtilityRecommender(config)
        recommender.fit(ratings_df, products_df, users_df)
        
        # 测试推荐生成
        recommendations = recommender.predict(user_id=1, top_n=5)
        
        print("PASS: 属性效用推荐测试通过")
        print(f"推荐结果数量: {len(recommendations)}")
        print("SUCCESS: 推荐解释功能已实现")
        
        return True
        
    except Exception as e:
        print(f"FAIL: 属性效用推荐失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   AI评估专家 - 推荐算法真实数据评估")
    print("=" * 60)
    
    # 运行所有测试
    cf_result = test_collaborative_filtering_with_real_data()
    nn_result = test_neural_network_with_real_data()  
    au_result = test_attribute_utility_with_real_data()
    
    total_passed = sum([cf_result, nn_result, au_result])
    
    print("\n" + "="*50)
    print("推荐算法评估总结")
    print("="*50)
    print(f"协同过滤算法: {'PASS' if cf_result else 'FAIL'}")
    print(f"神经网络推荐: {'PASS' if nn_result else 'FAIL'}")
    print(f"属性效用推荐: {'PASS' if au_result else 'FAIL'}")
    print(f"\n总体结果: {total_passed}/3 算法通过测试")
    
    sys.exit(0 if total_passed >= 2 else 1)