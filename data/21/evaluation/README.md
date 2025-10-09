# 程青岛一区抽奖系统 - 测试方案说明

## 测试方案概述

本测试方案为程青岛一区抽奖系统提供完整的质量保证验证，包含24个测试点，覆盖所有PRD功能需求。

## 测试方案结构

```
evaluation/
├── detailed_test_plan.json    # 详细测试计划（24个测试点）
├── metric.json               # 功能评估指标
├── run_tests.py             # 自动化测试运行脚本
├── README.md                # 本文件
├── inputs/                  # 测试输入文件目录
│   ├── startup_test.in      # 程序启动测试输入
│   ├── csv_import_test.in   # CSV导入测试输入
│   ├── full_workflow_test.in # 完整流程测试输入
│   └── ...                  # 其他测试输入文件
├── test_data/              # 测试数据文件目录
│   ├── employees_5.csv     # 5人员工数据
│   ├── employees_10.csv    # 10人员工数据
│   ├── employees_missing_field.csv  # 缺少字段测试数据
│   └── ...                 # 其他测试数据文件
├── tests/                  # 单元测试目录
│   ├── test_weighted_sampling.py   # 加权抽样测试
│   ├── test_no_duplicate.py        # 重复中奖测试
│   ├── test_fairness_report.py     # 公平性报告测试
│   └── test_file_operations.py     # 文件操作测试
└── expected_outputs/       # 期望输出文件目录
    └── sample_result.txt   # 示例结果文件
```

## 测试类型说明

### 1. Shell交互测试 (shell_interaction)
**用途**：测试需要用户与命令行进行真实交互的功能
**数量**：18个测试点
**执行方式**：手动执行，使用输入文件模拟用户交互

**示例**：
```bash
python src/main.py < evaluation/inputs/csv_import_test.in
```

### 2. 单元测试 (unit_test)
**用途**：直接调用源代码函数进行验证
**数量**：6个测试点
**执行方式**：使用pytest自动执行

**示例**：
```bash
python -m pytest evaluation/tests/test_weighted_sampling.py::test_score_weighted_lottery -v
```

### 3. 文件比较测试 (file_comparison)
**用途**：验证程序生成的输出文件
**数量**：2个测试点
**执行方式**：程序执行后比较生成文件与期望文件

## 测试数据说明

### 标准测试数据
- **employees_5.csv**: 5名员工，用于基础功能测试
- **employees_10.csv**: 10名员工，用于统计功能测试
- **employees_missing_field.csv**: 缺少工号字段，用于验证错误处理
- **employees_invalid_format.csv**: 包含格式错误，用于验证数据验证

### 特殊测试数据
- **employees_score_extreme.csv**: 极端积分差异，用于加权测试
- **employees_multi_dept.csv**: 多部门分布，用于卡方检验
- **employees_large.csv**: 大量员工，用于性能测试

## 运行测试

### 自动化测试
```bash
# 运行所有自动化测试
python evaluation/run_tests.py

# 运行特定单元测试
python -m pytest evaluation/tests/test_weighted_sampling.py -v
python -m pytest evaluation/tests/test_fairness_report.py -v
```

### 手动交互测试
```bash
# 程序启动测试
python src/main.py < evaluation/inputs/startup_test.in

# CSV导入测试
python src/main.py < evaluation/inputs/csv_import_test.in

# 完整工作流程测试
python src/main.py < evaluation/inputs/full_workflow_test.in
```

## 测试验证标准

### 功能完整性验证
- ✅ 程序能正常启动并显示主菜单
- ✅ 支持CSV和TXT格式员工名单导入
- ✅ 完善的数据验证和错误处理
- ✅ 统计信息计算准确
- ✅ 三种权重规则正确实现
- ✅ 重复中奖规则正确执行
- ✅ A-Res算法加权抽样有效
- ✅ 彩色结果展示正确
- ✅ 统计学公平性报告完整

### 用户体验验证
- ✅ 交互界面清晰直观
- ✅ 错误提示友好准确
- ✅ 操作流程连贯顺畅
- ✅ 进度提示及时准确

### 数据准确性验证
- ✅ 数学计算结果正确
- ✅ 统计检验实现准确
- ✅ 文件格式规范标准
- ✅ 编码处理正确无误

## 测试覆盖率

| 功能模块 | 测试点数 | 覆盖率 |
|---------|---------|--------|
| 程序启动 | 1 | 100% |
| 名单管理 | 8 | 100% |
| 抽奖配置 | 8 | 100% |
| 抽奖执行 | 5 | 100% |
| 结果展示 | 9 | 100% |
| 用户体验 | 2 | 100% |
| **总计** | **24** | **100%** |

## 测试执行建议

### 1. 环境准备
```bash
# 安装依赖
pip install -r src/requirements.txt

# 安装测试依赖
pip install pytest
```

### 2. 测试顺序
1. 先运行自动化测试验证核心逻辑
2. 再进行手动交互测试验证用户体验
3. 最后进行完整流程测试

### 3. 问题排查
- 如果单元测试失败，检查依赖包安装
- 如果交互测试异常，检查输入文件格式
- 如果文件测试失败，检查文件权限

## 质量标准

### 通过标准
- 所有单元测试通过率 ≥ 95%
- 所有交互测试功能可达
- 所有文件比较测试内容匹配
- 无程序崩溃或异常退出

### 性能标准
- 程序启动时间 < 3秒
- 名单导入时间 < 5秒（100人以内）
- 抽奖执行时间 < 10秒（100人10奖项）
- 报告生成时间 < 2秒

---

**测试方案版本**: v1.0  
**适用系统版本**: 程青岛一区抽奖系统 v1.0  
**更新日期**: 2025年8月20日