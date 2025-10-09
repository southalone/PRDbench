# 知识图谱补全系统测试方案

本文档描述了为知识图谱补全系统（TransE算法实现）创建的完整测试方案。

## 文件结构

```
evaluation/
├── detailed_test_plan.json          # 详细测试计划
├── metric.json                      # 原始评估指标
├── README.md                        # 本说明文档
├── expected_entity2id.txt           # 期望的实体映射文件
├── expected_relation2id.txt         # 期望的关系映射文件
├── expected_entity_vec.txt          # 期望的实体向量文件
├── expected_relation_vec.txt        # 期望的关系向量文件
├── expected_loss_curve.png          # 期望的损失曲线图
├── expected_report_meanrank.json    # 期望的MeanRank报告
├── expected_report_hit10.json       # 期望的Hit@10报告
├── expected_report_format.json      # 期望的JSON格式报告
├── expected_report_complete.json    # 期望的完整报告
├── invalid_data/                    # 无效数据测试文件
│   ├── entity2id.txt
│   ├── relation2id.txt
│   └── train.txt
└── tests/                           # 单元测试
    ├── __init__.py
    └── test_vector_initialization.py
```

## 测试计划概述

测试计划包含17个测试点，分为三种类型：

### 1. Shell Interaction 测试 (12个)
- 1.1 程序启动与帮助信息
- 2.1.2 数据完整性验证与异常处理
- 3.1 TransE模型训练启动
- 3.2 训练参数配置
- 3.4 损失值计算与监控（20个epoch，验证收敛趋势）
- 4.2 评估指标计算 - MeanRank
- 4.3 评估指标计算 - Hit@10
- 5.1a 实体向量文件输出
- 5.1b 关系向量文件输出
- 5.3a 评估报告生成 - 文件格式
- 5.3b 评估报告内容 - 包含关键指标
- 6.1 错误处理与提示

### 2. File Comparison 测试 (4个)
- 2.1.1a 数据加载 - 实体映射文件生成
- 2.1.1b 数据加载 - 关系映射文件生成
- 4.1 链接预测功能（使用黄金标准数据集）
- 5.2 损失曲线可视化

### 3. Unit Test 测试 (1个)
- 3.3 向量初始化验证

## 主要组件

### 1. 主程序 (src/main.py)
创建了统一的命令行接口，支持：
- `preprocess`: 数据预处理
- `train`: 模型训练（所有输出文件保存到指定目录）
- `evaluate`: 模型评估

### 2. 测试数据
- **有效数据**: 使用src/data/中的FB15K-237数据集
- **黄金标准数据**: evaluation/golden_data/中的小型确定性数据集，确保评估能产生有效结果
- **无效数据**: evaluation/invalid_data/中包含非法实体的测试数据

### 3. 期望输出文件
为每个file_comparison类型的测试创建了对应的期望输出文件，用于验证程序生成的文件格式和内容。期望文件与实际数据文件保持一致，确保测试的准确性。

### 4. 单元测试
创建了pytest兼容的单元测试，用于验证向量初始化的正确性。

## 使用方法

### 运行Shell Interaction测试
```bash
python src/main.py --help
python src/main.py train --input ./src/data --output ./test_output --epochs 2
python src/main.py evaluate --input ./src/data --model ./test_output
```

### 运行File Comparison测试
执行相应命令后，比较生成的文件与期望文件：
```bash
python src/main.py preprocess --input ./src/data --output ./test_output
# 比较 test_output/entity2id.txt 与 evaluation/expected_entity2id.txt
```

### 运行Unit Test
```bash
pytest evaluation/tests/test_vector_initialization.py::test_vector_dimensions
```

## 测试覆盖范围

本测试方案覆盖了PRD中的所有核心功能：
1. ✅ 数据加载与预处理
2. ✅ TransE模型训练
3. ✅ 链接预测与评估
4. ✅ 结果输出
5. ✅ 错误处理

每个功能都有对应的测试用例，确保系统的完整性和可靠性。
