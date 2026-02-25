# MinNE网络仿真系统测试方案

本目录包含了完整的测试方案，用于评估MinNE分层网络仿真与协议栈实现平台的功能完整性。

## 文件结构

### 核心文件
- `metric.json` - 功能评估指标定义
- `detailed_test_plan.json` - 详细的测试计划，包含30个测试点
- `README.md` - 本说明文件

### 输入文件
- `port_query.in` - 端口查询测试输入
- `text_transmission_test.in` - 文本传输测试输入
- `utf8_test_text.txt` - UTF-8编码测试文本
- `image_transmission_test.in` - 图片传输测试输入
- `image_save_test.in` - 图片保存测试输入
- `image_naming_test.in` - 图片命名测试输入
- `console_test.in` - 控制台功能测试输入
- `large_file_test.in` - 大文件传输测试输入
- `test_image.png` - 测试用图片文件
- `large_test_file.bin` - 大文件测试数据
- `crc_test_data.txt` - CRC校验测试数据

### 自动化测试脚本 (tests/)
- `test_frame_structure.py` - 帧结构字段完整性测试
- `test_frame_classes.py` - FrameBuilder和FrameParser类测试
- `test_crc16.py` - CRC-16算法测试
- `test_switch_table.py` - 交换机地址表测试
- `test_switch_learning.py` - 交换机地址学习测试
- `test_switch_lifetime.py` - 交换机生存时间管理测试
- `test_router_table.py` - 路由表结构测试
- `test_dijkstra.py` - Dijkstra算法测试
- `test_buffer_config.py` - 缓冲区配置测试
- `test_flow_control.py` - 流量控制机制测试
- `test_bit_stuffing.py` - 比特填充算法测试
- `test_arq.py` - 停等ARQ协议测试
- `test_switch_forwarding.py` - 交换机转发功能测试

## 测试类型

### 1. Shell交互测试 (shell_interaction)
用于测试需要与命令行程序进行真实交互的功能，如：
- 程序启动和基础运行
- 设备类型识别
- 文本和图片传输
- 交互式控制台
- 分阶段配置支持

### 2. 单元测试 (unit_test)
用于测试特定代码模块和类的实现，如：
- 帧结构和编解码类
- CRC-16校验算法
- 交换机和路由器功能模块
- 网络协议实现

### 3. 文件比较测试 (file_comparison)
用于验证程序生成的输出文件，如：
- 图片文件自动保存
- 文件命名格式验证

## 使用方法

### 运行单元测试
```bash
# 运行所有单元测试
pytest evaluation/tests/

# 运行特定测试文件
pytest evaluation/tests/test_frame_structure.py

# 运行特定测试函数
pytest evaluation/tests/test_crc16.py::test_crc16_parameters
```

### 运行Shell交互测试
```bash
# 基础启动测试
python code/main.py 2

# 带输入文件的测试
python code/main.py 2 < evaluation/port_query.in
```

### 批处理测试
```bash
# Windows批处理文件测试
bin\OneTouchToGo-stage2.bat
```

## 评分标准

每个测试点都有对应的评分标准：
- **2分**: 功能完全实现且正确工作
- **1分**: 功能基本实现但存在轻微问题
- **0分**: 功能未实现或严重错误

总共30个测试点，权重从1到5不等，总权重为75分。

## 注意事项

1. 运行测试前请确保系统环境配置正确
2. 某些测试需要特定的配置文件存在
3. 网络相关测试可能需要多个终端窗口
4. 建议按照测试计划中的顺序执行测试
5. 如果某个测试失败，请检查相关的依赖和前置条件