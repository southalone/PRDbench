# 3-MSA多序列比对算法优化系统 - 测试方案

## 概述

本测试方案为3-MSA多序列比对算法优化系统提供了完整的自动化测试框架，包含29个测试指标，覆盖了系统的所有主要功能。

## 文件结构

```
evaluation/
├── detailed_test_plan.json          # 详细测试计划
├── metric.json                      # 功能指标定义
├── run_tests.py                     # 自动化测试执行脚本
├── README.md                        # 本文档
├── input_files/                     # 测试输入文件
│   ├── main_menu_test.in
│   ├── invalid_input_test.in
│   ├── file_path_test.in
│   ├── valid_sequence.txt
│   ├── invalid_sequence.txt
│   ├── test_sequences.txt
│   └── ...
├── expected_output/                 # 期望输出文件
│   ├── saved_result.txt
│   ├── config_complete_result.txt
│   └── data_complete_result.txt
└── tests/                          # 单元测试文件
    ├── test_dp_algorithm.py
    ├── test_astar_algorithm.py
    ├── test_ga_algorithm.py
    ├── test_ga_algorithm_fixed.py
    └── test_optimization.py
```

## 测试类型

### 1. Shell交互测试 (shell_interaction)
- **用途**: 测试用户与命令行程序的交互功能
- **数量**: 24个测试
- **示例**: 主菜单显示、输入验证、算法选择等

### 2. 单元测试 (unit_test)
- **用途**: 测试核心算法和优化技术的实现
- **数量**: 3个测试
- **示例**: 动态规划算法、A*搜索算法、遗传算法

### 3. 文件对比测试 (file_comparison)
- **用途**: 验证程序生成的输出文件是否正确
- **数量**: 2个测试
- **示例**: 结果保存功能、配置信息完整性

## 快速开始

### 1. 环境准备

确保已安装必要的依赖：
```bash
pip install pytest
```

### 2. 运行所有测试

```bash
# 在项目根目录下执行
python evaluation/run_tests.py
```

### 3. 运行特定类型的测试

```bash
# 运行单元测试
pytest evaluation/tests/ -v

# 运行特定的单元测试
pytest evaluation/tests/test_dp_algorithm.py::test_dp_execution -v

# 运行修复版本的遗传算法测试
pytest evaluation/tests/test_ga_algorithm_fixed.py -v
```

### 4. 手动运行Shell交互测试

```bash
# 测试程序启动
python src/main.py < evaluation/input_files/main_menu_test.in

# 测试无效输入验证
python src/main.py < evaluation/input_files/invalid_input_test.in
```

## 测试结果解读

### 当前实现状态（基于eval_report.json）

- **通过测试**: 8/29 (27.6%)
- **失败测试**: 21/29 (72.4%)

#### ✅ 已通过的功能
1. 程序启动与主菜单显示
2. 菜单选项输入验证
3. 序列文件路径录入功能
4. 算法选择界面显示
5. 算法说明与使用样例
6. 动态规划算法实现
7. A*搜索算法实现

#### ❌ 需要改进的功能
1. **遗传算法**: 存在除零错误，需要修复
2. **进度提示**: 缺少动态进度显示
3. **性能对比**: 功能未完全实现
4. **性能分析**: 功能未完全实现
5. **结果保存**: 功能未实现

## 测试改进建议

### 1. 对于开发者

#### 立即修复项
- 修复遗传算法中的除零错误（参考`test_ga_algorithm_fixed.py`）
- 实现动态进度提示功能
- 完善历史记录复用功能

#### 中期目标
- 实现完整的性能对比功能
- 实现性能指标分析功能
- 添加结果保存和文本化表格展示

### 2. 对于测试计划

#### 已改进的方面
- 创建了更详细的测试输入文件
- 添加了期望输出文件用于文件对比测试
- 创建了修复版本的遗传算法测试
- 实现了自动化测试执行脚本

#### 进一步改进建议
- 为复杂功能提供更详细的测试数据
- 增加性能基准测试
- 添加更多边界情况和异常处理测试
- 改进中断测试的验证方法

## 自定义测试

### 添加新的测试用例

1. **Shell交互测试**:
   - 在`input_files/`目录下创建新的`.in`文件
   - 在`detailed_test_plan.json`中添加相应的测试配置

2. **单元测试**:
   - 在`tests/`目录下创建新的测试文件
   - 使用pytest框架编写测试函数

3. **文件对比测试**:
   - 在`expected_output/`目录下创建期望输出文件
   - 配置测试计划中的`expected_output_files`字段

### 修改测试参数

编辑`detailed_test_plan.json`文件，修改相应测试的配置：
- `test_command`: 测试执行命令
- `test_input`: 输入文件路径
- `expected_output`: 期望输出描述

## 故障排除

### 常见问题

1. **测试超时**
   - 检查算法实现是否存在无限循环
   - 调整`run_tests.py`中的超时设置

2. **文件路径错误**
   - 确保在项目根目录下执行测试
   - 检查输入文件和期望输出文件是否存在

3. **遗传算法除零错误**
   - 使用`test_ga_algorithm_fixed.py`中的测试用例
   - 参考修复建议改进算法实现

### 调试技巧

1. **查看详细输出**:
   ```bash
   python evaluation/run_tests.py 2>&1 | tee test_output.log
   ```

2. **单独运行失败的测试**:
   ```bash
   python src/main.py < evaluation/input_files/specific_test.in
   ```

3. **检查测试报告**:
   查看生成的`evaluation/test_execution_report.json`文件

## 贡献指南

欢迎提交改进建议和bug修复：

1. 遵循现有的测试文件命名规范
2. 为新功能添加相应的测试用例
3. 更新测试计划和文档
4. 确保所有测试都能正常执行

## 联系信息

如有问题或建议，请通过以下方式联系：
- 创建Issue描述问题
- 提交Pull Request进行改进
- 查看项目文档获取更多信息
