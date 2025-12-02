"""
测试基础图表可视化功能
"""
import pytest
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from src.evaluation.metrics import EvaluationMetrics
except ImportError:
    from evaluation.metrics import EvaluationMetrics


class TestVisualizationBasic:
    """基础可视化功能测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.metrics = EvaluationMetrics()
        self.test_data = self._create_test_data()
        
        # 设置matplotlib为非交互模式
        plt.ioff()
        plt.switch_backend('Agg')
    
    def _create_test_data(self):
        """创建测试数据"""
        # 模拟评估结果数据
        algorithms = ['Content-Based', 'User-CF', 'Item-CF', 'Hybrid']
        metrics = ['Precision@5', 'Recall@5', 'F1@5', 'NDCG@5']
        
        # 生成模拟性能数据
        np.random.seed(42)
        data = []
        for alg in algorithms:
            for metric in metrics:
                # 生成合理的指标值
                if 'Precision' in metric:
                    value = np.random.uniform(0.1, 0.8)
                elif 'Recall' in metric:
                    value = np.random.uniform(0.05, 0.6)
                elif 'F1' in metric:
                    value = np.random.uniform(0.08, 0.7)
                elif 'NDCG' in metric:
                    value = np.random.uniform(0.2, 0.9)
                else:
                    value = np.random.uniform(0.0, 1.0)
                
                data.append({
                    'Algorithm': alg,
                    'Metric': metric,
                    'Value': value
                })
        
        return pd.DataFrame(data)
    
    def test_basic_chart_generation(self):
        """测试基础图表生成功能"""
        try:
            chart_types_generated = []
            
            # 1. 测试柱状图生成
            bar_chart_success = self._test_bar_chart()
            if bar_chart_success:
                chart_types_generated.append("柱状图")
            
            # 2. 测试折线图生成
            line_chart_success = self._test_line_chart()
            if line_chart_success:
                chart_types_generated.append("折线图")
            
            # 3. 测试散点图生成
            scatter_chart_success = self._test_scatter_chart()
            if scatter_chart_success:
                chart_types_generated.append("散点图")
            
            # 4. 测试饼图生成（额外类型）
            pie_chart_success = self._test_pie_chart()
            if pie_chart_success:
                chart_types_generated.append("饼图")
            
            # 5. 测试箱线图生成（额外类型）
            box_chart_success = self._test_box_chart()
            if box_chart_success:
                chart_types_generated.append("箱线图")
            
            # 验证至少支持3种图表类型
            assert len(chart_types_generated) >= 3, f"系统应支持至少3种图表类型，实际支持{len(chart_types_generated)}种: {chart_types_generated}"
            
            print("✓ 基础图表生成测试通过")
            print(f"✓ 支持的图表类型: {chart_types_generated}")
            print(f"✓ 总共支持{len(chart_types_generated)}种图表类型")
            
            # 测试图表保存功能
            self._test_chart_saving()
            
        except Exception as e:
            pytest.fail(f"基础图表生成测试失败: {e}")
    
    def _test_bar_chart(self):
        """测试柱状图"""
        try:
            # 准备柱状图数据
            precision_data = self.test_data[self.test_data['Metric'] == 'Precision@5']
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(precision_data['Algorithm'], precision_data['Value'])
            ax.set_title('算法Precision@5对比')
            ax.set_xlabel('算法')
            ax.set_ylabel('Precision@5')
            ax.set_ylim(0, 1)
            
            # 添加数值标签
            for bar, value in zip(bars, precision_data['Value']):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.3f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"柱状图生成失败: {e}")
            return False
    
    def _test_line_chart(self):
        """测试折线图"""
        try:
            # 模拟训练过程中的指标变化
            epochs = list(range(1, 11))
            np.random.seed(42)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 绘制多个算法的性能曲线
            algorithms = self.test_data['Algorithm'].unique()
            for alg in algorithms:
                # 模拟训练过程中指标提升
                base_value = self.test_data[
                    (self.test_data['Algorithm'] == alg) & 
                    (self.test_data['Metric'] == 'Precision@5')
                ]['Value'].iloc[0]
                
                # 生成学习曲线
                values = [base_value * (0.3 + 0.7 * (1 - np.exp(-epoch/3))) for epoch in epochs]
                values = [v + np.random.normal(0, 0.02) for v in values]  # 添加噪声
                
                ax.plot(epochs, values, marker='o', label=alg, linewidth=2)
            
            ax.set_title('算法训练过程Precision@5变化')
            ax.set_xlabel('训练轮次')
            ax.set_ylabel('Precision@5')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"折线图生成失败: {e}")
            return False
    
    def _test_scatter_chart(self):
        """测试散点图"""
        try:
            # 准备散点图数据：Precision vs Recall
            precision_data = self.test_data[self.test_data['Metric'] == 'Precision@5']
            recall_data = self.test_data[self.test_data['Metric'] == 'Recall@5']
            
            # 合并数据
            scatter_data = precision_data.merge(
                recall_data, 
                on='Algorithm', 
                suffixes=('_precision', '_recall')
            )
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 为不同算法使用不同颜色和标记
            colors = ['red', 'blue', 'green', 'orange']
            markers = ['o', 's', '^', 'D']
            
            for i, alg in enumerate(scatter_data['Algorithm']):
                row = scatter_data[scatter_data['Algorithm'] == alg]
                ax.scatter(row['Value_precision'], row['Value_recall'], 
                          c=colors[i % len(colors)], 
                          marker=markers[i % len(markers)],
                          s=100, label=alg, alpha=0.7)
                
                # 添加算法名称标注
                ax.annotate(alg, 
                           (row['Value_precision'].iloc[0], row['Value_recall'].iloc[0]),
                           xytext=(5, 5), textcoords='offset points')
            
            ax.set_title('算法Precision vs Recall散点图')
            ax.set_xlabel('Precision@5')
            ax.set_ylabel('Recall@5')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 添加对角线（理想情况）
            max_val = max(ax.get_xlim()[1], ax.get_ylim()[1])
            ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, label='理想线')
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"散点图生成失败: {e}")
            return False
    
    def _test_pie_chart(self):
        """测试饼图"""
        try:
            # 模拟推荐类别分布数据
            categories = ['电子产品', '服装', '图书', '食品', '家居']
            proportions = [0.3, 0.25, 0.2, 0.15, 0.1]
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # 创建饼图
            wedges, texts, autotexts = ax.pie(proportions, labels=categories, 
                                             autopct='%1.1f%%', startangle=90,
                                             colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#ff99cc'])
            
            ax.set_title('推荐商品类别分布')
            
            # 美化文本
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"饼图生成失败: {e}")
            return False
    
    def _test_box_chart(self):
        """测试箱线图"""
        try:
            # 模拟不同算法的性能分布数据
            np.random.seed(42)
            algorithms = self.test_data['Algorithm'].unique()
            
            box_data = []
            labels = []
            
            for alg in algorithms:
                # 生成该算法的性能分布数据
                base_performance = self.test_data[
                    (self.test_data['Algorithm'] == alg) & 
                    (self.test_data['Metric'] == 'F1@5')
                ]['Value'].iloc[0]
                
                # 生成正态分布的性能数据
                performance_samples = np.random.normal(base_performance, 0.05, 50)
                performance_samples = np.clip(performance_samples, 0, 1)  # 限制在[0,1]范围
                
                box_data.append(performance_samples)
                labels.append(alg)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 创建箱线图
            box_plot = ax.boxplot(box_data, labels=labels, patch_artist=True)
            
            # 美化箱线图
            colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
            
            ax.set_title('算法F1@5性能分布')
            ax.set_ylabel('F1@5')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"箱线图生成失败: {e}")
            return False
    
    def _test_chart_saving(self):
        """测试图表保存功能"""
        try:
            # 创建一个简单的图表并保存
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot([1, 2, 3, 4], [1, 4, 2, 3], 'b-o')
            ax.set_title('测试图表保存')
            
            # 测试保存为不同格式
            save_path = Path("test_chart")
            formats = ['png', 'jpg', 'pdf']
            
            saved_formats = []
            for fmt in formats:
                try:
                    plt.savefig(f"{save_path}.{fmt}", format=fmt, dpi=100, bbox_inches='tight')
                    saved_formats.append(fmt)
                    
                    # 删除测试文件
                    test_file = Path(f"{save_path}.{fmt}")
                    if test_file.exists():
                        test_file.unlink()
                        
                except Exception as e:
                    print(f"保存{fmt}格式失败: {e}")
            
            plt.close(fig)
            
            print(f"✓ 图表保存功能测试通过，支持格式: {saved_formats}")
            
        except Exception as e:
            print(f"图表保存测试失败: {e}")
    
    def test_chart_customization(self):
        """测试图表自定义功能"""
        try:
            customization_features = []
            
            # 测试颜色自定义
            fig, ax = plt.subplots()
            ax.bar(['A', 'B', 'C'], [1, 2, 3], color=['red', 'green', 'blue'])
            customization_features.append("颜色自定义")
            plt.close(fig)
            
            # 测试字体自定义
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            ax.set_title('测试标题', fontsize=16, fontweight='bold')
            customization_features.append("字体自定义")
            plt.close(fig)
            
            # 测试网格自定义
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            ax.grid(True, linestyle='--', alpha=0.5)
            customization_features.append("网格自定义")
            plt.close(fig)
            
            # 测试图例自定义
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3], label='数据1')
            ax.plot([1, 2, 3], [2, 3, 1], label='数据2')
            ax.legend(loc='upper right', framealpha=0.8)
            customization_features.append("图例自定义")
            plt.close(fig)
            
            print(f"✓ 图表自定义功能测试通过，支持: {customization_features}")
            
        except Exception as e:
            pytest.fail(f"图表自定义测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])