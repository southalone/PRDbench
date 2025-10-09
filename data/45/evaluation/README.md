# Chord DHT 仿真系统测试框架

## 概述

本测试框架为Chord DHT仿真系统提供了完整的自动化测试方案，包括交互式测试、单元测试和文件比较测试。

## 目录结构

```
evaluation/
├── detailed_test_plan.json          # 详细测试计划
├── additional_unit_tests.json       # 额外的单元测试定义
├── inputs/                          # 测试输入文件
│   ├── basic_startup.in
│   ├── m_parameter_config.in
│   ├── nodes_config.in
│   ├── boundary_validation.in
│   ├── network_initialization.in
│   ├── menu_display.in
│   ├── node_add_success.in
│   ├── node_add_duplicate.in
│   ├── data_insert.in
│   ├── data_search_found.in
│   ├── data_search_notfound.in
│   ├── network_info.in
│   ├── node_delete_success.in
│   ├── node_delete_notfound.in
│   ├── network_visualization.in
│   ├── time_statistics.in
│   ├── menu_validation.in
│   ├── node_id_validation.in
│   ├── batch_data_generation.in
│   ├── menu_loop.in
│   └── graceful_exit.in
├── expected_outputs/                # 期望输出文件
│   └── expected_graph.dot
├── tests/                          # 单元测试文件
│   ├── __init__.py
│   ├── test_chord_basic.py
│   └── test_data_operations.py
└── README.md                       # 本文件
```

## 测试类型

### 1. Shell Interaction 测试
这类测试模拟用户与命令行程序的真实交互，验证：
- 程序启动和初始化
- 菜单系统
- 用户输入处理
- 错误处理
- 操作反馈

**执行方式：**
```bash
python src/Main.py < evaluation/inputs/test_case.in
```

### 2. Unit Test 测试
这类测试直接调用源代码中的类和方法，验证：
- 节点初始化
- 网络构建
- 哈希函数
- 数据操作

**执行方式：**
```bash
pytest evaluation/tests/test_chord_basic.py -v
pytest evaluation/tests/test_data_operations.py -v
```

### 3. File Comparison 测试
这类测试验证程序生成的文件是否符合预期：
- 网络拓扑DOT文件
- PNG图像文件（如果支持）

**执行方式：**
```bash
python src/Main.py < evaluation/inputs/network_visualization.in
diff graph.dot evaluation/expected_outputs/expected_graph.dot
```

## 输入文件格式

输入文件包含模拟用户输入的完整序列，每行代表一次输入：
- 数字：菜单选择或参数输入
- 文本：数据字符串或节点ID
- 空行：表示Enter键

例如 `node_add_success.in`：
```
4        # m参数
6        # 节点数量
0        # 数据数量
1        # 选择菜单项1（添加节点）
20       # 新节点ID
7        # 选择菜单项7（退出）
```

## 运行所有测试

### 运行单元测试
```bash
pytest evaluation/tests/ -v
```

### 运行交互式测试（示例）
```bash
# 测试程序基础启动
python src/Main.py < evaluation/inputs/basic_startup.in

# 测试节点添加功能
python src/Main.py < evaluation/inputs/node_add_success.in

# 测试数据插入功能
python src/Main.py < evaluation/inputs/data_insert.in
```

### 运行文件比较测试
```bash
# 生成网络拓扑文件
python src/Main.py < evaluation/inputs/network_visualization.in

# 比较生成的文件与期望文件
if [ -f "graph.dot" ]; then
    echo "DOT文件生成成功"
    # 可以进一步比较内容
    # diff graph.dot evaluation/expected_outputs/expected_graph.dot
else
    echo "DOT文件生成失败"
fi
```

## 测试覆盖范围

本测试框架覆盖了以下功能点：

### 基础功能
- [x] 程序启动和欢迎界面
- [x] 网络参数配置（m、节点数、数据数）
- [x] 边界条件验证
- [x] 网络初始化过程

### 核心功能
- [x] 动态节点管理（添加/删除）
- [x] 数据插入和查找
- [x] 网络状态信息显示
- [x] 网络拓扑可视化

### 交互功能
- [x] 菜单系统完整性
- [x] 用户输入验证
- [x] 错误处理
- [x] 菜单循环执行
- [x] 优雅退出

### 性能功能
- [x] 操作时间统计
- [x] 批量数据生成

## 预期结果

### 成功场景
- 程序正常启动并显示欢迎信息
- 参数配置成功接受有效输入
- 网络创建成功并显示统计信息
- 节点和数据操作成功执行
- 生成正确的可视化文件

### 错误处理
- 无效参数输入得到适当错误提示
- 重复操作得到正确处理
- 程序在错误输入时不崩溃

## 注意事项

1. **依赖环境**：确保安装了所需的Python包（参见src/requirements.txt）
2. **文件路径**：所有测试都假设从项目根目录执行
3. **Graphviz**：网络可视化功能需要系统安装Graphviz
4. **并发测试**：某些测试可能需要足够的系统资源

## 故障排除

### 常见问题
1. **ModuleNotFoundError**：检查Python路径和依赖安装
2. **文件不存在**：确保从正确的目录执行测试
3. **权限错误**：检查文件和目录权限
4. **图形生成失败**：检查Graphviz安装和配置

### 调试建议
1. 单独运行失败的测试用例
2. 检查程序的标准输出和错误输出
3. 验证输入文件格式是否正确
4. 确认测试环境与开发环境一致
