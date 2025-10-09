# 家谱系统自动化测试方案

## 概述

本测试方案基于 `evaluation/metric.json` 中定义的55个功能测试点，生成了完整的自动化测试套件。

## 文件结构

```
evaluation/
├── metric.json                    # 功能评估指标文件（已移除前置校验）
├── detailed_test_plan.json        # 详细测试计划（55个测试点）
├── run_tests.py                   # 主测试运行脚本
├── README.md                      # 本说明文件
├── test_inputs/                   # 测试输入文件目录
│   ├── test_startup.in            # 程序启动测试输入
│   ├── test_002.in                # 姓名必填字段校验测试
│   ├── test_003.in                # 性别必填字段校验测试
│   └── ...                        # 其他测试输入文件
├── test_data/                     # 测试数据文件
│   └── existing_data.csv          # 用于增量存储测试的现有数据
├── expected_outputs/              # 期望输出文件（用于文件比较测试）
│   ├── expected_001.csv           # 期望的CSV输出
│   └── ...                        # 其他期望输出文件
└── tests/                         # 单元测试文件目录
    ├── test_tree_structure.py     # 树形结构相关测试
    ├── test_data_processing.py    # 数据处理相关测试
    ├── test_file_format.py        # 文件格式相关测试
    └── ...                        # 其他单元测试文件
```

## 测试类型

### 1. Shell Interaction Tests (shell_interaction)
- 用于测试需要模拟用户与命令行进行真实交互的功能
- 使用 `main_automated.py` 和 `.in` 输入文件进行自动化交互
- 主要测试：必填字段校验、格式校验、查询功能等

### 2. Unit Tests (unit_test)
- 用于直接调用源代码中的特定函数或类进行验证
- 使用 pytest 框架执行
- 主要测试：类定义、数据处理、结构一致性等

### 3. File Comparison Tests (file_comparison)
- 用于验证程序是否生成了正确的输出文件
- 比较生成文件与期望文件的内容
- 主要测试：CSV文件创建、数据存储、文件格式等

## 使用方法

### 运行所有测试
```bash
python evaluation/run_tests.py
```

### 运行单个单元测试
```bash
pytest evaluation/tests/test_tree_structure.py
```

### 运行特定的shell交互测试
```bash
python src/main_automated.py evaluation/test_inputs/test_002.in
```

## 测试输入文件格式

测试输入文件（.in文件）包含模拟用户输入的命令序列，例如：

```
add
张三
北京
19900101
0
175.5
本科
软件工程师
高级工程师

0
1
男
```

## 测试报告

运行完成后，测试结果将保存在：
- `evaluation/test_report.json` - 详细的JSON格式测试报告
- 控制台输出 - 实时测试进度和汇总结果

## 注意事项

1. 确保Python环境已安装pandas等依赖库
2. 测试前会自动清理data.csv等数据文件
3. 某些测试可能需要特定的数据准备，请确保相关测试数据文件存在
4. 如果测试失败，请检查错误信息并确认程序功能是否正确实现

## 扩展测试

如需添加新的测试点：
1. 在 `metric.json` 中添加新的测试指标
2. 在 `detailed_test_plan.json` 中添加对应的测试计划
3. 创建相应的测试输入文件和期望输出文件
4. 如果是单元测试，在 `tests/` 目录下创建对应的测试文件