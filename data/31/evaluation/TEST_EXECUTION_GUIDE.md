# 测试执行指南

## 为什么需要先运行 `python src/main.py init`？

### 1. **数据库表创建**
```python
def init():
    # 创建数据库表
    create_tables()  # 这会创建所有必要的数据库表结构
    
    # 创建默认量表
    scale_manager.create_default_scales()
```

### 2. **系统依赖关系**
- **数据库表**: 系统使用SQLite数据库存储数据，需要先创建表结构
- **默认量表**: 系统预置了3个标准心理量表，为后续测试提供基础数据
- **配置初始化**: 确保所有配置和路径正确设置

### 3. **测试执行顺序的重要性**

#### 错误的执行方式：
```bash
# ❌ 直接导入量表 - 会失败
python src/main.py scales import-csv evaluation/test_scale.csv
# 错误：数据库表不存在，无法保存量表数据
```

#### 正确的执行方式：
```bash
# ✅ 先初始化系统
python src/main.py init
# 创建数据库表：scales, scale_items, participants, responses等

# ✅ 然后导入量表
python src/main.py scales import-csv evaluation/test_scale.csv
# 现在可以成功保存到数据库
```

### 4. **init命令具体做了什么**

1. **创建数据库表结构**：
   - `scales` 表：存储量表基本信息
   - `scale_items` 表：存储量表条目
   - `participants` 表：存储被试者信息
   - `responses` 表：存储问卷回答
   - `analysis_results` 表：存储分析结果

2. **创建默认量表**：
   - 大学生注意稳定性量表（8个条目）
   - 大学生自控力量表（10个条目）
   - 大学生情绪稳定性量表（6个条目）

3. **验证系统完整性**：
   - 检查数据库连接
   - 验证配置文件
   - 确保输出目录存在

### 5. **测试场景分析**

#### Shell交互测试的典型流程：
```bash
# 步骤1：系统准备
python src/main.py init                    # 必需：创建基础环境

# 步骤2：执行具体功能
python src/main.py scales import-csv file.csv  # 测试目标功能

# 步骤3：验证结果
python src/main.py scales list             # 确认导入成功
```

#### 为什么不能跳过init：
- **数据库错误**: 没有表结构，无法保存数据
- **配置缺失**: 系统配置未初始化
- **依赖缺失**: 缺少默认量表等基础数据

### 6. **测试独立性考虑**

虽然每个测试都需要init，但这是**系统级别的前置条件**，不是测试设计问题：

- **真实用户场景**: 用户首次使用系统时也需要先初始化
- **系统架构要求**: 基于数据库的系统必须先创建表结构
- **功能依赖**: 很多功能依赖于默认量表的存在

### 7. **优化建议**

对于频繁测试，可以考虑：

```bash
# 一次性初始化
python src/main.py init

# 然后运行多个测试
python src/main.py scales import-csv test1.csv
python src/main.py scales import-csv test2.csv
python src/main.py data import-participants participants.csv
```

### 8. **测试结果验证**

init命令成功的标志：
- ✅ 显示"系统初始化完成！"
- ✅ 列出创建的默认量表
- ✅ 无错误信息输出
- ✅ 退出码为0

这样的设计确保了测试的**真实性**和**可靠性**，模拟了用户的实际使用流程。