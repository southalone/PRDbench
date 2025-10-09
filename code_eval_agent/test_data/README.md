# Judge工具测试数据

这个目录包含了用于测试Judge工具的测试程序和输入数据。

## 测试程序

### 1. hello_world.py
- **功能**: 简单的Hello World程序，要求用户输入姓名
- **预期行为**: 输出欢迎信息和用户姓名
- **配套输入**: input_name.txt

### 2. calculator.py
- **功能**: 交互式计算器，计算两个数的加法和乘法
- **预期行为**: 输出加法和乘法结果
- **配套输入**: input_normal.txt (正常数字), input_invalid.txt (无效输入)

### 3. error_program.py
- **功能**: 故意崩溃的程序，用于测试错误处理
- **预期行为**: 输出一些信息后抛出异常
- **配套输入**: 无需输入

## 输入数据文件

### input_normal.txt
```
15
3
```
用于calculator.py的正常输入测试。

### input_name.txt
```
张三
```
用于hello_world.py的姓名输入。

### input_invalid.txt
```
abc
def
```
用于测试程序对无效输入的处理。

## 使用示例

```bash
# 手动测试程序
echo "张三" | python hello_world.py
cat input_normal.txt | python calculator.py

# 使用Judge工具测试
python test_judge.py
```

## Judge工具调用示例

```python
# 测试Hello World程序
judge(
    context="程序应该输出Hello World和用户姓名",
    entry_command="python test_data/hello_world.py",
    input_file="test_data/input_name.txt"
)

# 测试计算器程序
judge(
    context="程序应该输出15+3=18和15×3=45的计算结果", 
    entry_command="python test_data/calculator.py",
    input_file="test_data/input_normal.txt"
)

# 测试错误处理
judge(
    context="程序会崩溃并抛出异常",
    entry_command="python test_data/error_program.py"
)
``` 