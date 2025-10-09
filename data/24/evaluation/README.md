# 物流中心选址系统测试方案

## 概述
本测试方案为物流中心选址系统提供了完整的自动化测试框架，包含功能测试、单元测试和文件比较测试。

## 文件结构
```
evaluation/
├── metric.json                    # 评分标准定义
├── detailed_test_plan.json       # 详细测试计划
├── expected_cluster_points.xlsx  # 期望的聚类结果文件（黄金标准）
├── pytest.ini                    # pytest配置文件
├── tests/                         # 单元测试目录
│   ├── __init__.py
│   ├── test_centroid_coordinates.py    # 重心坐标测试
│   ├── test_cluster_coordinates.py     # 聚类坐标测试
│   ├── test_code_analysis.py           # 代码分析测试
│   └── test_consistency.py             # 一致性测试
└── README.md                      # 本文件
```

## 测试类型说明

### 1. Shell Interaction 测试
直接执行Python脚本，验证控制台输出和图表显示：
- 环境依赖检查
- Excel文件读取
- 数据验证
- 算法执行和可视化
- 系统稳定性

### 2. Unit Test 测试
使用pytest框架进行单元测试：
- 重心坐标合理性验证
- 聚类中心坐标验证
- 代码实现检查
- 结果一致性测试

### 3. File Comparison 测试
验证程序生成的文件与期望文件的一致性：
- Excel文件生成验证

## 运行测试

### 前置条件
1. 确保在AHAU-logistics-GM/src目录下有以下文件：
   - mdl4.xlsx
   - 聚类之后.xlsx
   - HarmonyOS_Sans_SC_Black.ttf
   - 单重心法.py
   - 聚类算法.py
   - 轮廓系数zh.py

2. 安装依赖包：
   ```bash
   pip install pandas numpy scikit-learn matplotlib openpyxl pytest
   ```

### 运行所有单元测试
```bash
cd evaluation
pytest tests/ -v
```

### 运行特定测试
```bash
# 测试重心坐标
pytest tests/test_centroid_coordinates.py::test_centroid_in_anhui_range -v

# 测试聚类坐标
pytest tests/test_cluster_coordinates.py::test_cluster_centers_in_anhui_range -v

# 测试代码分析
pytest tests/test_code_analysis.py::test_standard_scaler_usage -v
pytest tests/test_code_analysis.py::test_weight_normalization -v

# 测试一致性
pytest tests/test_consistency.py::test_centroid_consistency -v
```

### 手动执行Shell Interaction测试
```bash
cd src

# 测试环境依赖
python -c "import pandas, numpy, sklearn, matplotlib, openpyxl; print('所有依赖导入成功')"

# 测试Excel文件读取
python -c "import pandas as pd; data1=pd.read_excel('mdl4.xlsx'); data2=pd.read_excel('聚类之后.xlsx'); print(f'mdl4数据行数: {len(data1)}, 列数: {len(data1.columns)}'); print(f'聚类数据行数: {len(data2)}, 列数: {len(data2.columns)}')"

# 运行算法脚本
python 轮廓系数zh.py
python 聚类算法.py
python 单重心法.py
```

## 评分标准
每个测试点都有对应的评分标准（0-2分）和权重（1-5分）。详细评分规则请参考 `metric.json` 文件。

## 注意事项
1. 运行测试前确保所有必需的数据文件都存在
2. 图表显示测试需要支持matplotlib的GUI环境
3. 中文字体测试需要正确的字体文件支持
4. 某些测试可能需要关闭图表窗口后才能继续执行