# 东野圭吾小说文本挖掘与语义分析工具 - 测试方案

## 概述

本测试方案包含了对东野圭吾小说文本挖掘与语义分析工具的完整测试计划，涵盖了所有功能点的验证。

## 文件结构

```
evaluation/
├── detailed_test_plan.json     # 详细测试计划
├── input_files/               # 测试输入文件
│   ├── *.in                  # 交互式测试输入
│   ├── *.txt                 # 测试文本文件
│   └── ...
├── expected_output/           # 期望输出文件
│   └── expected_results.txt   # 期望的分析结果
├── tests/                     # 单元测试文件
│   ├── test_entity_recognition.py
│   ├── test_output_format.py
│   ├── test_word2vec.py
│   └── test_relationship_reasoning.py
└── README.md                  # 本文件
```

## 测试类型说明

### 1. Shell Interaction 测试
用于测试需要模拟用户与命令行进行真实交互的功能。

**运行方式：**
```bash
cd src
python main.py < ../evaluation/input_files/menu_test.in
```

### 2. Unit Test 测试
用于验证特定函数或类的功能。

**运行方式：**
```bash
cd src
pytest ../evaluation/tests/test_entity_recognition.py::test_person_name_recognition
```

### 3. File Comparison 测试
用于验证程序生成的输出文件是否正确。

**运行方式：**
```bash
cd src
python main.py < ../evaluation/input_files/save_results_test.in
# 然后比较生成的文件与期望输出文件
```

## 主要测试点

### 程序启动与菜单 (0.1)
- 验证程序能正常启动并显示7个菜单选项

### 文件路径功能 (1.1-1.3)
- 菜单访问测试
- 文件路径有效性校验
- 文件编码自动检测（GBK/UTF-8）

### 实体识别提取 (2.1-2.7)
- 菜单访问
- 人物姓名识别 (nr)
- 地理名称识别 (ns)
- 时间表达识别 (t)
- 职业称谓识别 (nn)
- 进度显示
- 中断支持
- 状态反馈
- 历史记录保存与复用
- 输出格式验证

### 频次统计分析 (3.1-3.7)
- 菜单访问
- 频次统计与排行榜生成
- 实体类型筛选（人物/地点/时间/职业）
- 频次区间筛选
- 组合筛选条件
- 排序功能
- 分页展示

### 语义相似度分析 (4.1-4.5)
- 菜单访问
- 人物实体选择
- Word2Vec模型算法使用
- Word2Vec参数配置验证
- 相似度计算与排名
- 高相似度实体深度分析

### 关系推理分析 (5.1-5.5)
- 菜单访问
- 类比推理查询格式解析
- 向量空间类比推理算法 (D=C+B-A)
- 关系模式识别
- 关系模式统计分析

### 其他功能 (6.1-6.4)
- 输入有效性校验
- 表格化展示选项
- 结果保存功能
- 保存路径自定义

## 运行所有测试

### 运行单元测试
```bash
cd src
pytest ../evaluation/tests/ -v
```

### 运行交互式测试示例
```bash
cd src
python main.py < ../evaluation/input_files/menu_test.in
python main.py < ../evaluation/input_files/file_path_validation_test.in
python main.py < ../evaluation/input_files/entity_extraction_menu_test.in
```

## 测试数据

### 输入文件
- `test_novel.txt`: 包含人物、地点、时间、职业实体的测试小说
- `test_novel_gbk.txt`: GBK编码的测试文件
- `test_novel_utf8.txt`: UTF-8编码的测试文件
- `person_name_test.txt`: 人物姓名测试数据
- `location_test.txt`: 地理名称测试数据
- `time_test.txt`: 时间表达测试数据
- `profession_test.txt`: 职业称谓测试数据

### 交互输入文件
- `*.in`: 各种功能的模拟用户输入序列

## 注意事项

1. 运行测试前请确保已安装必要的依赖：
   ```bash
   pip install pytest numpy
   ```

2. 某些测试可能需要额外的依赖（如gensim），如果未安装会自动跳过相关测试。

3. 交互式测试使用输入重定向，确保输入文件格式正确。

4. 文件路径测试需要确保测试文件存在于正确位置。

## 测试结果评估

每个测试点都有对应的评分标准：
- 2分：完全符合要求
- 1分：部分符合要求
- 0分：不符合要求

详细的评分标准请参考 `metric.json` 文件。
