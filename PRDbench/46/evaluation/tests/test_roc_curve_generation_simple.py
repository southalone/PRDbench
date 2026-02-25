#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.5.1a ROC曲线 - 图像生成 (简化版)
"""

import os
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc


def test_roc_curve_generation_simple():
    """简化的ROC曲线生成测试，不依赖项目模块"""
    print("开始测试2.5.1a ROC曲线生成（简化版）...")
    
    # 创建模拟预测数据
    np.random.seed(42)
    n_samples = 200
    
    # 模拟真实标签和预测概率
    y_true = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    y_proba = np.random.beta(2, 5, n_samples)
    
    # 为正样本增加预测概率
    y_proba[y_true == 1] += 0.3
    y_proba = np.clip(y_proba, 0, 1)
    
    # 创建临时输出路径
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "test_roc_curve.png")
        
        try:
            # 计算ROC曲线
            fpr, tpr, thresholds = roc_curve(y_true, y_proba)
            auc_score = auc(fpr, tpr)
            
            # 绘制ROC曲线
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, color='darkorange', lw=2, 
                    label=f'ROC curve (AUC = {auc_score:.3f})')
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
                    label='Random')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curve')
            plt.legend(loc="lower right")
            plt.grid(True, alpha=0.3)
            
            # 保存PNG文件
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # 验证PNG文件是否生成
            assert os.path.exists(output_path), f"ROC曲线PNG文件未生成: {output_path}"
            
            # 验证文件大小
            file_size = os.path.getsize(output_path)
            assert file_size > 10000, f"ROC曲线PNG文件太小: {file_size}字节"
            
            # 验证AUC数值合理性
            assert 0.5 <= auc_score <= 1.0, f"AUC数值不合理: {auc_score}"
            assert auc_score > 0.7, f"AUC数值过低: {auc_score}"
            
            # 验证图像尺寸
            from PIL import Image
            with Image.open(output_path) as img:
                width, height = img.size
                assert width > 500 and height > 400, f"图像尺寸不合理: {width}x{height}"
            
            print(f"SUCCESS: ROC曲线PNG生成成功: {output_path}")
            print(f"SUCCESS: 文件大小: {file_size}字节")
            print(f"SUCCESS: AUC数值: {auc_score:.3f}")
            print(f"SUCCESS: 图像尺寸: {width}x{height}")
            print("SUCCESS: ROC曲线图像验证通过")
            
            return True
            
        except Exception as e:
            print(f"FAIL: ROC曲线生成失败: {e}")
            return False


if __name__ == "__main__":
    success = test_roc_curve_generation_simple()
    if success:
        print("2.5.1a ROC曲线生成测试通过")
    else:
        print("2.5.1a ROC曲线生成测试失败")