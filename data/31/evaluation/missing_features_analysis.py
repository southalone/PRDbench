#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析PRD需求与测试计划的差异，找出未实现的功能
"""
import json

def analyze_missing_features():
    # 读取detailed_test_plan.json
    with open('evaluation/detailed_test_plan.json', 'r', encoding='utf-8') as f:
        test_plan_data = json.load(f)
    
    # 提取所有测试的metric
    implemented_features = set()
    for item in test_plan_data:
        implemented_features.add(item["metric"])
    
    print("=== 已实现的功能（基于测试计划） ===")
    for i, feature in enumerate(sorted(implemented_features), 1):
        print(f"{i:2d}. {feature}")
    
    print(f"\n总计: {len(implemented_features)} 个功能")
    
    # PRD中提到的功能需求
    prd_requirements = {
        # 2.1 量表自定义与信效度分析模块
        "量表设计管理": [
            "量表创建、编辑",
            "量表导入/导出（CSV/JSON格式）",
            "量表结构定义（内容、条目、维度、计分方式、反向条目）",
            "量表版本管理",
            "量表批量发布"
        ],
        "项目分析与探索性因素分析（EFA）": [
            "条目分布、均值/方差分析",
            "极端分组分析",
            "相关性分析",
            "KMO、Bartlett球形检验",
            "主成分分析",
            "最大方差旋转",
            "因子载荷矩阵输出",
            "因子解释方差比"
        ],
        "信效度检验": [
            "Cronbach's α系数",
            "分半信度",
            "重测信度",
            "同质性分析",
            "区分度分析",
            "因子结构有效性",
            "项目剔除建议",
            "信效度可视化"
        ],
        
        # 2.2 被试数据采集与数据管理
        "数据采集": [
            "批量被试信息导入",
            "多量表答题录入",
            "CSV批量导入",
            "Web录入界面（可选）",
            "跳题、漏题检测",
            "数据异常修正建议",
            "分组标签划分"
        ],
        "数据版本与权限管理": [
            "分批次采集版本管理",
            "多中心采集管理",
            "分级权限管理",
            "数据访问控制"
        ],
        
        # 2.3 特征分组与差异分析
        "基本特征分析": [
            "描述统计（均值/标准差/分位数/偏态/峰度）",
            "分组柱状图/箱线图",
            "独立样本t检验",
            "ANOVA方差分析",
            "效应量计算",
            "组间均值差可视化"
        ],
        "趋势与横断分析": [
            "年级递变趋势分析",
            "回归斜率分析",
            "趋势拟合图"
        ],
        
        # 2.4 高阶关系与路径分析
        "指标相关与预测作用分析": [
            "Pearson/Spearman相关矩阵",
            "相关矩阵可视化（热力图）",
            "线性回归分析",
            "多元回归分析",
            "Logistic回归分析",
            "标准化系数输出"
        ],
        "分层预测与路径结构模型": [
            "结构方程建模（SEM）",
            "路径分析",
            "中介分析",
            "路径系数图可视化",
            "直接/间接效应分解",
            "自举法置信区间",
            "模型拟合优度指标（CFI, TLI, RMSEA, SRMR）"
        ],
        
        # 2.5 报告与可视化导出
        "智能报告生成": [
            "分析摘要报告",
            "样本描述",
            "差异检验报告",
            "路径系数表",
            "显著性解读",
            "中英双语支持",
            "报告模板自定义",
            "批量报告生成"
        ],
        "图表与数据导出": [
            "PNG格式导出",
            "PDF格式导出",
            "SVG格式导出",
            "CSV数据导出",
            "Excel数据导出",
            "图表样式定制",
            "分辨率设置",
            "配色主题"
        ],
        
        # 其他技术要求
        "权限与安全": [
            "用户身份鉴权",
            "权限细粒度管理",
            "数据脱敏",
            "数据加密存储",
            "审计日志"
        ],
        "性能与扩展": [
            "大样本处理（500+）",
            "并发分析支持",
            "云端扩展",
            "多平台支持"
        ],
        "国际化与文档": [
            "多语言配置",
            "接口文档",
            "数据字典",
            "示例数据集"
        ],
        "Web扩展（可选）": [
            "Web端录入界面",
            "Web端结果查看",
            "FastAPI后端",
            "Vue3前端"
        ]
    }
    
    print("\n=== PRD需求与实现情况对比 ===")
    
    # 分析每个需求类别的实现情况
    for category, requirements in prd_requirements.items():
        print(f"\n【{category}】")
        for req in requirements:
            # 简单的关键词匹配来判断是否实现
            implemented = False
            matching_features = []
            
            # 检查是否有相关的测试覆盖
            for feature in implemented_features:
                if any(keyword in feature.lower() for keyword in req.lower().split()):
                    implemented = True
                    matching_features.append(feature)
            
            status = "✅" if implemented else "❌"
            print(f"  {status} {req}")
            if matching_features:
                for match in matching_features[:2]:  # 只显示前2个匹配
                    print(f"      → {match}")

if __name__ == '__main__':
    analyze_missing_features()