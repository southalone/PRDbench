# VSCode终端UTF-8编码配置说明

## 已完成的配置

我已经为这个项目创建了 `.vscode/settings.json` 配置文件，包含以下设置：

```json
{
    "terminal.integrated.env.windows": {
        "PYTHONIOENCODING": "utf-8"
    },
    "terminal.integrated.profiles.windows": {
        "Command Prompt UTF-8": {
            "path": "C:\\windows\\System32\\cmd.exe",
            "args": ["/k", "chcp 65001"]
        }
    },
    "terminal.integrated.defaultProfile.windows": "Command Prompt UTF-8"
}
```

## 使配置生效的步骤

### 方法1：重新加载VSCode窗口
1. 按 `Ctrl + Shift + P` 打开命令面板
2. 输入 `Developer: Reload Window`
3. 回车执行，VSCode将重新加载

### 方法2：新建终端
1. 关闭当前终端（点击垃圾桶图标）
2. 按 `Ctrl + Shift + `` 新建终端
3. 新终端将自动应用UTF-8配置

### 方法3：手动选择终端配置文件
1. 点击终端右上角的 `+` 旁边的下拉箭头
2. 选择 "Command Prompt UTF-8"
3. 新终端将使用UTF-8编码

## 验证配置是否生效

新建终端后运行以下命令验证：

```bash
# 检查代码页（应该显示 65001）
chcp

# 检查Python编码环境变量
echo %PYTHONIOENCODING%

# 测试中文显示
python evaluation/verify_file_comparison_test.py
```

## 预期结果

- `chcp` 应该显示 `Active code page: 65001`
- `echo %PYTHONIOENCODING%` 应该显示 `utf-8`
- Python脚本的中文输出应该正常显示，不再有乱码

## 其他说明

- 这个配置只对当前项目有效（工作区级别设置）
- 如果要全局生效，需要在用户设置中添加相同配置
- 配置文件位置：`.vscode/settings.json`