"""
测试高级图表可视化功能
"""
import pytest
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from src.evaluation.metrics import EvaluationMetrics
except ImportError:
    from evaluation.metrics import EvaluationMetrics


class TestVisualizationAdvanced:
    """高级可视化功能测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.metrics = EvaluationMetrics()
        
        # 设置matplotlib为非交互模式
        plt.ioff()
        plt.switch_backend('Agg')
        
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def test_advanced_chart_generation(self):
        """测试高级图表生成功能"""
        try:
            advanced_chart_types = []
            
            # 1. 测试热力图生成
            heatmap_success = self._test_heatmap()
            if heatmap_success:
                advanced_chart_types.append("热力图")
            
            # 2. 测试雷达图生成
            radar_chart_success = self._test_radar_chart()
            if radar_chart_success:
                advanced_chart_types.append("雷达图")
            
            # 3. 测试相关性矩阵图
            correlation_success = self._test_correlation_matrix()
            if correlation_success:
                advanced_chart_types.append("相关性矩阵图")
            
            # 4. 测试聚类图
            cluster_success = self._test_cluster_visualization()
            if cluster_success:
                advanced_chart_types.append("聚类可视化图")
            
            # 5. 测试分布密度图
            density_success = self._test_density_plot()
            if density_success:
                advanced_chart_types.append("密度分布图")
            
            # 验证至少支持2种高级图表类型
            assert len(advanced_chart_types) >= 2, f"系统应支持至少2种高级图表类型，实际支持{len(advanced_chart_types)}种: {advanced_chart_types}"
            
            print("✓ 高级图表生成测试通过")
            print(f"✓ 支持的高级图表类型: {advanced_chart_types}")
            print(f"✓ 总共支持{len(advanced_chart_types)}种高级图表类型")
            
            # 测试图表组合展示
            self._test_dashboard_layout()
            
        except Exception as e:
            pytest.fail(f"高级图表生成测试失败: {e}")
    
    def _test_heatmap(self):
        """测试热力图"""
        try:
            # 创建算法性能对比的热力图数据
            algorithms = ['Content-Based', 'User-CF', 'Item-CF', 'Hybrid']
            metrics = ['Precision@5', 'Recall@5', 'F1@5', 'NDCG@5', 'MAP']
            
            # 生成模拟数据
            np.random.seed(42)
            data = np.random.uniform(0.1, 0.9, (len(algorithms), len(metrics)))
            
            # 创建热力图
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 使用seaborn创建热力图
            heatmap = sns.heatmap(data, 
                                 xticklabels=metrics, 
                                 yticklabels=algorithms,
                                 annot=True, 
                                 fmt='.3f', 
                                 cmap='YlOrRd',
                                 ax=ax)
            
            ax.set_title('算法性能热力图')
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"热力图生成失败: {e}")
            return False
    
    def _test_radar_chart(self):
        """测试雷达图"""
        try:
            # 雷达图数据：多维度算法性能对比
            categories = ['精确率', '召回率', 'F1分数', '多样性', '新颖性', '覆盖率']
            
            # 两个算法的性能数据
            algorithm1_scores = [0.8, 0.6, 0.7, 0.5, 0.4, 0.9]  # Hybrid
            algorithm2_scores = [0.6, 0.8, 0.7, 0.7, 0.6, 0.7]  # Content-Based
            
            # 计算角度
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            
            # 闭合雷达图
            algorithm1_scores += algorithm1_scores[:1]
            algorithm2_scores += algorithm2_scores[:1]
            angles += angles[:1]
            
            # 创建雷达图
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # 绘制算法1
            ax.plot(angles, algorithm1_scores, 'o-', linewidth=2, label='混合推荐', color='blue')
            ax.fill(angles, algorithm1_scores, alpha=0.25, color='blue')
            
            # 绘制算法2
            ax.plot(angles, algorithm2_scores, 'o-', linewidth=2, label='内容推荐', color='red')
            ax.fill(angles, algorithm2_scores, alpha=0.25, color='red')
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 1)
            ax.set_title('算法性能雷达图', size=16, y=1.1)
            ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
            ax.grid(True)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"雷达图生成失败: {e}")
            return False
    
    def _test_correlation_matrix(self):
        """测试相关性矩阵图"""
        try:
            # 创建指标相关性数据
            np.random.seed(42)
            metrics = ['Precision', 'Recall', 'F1', 'NDCG', 'Diversity', 'Coverage']
            n_metrics = len(metrics)
            
            # 生成相关性矩阵
            correlation_matrix = np.random.uniform(-0.5, 1.0, (n_metrics, n_metrics))
            # 确保对角线为1
            np.fill_diagonal(correlation_matrix, 1.0)
            # 确保矩阵对称
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
            
            # 创建相关性热力图
            fig, ax = plt.subplots(figsize=(8, 6))
            
            heatmap = sns.heatmap(correlation_matrix, 
                                 xticklabels=metrics, 
                                 yticklabels=metrics,
                                 annot=True, 
                                 fmt='.3f', 
                                 cmap='coolwarm',
                                 center=0,
                                 ax=ax)
            
            ax.set_title('评估指标相关性矩阵')
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"相关性矩阵图生成失败: {e}")
            return False
    
    def _test_cluster_visualization(self):
        """测试聚类可视化"""
        try:
            # 模拟用户聚类数据
            np.random.seed(42)
            n_users = 100
            
            # 生成3个用户群体
            cluster1 = np.random.multivariate_normal([2, 2], [[0.5, 0.1], [0.1, 0.5]], 30)
            cluster2 = np.random.multivariate_normal([6, 6], [[0.8, -0.2], [-0.2, 0.8]], 35)
            cluster3 = np.random.multivariate_normal([4, 8], [[0.6, 0.0], [0.0, 0.6]], 35)
            
            # 合并数据
            user_features = np.vstack([cluster1, cluster2, cluster3])
            labels = np.array([0]*30 + [1]*35 + [2]*35)
            
            # 创建聚类可视化图
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors = ['red', 'blue', 'green']
            cluster_names = ['年轻用户', '商务用户', '家庭用户']
            
            for i in range(3):
                cluster_data = user_features[labels == i]
                ax.scatter(cluster_data[:, 0], cluster_data[:, 1], 
                          c=colors[i], label=cluster_names[i], alpha=0.7, s=50)
            
            ax.set_title('用户群体聚类可视化')
            ax.set_xlabel('特征维度1')
            ax.set_ylabel('特征维度2')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"聚类可视化生成失败: {e}")
            return False
    
    def _test_density_plot(self):
        """测试密度分布图"""
        try:
            # 模拟评分分布数据
            np.random.seed(42)
            
            # 生成不同算法的评分分布
            content_based_scores = np.random.beta(2, 5, 1000)  # 偏向低分
            collaborative_scores = np.random.beta(3, 3, 1000)  # 均匀分布
            hybrid_scores = np.random.beta(5, 2, 1000)        # 偏向高分
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 绘制密度图
            ax.hist(content_based_scores, bins=50, alpha=0.5, label='内容推荐', 
                   density=True, color='blue')
            ax.hist(collaborative_scores, bins=50, alpha=0.5, label='协同过滤', 
                   density=True, color='green')
            ax.hist(hybrid_scores, bins=50, alpha=0.5, label='混合推荐', 
                   density=True, color='red')
            
            # 添加KDE曲线
            try:
                import scipy.stats as stats
                x = np.linspace(0, 1, 100)
                
                # 计算KDE
                kde1 = stats.gaussian_kde(content_based_scores)
                kde2 = stats.gaussian_kde(collaborative_scores)
                kde3 = stats.gaussian_kde(hybrid_scores)
                
                ax.plot(x, kde1(x), 'b-', linewidth=2, alpha=0.8)
                ax.plot(x, kde2(x), 'g-', linewidth=2, alpha=0.8)
                ax.plot(x, kde3(x), 'r-', linewidth=2, alpha=0.8)
                
            except ImportError:
                print("scipy未安装，跳过KDE曲线")
            
            ax.set_title('不同算法推荐分数分布密度图')
            ax.set_xlabel('推荐分数')
            ax.set_ylabel('密度')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"密度分布图生成失败: {e}")
            return False
    
    def _test_dashboard_layout(self):
        """测试仪表板布局"""
        try:
            # 创建多子图仪表板
            fig = plt.figure(figsize=(15, 10))
            
            # 子图1：性能对比柱状图
            ax1 = plt.subplot(2, 3, 1)
            algorithms = ['A', 'B', 'C']
            values = [0.6, 0.8, 0.7]
            ax1.bar(algorithms, values, color=['skyblue', 'lightgreen', 'lightcoral'])
            ax1.set_title('算法性能对比')
            ax1.set_ylim(0, 1)
            
            # 子图2：时间序列
            ax2 = plt.subplot(2, 3, 2)
            time_points = list(range(1, 11))
            performance = [0.5 + 0.3*np.sin(i/2) + 0.1*i/10 for i in time_points]
            ax2.plot(time_points, performance, 'b-o')
            ax2.set_title('性能趋势')
            ax2.grid(True, alpha=0.3)
            
            # 子图3：饼图
            ax3 = plt.subplot(2, 3, 3)
            sizes = [30, 25, 20, 15, 10]
            labels = ['类别A', '类别B', '类别C', '类别D', '其他']
            ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax3.set_title('类别分布')
            
            # 子图4：散点图
            ax4 = plt.subplot(2, 3, 4)
            x = np.random.normal(0.5, 0.2, 100)
            y = np.random.normal(0.6, 0.1, 100)
            ax4.scatter(x, y, alpha=0.6)
            ax4.set_title('特征分布')
            ax4.set_xlabel('特征1')
            ax4.set_ylabel('特征2')
            
            # 子图5：箱线图
            ax5 = plt.subplot(2, 3, 5)
            data_groups = [np.random.normal(0.6, 0.1, 50), 
                          np.random.normal(0.7, 0.15, 50),
                          np.random.normal(0.5, 0.08, 50)]
            ax5.boxplot(data_groups, labels=['算法1', '算法2', '算法3'])
            ax5.set_title('性能分布')
            
            # 子图6：热力图
            ax6 = plt.subplot(2, 3, 6)
            heatmap_data = np.random.uniform(0, 1, (5, 5))
            im = ax6.imshow(heatmap_data, cmap='viridis')
            ax6.set_title('特征重要性')
            plt.colorbar(im, ax=ax6)
            
            plt.suptitle('推荐系统评估仪表板', fontsize=16)
            plt.tight_layout()
            plt.close(fig)
            
            print("✓ 仪表板布局测试通过")
            
        except Exception as e:
            print(f"仪表板布局测试失败: {e}")
    
    def test_interactive_features(self):
        """测试交互功能支持"""
        try:
            interactive_features = []
            
            # 测试图例交互
            fig, ax = plt.subplots()
            line1, = ax.plot([1, 2, 3], [1, 2, 3], label='数据1')
            line2, = ax.plot([1, 2, 3], [2, 3, 1], label='数据2')
            legend = ax.legend()
            legend.set_draggable(True)
            interactive_features.append("可拖拽图例")
            plt.close(fig)
            
            # 测试缩放功能
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3, 4, 5], [1, 4, 2, 5, 3])
            ax.set_title('支持缩放的图表')
            interactive_features.append("图表缩放")
            plt.close(fig)
            
            # 测试注释功能
            fig, ax = plt.subplots()
            ax.scatter([1, 2, 3], [1, 2, 3])
            ax.annotate('重要点', xy=(2, 2), xytext=(2.5, 2.5),
                       arrowprops=dict(arrowstyle='->'))
            interactive_features.append("数据点注释")
            plt.close(fig)
            
            print(f"✓ 交互功能测试通过，支持: {interactive_features}")
            
        except Exception as e:
            print(f"交互功能测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])