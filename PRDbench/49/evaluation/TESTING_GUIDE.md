# IoT环境数据采集系统 - 测试指南

## 概述

本指南提供了完整的测试方案，用于评估IoT环境数据采集与智能预测系统的实现质量。测试方案包括人工评测标准、自动化测试接口和详细的测试计划。

## 文件结构

```
evaluation/
├── metric.json                      # 人工评测标准（19个评分点）
├── detailed_test_plan.json          # 详细测试计划（结构化测试用例）
├── agent_test_interface.py          # Agent自动化测试接口
├── run_tests.py                     # 综合测试执行脚本
├── README.md                        # 评测说明文档
├── EVALUATION_SUMMARY.md            # 评测总结报告
├── TESTING_GUIDE.md                 # 本测试指南
├── pytest.ini                      # Pytest配置文件
├── test_environmental_data.csv      # 测试用环境数据
├── test_data_with_anomalies.csv     # 包含异常的测试数据
├── setup_inputs.in                  # 配置向导输入文件
├── user_interaction.in              # 用户交互输入文件
├── expected_data_format.csv         # 期望的数据格式文件
└── tests/                           # 单元测试目录
    ├── __init__.py                  # 测试包初始化
    ├── test_data_quality.py         # 数据质量控制测试
    ├── test_error_handling.py       # 错误处理测试
    ├── test_logging.py              # 日志功能测试
    └── test_functionality_completeness.py  # 功能完整性测试
```

## 测试类型说明

### 1. Shell Interaction Tests (shell_interaction)
用于测试需要模拟用户与命令行进行真实交互的功能。

**特点:**
- 执行完整的CLI命令
- 可以包含标准输入模拟
- 验证命令输出和行为

**示例:**
```json
{
  "type": "shell_interaction",
  "testcases": [
    {
      "test_command": "cd src && python main.py mqtt publish --random",
      "test_input": null
    }
  ]
}
```

### 2. Unit Tests (unit_test)
用于验证可以通过直接调用源代码中的特定函数或类来测试的功能点。

**特点:**
- 直接测试代码逻辑
- 可以测试边界条件
- 提供详细的断言验证

**示例:**
```json
{
  "type": "unit_test", 
  "testcases": [
    {
      "test_command": "python tests/test_data_quality.py",
      "test_input": null
    }
  ]
}
```

### 3. File Comparison Tests (file_comparison)
用于验证程序是否生成了正确的输出文件。

**特点:**
- 验证文件生成
- 比较输出与期望结果
- 检查文件格式和内容

**示例:**
```json
{
  "type": "file_comparison",
  "expected_output_files": ["evaluation/expected_data_format.csv"]
}
```

## 使用方法

### 1. 快速评测

```bash
# 使用综合测试脚本
cd evaluation
python run_tests.py
```

### 2. 使用Agent自动化测试接口

```bash
# 运行Agent测试接口
cd evaluation
python agent_test_interface.py
```

### 3. 单独运行单元测试

```bash
# 测试功能完整性
python tests/test_functionality_completeness.py

# 测试错误处理
python tests/test_error_handling.py

# 测试日志功能
python tests/test_logging.py

# 测试数据质量
python tests/test_data_quality.py
```

### 4. 手动测试特定功能

```bash
# 测试MQTT功能
cd ../src
python main.py mqtt publish --random
python main.py mqtt subscribe --duration 10

# 测试数据管理
python main.py data analyze
python main.py data clean

# 测试机器学习
python main.py ml train --data-file samples/environmental_sample.csv --epochs 10
python main.py ml predict --temperature 25.0 --humidity 60.0 --pressure 1013.25

# 测试系统监控
python main.py system status
python main.py system monitor --duration 15

# 测试Web界面
python test_web.py  # 然后访问 http://localhost:8080
```

## 评分标准

### 评分点权重分布
- **权重5** (关键功能): 系统启动、ML训练、功能完整性
- **权重4** (重要功能): MQTT通信、数据分析、系统监控、Web界面、用户体验
- **权重3** (辅助功能): 数据清洗、数据合并、配置向导、数据格式验证、错误处理
- **权重2** (支持功能): 日志记录

### 评分规则
- **2分**: 功能完全可用，符合PRD要求
- **1分**: 功能部分可用，有小问题但不影响基本使用
- **0分**: 功能不可用或严重错误

### 总分计算
```
最终得分 = Σ(各评分点得分 × 对应权重) / Σ(所有权重 × 2) × 100
```

## 测试环境要求

### 系统要求
- Python 3.9+
- 操作系统: Windows/Linux/macOS
- 内存: ≥4GB
- 存储: ≥1GB可用空间

### 依赖包要求
```bash
pip install -r requirements.txt
```

主要依赖:
- pyyaml, pandas, numpy, scikit-learn
- torch, matplotlib, seaborn
- psutil, click, rich
- paho-mqtt, flask, tqdm

## 测试执行流程

### 1. 环境准备
```bash
# 检查Python版本
python --version

# 安装依赖
pip install -r requirements.txt

# 验证基础功能
python run.py test
```

### 2. 执行评测
```bash
# 方式1: 使用综合测试脚本
cd evaluation
python run_tests.py

# 方式2: 使用Agent接口
python agent_test_interface.py

# 方式3: 手动逐项测试
# 参考 metric.json 中的验证方法
```

### 3. 查看结果
```bash
# 查看测试报告
cat test_execution_results.json

# 查看评测总结
cat EVALUATION_SUMMARY.md
```

## 常见问题与解决方案

### 1. MQTT连接失败
**现象**: MQTT发布/订阅功能报连接错误
**原因**: 未配置阿里云IoT平台凭据
**解决**: 这是正常现象，不影响功能评分。系统会显示连接尝试和错误处理。

### 2. 模型训练失败
**现象**: ML训练命令执行失败
**原因**: 可能是数据文件路径或格式问题
**解决**: 检查samples目录下是否有environmental_sample.csv文件

### 3. Web界面无法访问
**现象**: Web服务启动后无法访问
**解决**: 
```bash
cd src
python test_web.py  # 使用测试版Web界面
```

### 4. 数据合并失败
**现象**: data merge命令失败
**原因**: 缺少分离的传感器数据文件
**解决**: 先运行数据发布命令生成测试数据

### 5. 单元测试导入错误
**现象**: 测试文件无法导入模块
**解决**: 确保从evaluation目录运行测试，Python路径会自动设置

## 测试结果解读

### 成功率等级
- **90-100%**: A级 - 优秀实现
- **80-89%**: B级 - 良好实现
- **70-79%**: C级 - 中等实现
- **60-69%**: D级 - 及格实现
- **<60%**: F级 - 不及格

### 关键指标
1. **系统启动成功率**: 必须100%
2. **核心功能可用性**: 应≥80%
3. **用户体验质量**: 应≥75%
4. **错误处理完善度**: 应≥70%

## 测试最佳实践

### 1. 测试顺序
1. 基础功能测试（系统启动、帮助信息）
2. 核心业务功能测试（MQTT、数据管理、ML）
3. 系统支持功能测试（监控、日志、配置）
4. 用户体验测试（界面友好性、错误处理）

### 2. 测试数据准备
- 使用提供的测试数据文件
- 确保数据格式符合PRD规范
- 包含正常数据和异常数据

### 3. 结果验证
- 检查命令执行状态
- 验证输出内容完整性
- 确认日志记录正确性
- 测试错误处理机制

### 4. 报告生成
- 记录详细的测试过程
- 统计成功/失败率
- 提供改进建议
- 生成评分报告

## 扩展测试

### 添加新测试用例
1. 在`metric.json`中添加新的评分点
2. 在`detailed_test_plan.json`中添加对应的测试用例
3. 如需要，创建相应的单元测试文件
4. 更新测试文档

### 自定义测试脚本
可以基于`agent_test_interface.py`创建自定义的测试脚本，适应特定的测试需求。

## 联系与支持

如有测试相关问题，请参考：
1. 项目主文档: `../README.md`
2. 详细使用文档: `../src/docs/README.md`
3. 产品需求文档: `../src/docs/PRD.md`

测试方案确保了对系统实现质量的客观、全面、可复现的评估。