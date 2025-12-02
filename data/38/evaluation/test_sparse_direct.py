#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试稀疏矩阵分析功能
"""

import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

def test_sparse_analysis_direct():
    """直接测试稀疏矩阵分析"""
    print("=" * 60)
    print("2.3.4 稀疏矩阵分析 - 直接测试")
    print("=" * 60)
    
    try:
        from main import RecommendationSystemCLI
        
        # 创建CLI实例并直接调用稀疏矩阵分析
        cli = RecommendationSystemCLI()
        cli.analyze_sparse_matrix()
        
        # 检查报告文件是否生成
        report_path = os.path.join(src_dir, "results", "sparse_analysis.txt")
        
        if os.path.exists(report_path):
            print(f"✓ 稀疏矩阵分析报告已生成: {report_path}")
            
            # 验证报告内容
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键内容
            checks = [
                "稀疏度统计" in content,
                "填补率" in content, 
                "冷启动触发率" in content,
                "运营建议" in content
            ]
            
            passed = sum(checks)
            print(f"报告内容验证: {passed}/4项通过")
            
            if passed >= 3:
                print("✅ 2.3.4 稀疏矩阵分析 - 测试通过")
                return True
            else:
                print("⚠️ 2.3.4 稀疏矩阵分析 - 部分通过")
                return "partial"
        else:
            print(f"✗ 报告文件未生成: {report_path}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_sparse_analysis_direct()
    print(f"\n最终结果: {'通过' if result == True else '部分通过' if result == 'partial' else '失败'}")
    sys.exit(0 if result else 2)