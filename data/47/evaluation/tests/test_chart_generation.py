#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from utils.chart_generator import chart_generator
from config.settings import FILE_PATHS

def main():
    """测试借阅数据可视化功能"""
    print("测试借阅数据可视化功能...")
    
    # 准备测试数据
    borrow_data = {"计算机": 15, "文学": 8, "历史": 5, "科学": 12}
    category_data = {"计算机": 45, "文学": 30, "历史": 15, "科学": 10}
    
    try:
        # 生成柱状图
        bar_chart_path = chart_generator.generate_bar_chart(
            data=borrow_data,
            title="图书借阅统计",
            xlabel="图书分类",
            ylabel="借阅次数",
            filename="borrow_statistics_bar.png"
        )
        
        # 生成饼图
        pie_chart_path = chart_generator.generate_pie_chart(
            data=category_data,
            title="图书分类分布",
            filename="category_distribution_pie.png"
        )
        
        # 检查文件是否生成
        charts_generated = []
        if bar_chart_path and os.path.exists(bar_chart_path):
            print(f"+ 柱状图生成成功: {bar_chart_path}")
            charts_generated.append("柱状图")
        
        if pie_chart_path and os.path.exists(pie_chart_path):
            print(f"+ 饼图生成成功: {pie_chart_path}")
            charts_generated.append("饼图")
        
        if len(charts_generated) >= 2:
            print(f"+ 成功生成{len(charts_generated)}种类型的图表")
            return True
        else:
            print(f"- 只生成了{len(charts_generated)}种图表，需要至少2种")
            return False
            
    except Exception as e:
        print(f"- 图表生成异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
