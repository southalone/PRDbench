# MatrixAnalysisFinal 测试系统

## 概述

这是为MatrixAnalysisFinal矩阵分解项目设计的完整自动化测试系统，用于验证五种矩阵分解算法的正确性、输出格式规范性和数值计算精度。

## 项目结构

```
evaluation/
├── detailed_test_plan.json    # 详细测试计划（JSON格式）
├── metric.json                # 功能评估指标
├── run_tests.py              # 测试运行脚本
├── README.md                 # 本文件
└── tests/                    # 测试文件目录
    ├── test_lu_correctness.py     # LU分解正确性测试
    ├── test_qr_correctness.py     # QR分解正确性测试
    ├── test_hr_correctness.py     # Householder反射正确性测试
    ├── test_gr_correctness.py     # Givens旋转正确性测试
    ├── test_urv_correctness.py    # URV分解正确性测试
    ├── test_output_format.py      # 输出格式规范性测试
    └── test_matrix_rank.py        # 矩阵秩计算测试
```

## 测试覆盖范围

### 1. 命令行接口测试
- **1.1** 无参数或无效参数时的帮助信息显示
- **1.2** 无效模型参数的错误处理
- **1.3** 无效文件路径的错误处理

### 2. 核心算法测试

#### 2.1 LU分解
- **2.1a** 计算结果正确性（P×L×U = A）
- **2.1b** 输出格式规范性（4位小数精度）
- **2.1c** 矩阵秩计算正确性

#### 2.2 QR分解（Gram-Schmidt）
- **2.2a** 计算结果正确性（Q×R = A，Q正交性）
- **2.2b** 输出格式规范性
- **2.2c** 矩阵秩计算正确性

#### 2.3 Householder反射分解
- **2.3a** 计算结果正确性（Q×R = A，Q正交性）
- **2.3b** 输出格式规范性
- **2.3c** 矩阵秩计算正确性

#### 2.4 Givens旋转分解
- **2.4a** 计算结果正确性（Q×R = A，Q正交性）
- **2.4b** 输出格式规范性
- **2.4c** 矩阵秩计算正确性

#### 2.5 URV分解
- **2.5a** 计算结果正确性（U×R×V^T = A，U、V正交性）
- **2.5b** 输出格式规范性
- **2.5c** 矩阵秩计算正确性

## 使用方法

### 运行所有测试
```bash
# 方法1：使用测试运行脚本
python evaluation/run_tests.py

# 方法2：使用pytest直接运行
pytest evaluation/tests/ -v
```

### 运行特定测试
```bash
# 运行LU分解正确性测试
pytest evaluation/tests/test_lu_correctness.py::test_lu_factorization_correctness -v

# 运行所有输出格式测试
pytest evaluation/tests/test_output_format.py -v

# 运行所有矩阵秩计算测试
pytest evaluation/tests/test_matrix_rank.py -v
```

### 命令行接口测试（手动）
```powershell
# 测试帮助信息
cd src; python main.py
cd src; python main.py --unknown-arg

# 测试无效模型参数
cd src; python main.py --model INVALIDMODEL --input data/LU.txt

# 测试无效文件路径
cd src; python main.py --model LU --input non_existent_file.txt
```

## 测试数据

测试使用src/data/目录中的标准测试矩阵：
- `LU.txt` - LU分解测试矩阵
- `GramSchmidt.txt` - QR分解测试矩阵
- `Household.txt` - Householder反射测试矩阵
- `Givens.txt` - Givens旋转测试矩阵
- `URV.txt` - URV分解测试矩阵

## 验证标准

### 数值精度
- 矩阵重构误差 < 1e-10
- 正交性验证误差 < 1e-10
- 矩阵秩计算与numpy.linalg.matrix_rank一致

### 输出格式
- 所有数值输出严格按照8.4f格式（8位宽度，4位小数）
- 矩阵元素对齐显示

### 矩阵性质验证
- LU分解：L为下三角，U为上三角，P为置换矩阵
- QR分解：Q为正交矩阵，R为上三角矩阵
- URV分解：U、V为正交矩阵

## 依赖要求

```bash
pip install pytest numpy
```

## 注意事项

1. 测试不会修改src/目录下的任何源代码
2. 所有测试都直接调用src/model/中的现有函数
3. 测试数据使用src/data/中的标准测试文件
4. 测试结果基于数值计算的浮点精度考虑