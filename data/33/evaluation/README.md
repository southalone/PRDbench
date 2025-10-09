# 联邦学习系统测试方案

本目录包含了联邦学习训练系统的完整测试方案，基于 `evaluation/metric.json` 中定义的功能评估指标。

## 文件结构

```
evaluation/
├── detailed_test_plan.json     # 详细测试计划（主要产物）
├── run_tests.py               # 测试运行脚本
├── README.md                  # 本说明文档
├── tests/                     # 单元测试目录
│   ├── __init__.py
│   ├── test_interrupt_handling.py
│   ├── test_error_handling.py
│   ├── test_log_content.py
│   ├── test_online_fl.py
│   └── test_file_naming.py
├── *.in                       # 输入文件（用于shell交互测试）
├── expected_*.log             # 期望输出文件（用于文件比较测试）
└── expected_result_file.txt   # 期望结果文件
```

## 测试类型说明

### 1. Shell Interaction 测试
- **用途**: 测试需要用户与命令行进行真实交互的功能
- **执行方式**: 通过 `python main.py` 启动程序，使用预定义的输入文件模拟用户交互
- **输入文件**: `*.in` 文件包含模拟的用户输入序列

### 2. Unit Test 测试
- **用途**: 测试可以通过直接调用源代码函数进行验证的功能
- **执行方式**: 使用 pytest 框架运行测试文件
- **测试文件**: `tests/test_*.py` 文件

### 3. File Comparison 测试
- **用途**: 验证程序是否生成了正确的输出文件
- **执行方式**: 运行程序生成文件，然后与期望文件进行比较
- **期望文件**: `expected_*.log` 和 `expected_*.txt` 文件

## 运行测试

### 方法1: 运行所有测试
```bash
cd evaluation
python run_tests.py
```

### 方法2: 运行单个测试类型
```bash
# 运行单元测试
pytest tests/

# 运行特定测试文件
pytest tests/test_interrupt_handling.py

# 运行特定测试函数
pytest tests/test_interrupt_handling.py::test_ctrl_c_interrupt
```

### 方法3: 手动运行shell交互测试
```bash
# 使用输入文件运行程序
python main.py < evaluation/main_menu_display.in
```

## 测试覆盖范围

本测试方案覆盖了 `metric.json` 中定义的所有33个评估指标：

### 1. 程序启动与菜单系统 (3个测试)
- 1.1 程序启动与主菜单显示
- 1.2a 菜单输入验证 - 无效数字处理
- 1.2b 菜单输入验证 - 非数字字符处理

### 2. 离线联邦学习 (15个测试)
- 2.1a-e 菜单可达性和参数配置
- 2.2a-b 训练模式选择
- 2.3a-b 进度显示
- 2.4 中断支持
- 2.5a-b 状态返回
- 2.6a-b 日志生成

### 3. 在线联邦学习 (5个测试)
- 3.1a-c 菜单可达性和配置
- 3.2a-b 连接状态显示

### 4. 参数扫描实验 (4个测试)
- 4.1a-b 菜单可达性和一键执行
- 4.2a-b 日志文件生成和命名
- 4.3 状态查询

### 5. 日志查看和模型评估 (4个测试)
- 5.1a-c 日志查看功能
- 5.2a-b 模型评估功能

### 6. 结果保存和展示 (2个测试)
- 6.1a-b 结果文件保存
- 6.2 文本化表格展示

### 7. 程序退出 (1个测试)
- 7.1 程序正常退出

## 输入文件说明

每个 `.in` 文件包含模拟用户输入的序列，用于测试特定功能：

- `main_menu_display.in`: 测试主菜单显示（输入6退出）
- `invalid_number_input.in`: 测试无效数字输入处理
- `offline_fl_*.in`: 测试离线联邦学习各种功能
- `online_fl_*.in`: 测试在线联邦学习功能
- `param_sweep_*.in`: 测试参数扫描实验功能
- 等等...

## 期望输出文件说明

- `expected_training_log.log`: 期望的训练日志格式
- `expected_result_*.log`: 期望的参数扫描实验日志
- `expected_result_file.txt`: 期望的结果保存文件格式

## 注意事项

1. **依赖要求**: 确保安装了 pytest 和其他必要的依赖
2. **主程序**: 测试依赖于项目根目录下的 `main.py` 文件
3. **超时设置**: 测试设置了合理的超时时间，避免长时间等待
4. **资源清理**: 测试会自动清理临时文件和进程
5. **并发问题**: 某些测试可能涉及网络端口，注意避免冲突

## 扩展测试

如需添加新的测试用例：

1. 在 `detailed_test_plan.json` 中添加新的测试定义
2. 创建相应的输入文件（如果是shell_interaction类型）
3. 创建相应的测试文件（如果是unit_test类型）
4. 创建期望输出文件（如果是file_comparison类型）
5. 运行 `python run_tests.py` 验证新测试

## 故障排除

如果测试失败，请检查：

1. 主程序 `main.py` 是否存在且可执行
2. 输入文件格式是否正确
3. 依赖包是否已安装
4. 文件权限是否正确
5. 端口是否被占用（对于网络相关测试）
