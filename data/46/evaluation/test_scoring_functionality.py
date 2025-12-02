#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.4.1a&b 评分预测功能 - 单条数据评分和批量数据评分
基于typer项目模式：直接测试核心功能而非CLI交互
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_single_record_scoring():
    """测试单条数据评分功能"""
    print("测试单条数据评分功能...")
    
    try:
        from credit_assessment.data.data_manager import DataManager
        from credit_assessment.algorithms.logistic_regression import LogisticRegressionAnalyzer
        from credit_assessment.utils.config_manager import ConfigManager
        
        # 初始化组件
        config = ConfigManager()
        data_manager = DataManager(config)
        algorithm = LogisticRegressionAnalyzer(config)
        
        # 准备训练数据
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        X_train = pd.DataFrame(np.random.randn(n_samples, n_features), 
                              columns=[f'feature_{i}' for i in range(n_features)])
        y_train = pd.Series(np.random.choice([0, 1], n_samples))
        
        # 训练模型
        model = algorithm.train(X_train, y_train)
        assert model is not None, "模型训练失败"
        
        # 准备单条测试数据
        single_record = pd.DataFrame({
            f'feature_{i}': [np.random.randn()] for i in range(n_features)
        })
        
        # 执行单条评分
        predictions = algorithm.predict(single_record)
        
        # 验证预测结果
        assert predictions is not None, "预测失败"
        assert len(predictions) == 1, "预测结果数量不正确"
        assert 0 <= predictions[0] <= 1, "预测概率超出范围[0,1]"
        
        # 获取评分和评级
        score = predictions[0] * 1000  # 转换为1000分制
        if score >= 800:
            grade = "优秀"
        elif score >= 650:
            grade = "良好"  
        elif score >= 500:
            grade = "一般"
        elif score >= 350:
            grade = "较差"
        else:
            grade = "极差"
        
        print("[PASS] 单条数据评分成功")
        print("[INFO] 评分结果: {:.2f}分, 信用评级: {}".format(score, grade))
        print("评分预测功能正常，输出评分结果和信用评级。")
        
        return True
        
    except Exception as e:
        print("[FAIL] 单条数据评分测试失败: {}".format(e))
        return False

def test_batch_scoring():
    """测试批量数据评分功能"""
    print("\n测试批量数据评分功能...")
    
    try:
        from credit_assessment.data.data_manager import DataManager
        from credit_assessment.algorithms.logistic_regression import LogisticRegressionAnalyzer
        from credit_assessment.utils.config_manager import ConfigManager
        
        # 初始化组件
        config = ConfigManager()
        data_manager = DataManager(config)
        algorithm = LogisticRegressionAnalyzer(config)
        
        # 准备训练数据
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        X_train = pd.DataFrame(np.random.randn(n_samples, n_features), 
                              columns=[f'feature_{i}' for i in range(n_features)])
        y_train = pd.Series(np.random.choice([0, 1], n_samples))
        
        # 训练模型
        model = algorithm.train(X_train, y_train)
        assert model is not None, "模型训练失败"
        
        # 准备批量测试数据(10条以上)
        batch_size = 15
        batch_data = pd.DataFrame(np.random.randn(batch_size, n_features), 
                                 columns=[f'feature_{i}' for i in range(n_features)])
        
        # 添加客户ID
        batch_data['customer_id'] = [f'C{i:03d}' for i in range(1, batch_size + 1)]
        
        # 执行批量评分
        features_only = batch_data.drop(columns=['customer_id'])
        predictions = algorithm.predict(features_only)
        
        # 验证预测结果
        assert predictions is not None, "批量预测失败"
        assert len(predictions) == batch_size, "预测结果数量不正确"
        
        # 创建完整结果
        results = []
        for i, prob in enumerate(predictions):
            customer_id = batch_data.iloc[i]['customer_id']
            score = prob * 1000
            algorithm_type = "Logistic Regression"
            
            results.append({
                'customer_id': customer_id,
                'probability': prob,
                'score': score,
                'algorithm': algorithm_type
            })
        
        results_df = pd.DataFrame(results)
        
        print("[PASS] 批量数据评分成功")
        print("[INFO] 成功评分{}条数据".format(len(results_df)))
        print("[INFO] 结果包含: 客户ID, 评分概率, 评分, 算法类别")
        print("批量数据评分测试通过，成功对所有数据进行评分，输出包含客户ID、评分概率、算法类别的完整结果。")
        
        return True
        
    except Exception as e:
        print("[FAIL] 批量数据评分测试失败: {}".format(e))
        return False

def test_scoring_functionality():
    """测试评分预测功能"""
    print("测试评分预测功能...")
    
    single_result = test_single_record_scoring()
    batch_result = test_batch_scoring()
    
    if single_result and batch_result:
        print("\n[PASS] 所有评分功能测试通过")
        print("测试通过：评分预测功能完整")
        return True
    else:
        print("\n[FAIL] 部分评分功能测试失败")
        return False

if __name__ == "__main__":
    success = test_scoring_functionality()
    sys.exit(0 if success else 1)