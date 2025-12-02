# OA系统测试方案

本目录包含了完整的OA系统测试方案，基于 `metric.json` 中定义的功能评估指标生成。

## 文件结构

```
evaluation/
├── README.md                    # 本说明文件
├── metric.json                  # 原始功能评估指标
├── detailed_test_plan.json      # 详细测试计划
├── tests/                       # 自动化测试脚本
│   ├── __init__.py
│   ├── test_system_init.py      # 系统初始化测试
│   ├── test_auth_service.py     # 认证服务测试
│   └── test_workflow_service.py # 工作流服务测试
├── *.in                        # 测试输入文件
└── expected_*.csv              # 期望输出文件
```

## 测试类型说明

### 1. Shell Interaction Tests (命令行交互测试)
这类测试模拟用户与命令行程序的真实交互，验证程序的用户界面和交互流程。

**执行方式:**
```bash
# 示例：测试用户登录
python src/main.py login admin < evaluation/admin_login.in
```

### 2. Unit Tests (单元测试)
使用pytest框架的自动化测试，验证核心业务逻辑和服务功能。

**执行方式:**
```bash
# 运行所有单元测试
pytest evaluation/tests/

# 运行特定测试
pytest evaluation/tests/test_system_init.py::test_database_initialization
pytest evaluation/tests/test_auth_service.py::test_user_authentication
pytest evaluation/tests/test_workflow_service.py::test_workflow_operations
```

### 3. File Comparison Tests (文件对比测试)
验证程序生成的输出文件是否符合预期格式和内容。

**执行方式:**
```bash
# 生成输出文件
python src/main.py < evaluation/data_export.in

# 对比生成的文件与期望文件
diff export.csv evaluation/expected_export.csv
```

## 测试执行步骤

### 前置条件
1. 确保Python环境已安装必要依赖：
   ```bash
   pip install pytest sqlalchemy rich click
   ```

2. 初始化系统数据库：
   ```bash
   python src/main.py
   # 选择 "2. 初始化系统"
   ```

### 执行测试

#### 1. 运行单元测试
```bash
# 进入项目根目录
cd /path/to/OA

# 运行所有单元测试
pytest evaluation/tests/ -v

# 运行特定测试模块
pytest evaluation/tests/test_system_init.py -v
pytest evaluation/tests/test_auth_service.py -v
pytest evaluation/tests/test_workflow_service.py -v
```

#### 2. 运行命令行交互测试
```bash
# 测试系统帮助信息
python src/main.py --help

# 测试用户登录
python src/main.py login admin < evaluation/admin_login.in

# 测试用户列表
python src/main.py user list

# 测试工作流模板
python src/main.py workflow templates

# 测试用户创建
python src/main.py user create < evaluation/user_create.in
```

#### 3. 运行文件对比测试
```bash
# 执行数据导出功能
python src/main.py < evaluation/data_export.in

# 检查生成的文件
ls -la export.csv

# 对比文件内容（如果支持导出功能）
diff export.csv evaluation/expected_export.csv
```

## 测试覆盖范围

本测试方案覆盖了以下功能模块：

### 系统基础功能
- [x] 系统启动与帮助显示
- [x] 用户登录认证
- [x] 主菜单显示
- [x] 个人信息管理
- [x] 用户登出功能

### 用户管理功能
- [x] 用户列表查看
- [x] 用户详情查看
- [x] 用户创建（交互式）
- [x] 用户创建（字段验证）
- [x] 部门信息查看
- [x] 角色信息查看

### 工作流管理功能
- [x] 工作流模板列表
- [x] 工作流模板详情
- [x] 工作流启动
- [x] 工作流实例管理
- [x] 待办任务查看
- [x] 任务处理操作

### 系统安全功能
- [x] 权限控制验证
- [x] 错误处理机制
- [x] 密码修改功能

## 测试数据

### 预设用户账户
- **管理员**: 用户名 `admin`, 密码 `admin123`
- **经理**: 用户名 `manager`, 密码 `manager123`  
- **员工**: 用户名 `employee`, 密码 `employee123`

### 测试输入文件说明
- `admin_login.in`: 管理员登录密码
- `user_create.in`: 创建新用户的输入数据
- `user_create_invalid.in`: 包含无效数据的用户创建输入
- `workflow_start.in`: 启动工作流的输入数据
- `workflow_start_form.in`: 工作流表单数据输入
- `change_password.in`: 密码修改输入
- `permission_test.in`: 权限测试输入
- `data_export.in`: 数据导出功能输入

## 预期结果

每个测试用例的预期结果已在 `detailed_test_plan.json` 中详细定义。测试执行时应对照预期结果验证实际输出。

### 成功标准
- **Shell Interaction Tests**: 程序正常执行，输出包含预期信息，无崩溃
- **Unit Tests**: 所有断言通过，测试用例执行成功
- **File Comparison Tests**: 生成文件与期望文件内容匹配

### 失败处理
如果测试失败，请检查：
1. 系统是否正确初始化
2. 数据库连接是否正常
3. 输入数据格式是否正确
4. 程序逻辑是否符合预期

## 注意事项

1. **数据库隔离**: 单元测试使用独立的测试数据库，不会影响主数据库
2. **测试顺序**: 某些测试可能依赖于系统初始化，建议先运行系统初始化
3. **环境清理**: 测试完成后会自动清理测试数据库文件
4. **权限要求**: 某些测试需要管理员权限，确保使用正确的用户账户

## 扩展测试

如需添加新的测试用例：

1. **Shell Interaction**: 在 `detailed_test_plan.json` 中添加新的测试项，创建对应的 `.in` 输入文件
2. **Unit Tests**: 在 `tests/` 目录下创建新的测试文件，遵循 `test_*.py` 命名规范
3. **File Comparison**: 创建期望输出文件，在测试计划中指定文件路径

## 技术支持

如遇到测试执行问题，请检查：
- Python版本兼容性（推荐Python 3.8+）
- 依赖包安装完整性
- 文件路径和权限设置
- 数据库配置正确性