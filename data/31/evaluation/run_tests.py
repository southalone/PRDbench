"""
测试执行脚本
用于运行所有测试用例并生成测试报告
"""
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_pytest_tests():
    """运行pytest测试"""
    print("=" * 60)
    print("开始运行自动化测试...")
    print("=" * 60)
    
    # 切换到evaluation目录
    evaluation_dir = Path(__file__).parent
    
    # 运行pytest命令
    cmd = [
        sys.executable, "-m", "pytest",
        str(evaluation_dir / "tests"),
        "-v",
        "--tb=short",
        "--color=yes",
        f"--junitxml={evaluation_dir}/test_results.xml"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=evaluation_dir)
        
        print("测试输出:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print("-" * 40)
            print(result.stderr)
        
        print("=" * 60)
        if result.returncode == 0:
            print("✅ 所有测试通过!")
        else:
            print(f"❌ 测试失败，退出码: {result.returncode}")
        print("=" * 60)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False

def run_shell_tests():
    """运行shell交互测试"""
    print("\n" + "=" * 60)
    print("开始运行Shell交互测试...")
    print("=" * 60)
    
    # 读取测试计划
    test_plan_file = Path(__file__).parent / "detailed_test_plan.json"
    
    if not test_plan_file.exists():
        print("❌ 测试计划文件不存在")
        return False
    
    with open(test_plan_file, 'r', encoding='utf-8') as f:
        test_plan = json.load(f)
    
    shell_tests = [test for test in test_plan if test['type'] == 'shell_interaction']
    
    print(f"找到 {len(shell_tests)} 个Shell交互测试")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test in enumerate(shell_tests, 1):
        print(f"\n[{i}/{len(shell_tests)}] 测试: {test['metric']}")
        print("-" * 40)
        
        success = True
        for j, testcase in enumerate(test['testcases']):
            cmd = testcase['test_command']
            print(f"  执行命令: {cmd}")
            
            try:
                # 切换到项目根目录执行命令
                project_root = Path(__file__).parent.parent
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"  ✅ 命令执行成功")
                    if result.stdout.strip():
                        # 只显示前几行输出
                        output_lines = result.stdout.strip().split('\n')[:3]
                        for line in output_lines:
                            print(f"     {line}")
                        if len(result.stdout.strip().split('\n')) > 3:
                            print("     ...")
                else:
                    print(f"  ❌ 命令执行失败 (退出码: {result.returncode})")
                    if result.stderr:
                        error_lines = result.stderr.strip().split('\n')[:2]
                        for line in error_lines:
                            print(f"     错误: {line}")
                    success = False
                    
            except subprocess.TimeoutExpired:
                print(f"  ⏰ 命令执行超时")
                success = False
            except Exception as e:
                print(f"  ❌ 执行出错: {e}")
                success = False
        
        if success:
            passed_tests += 1
            print(f"  ✅ 测试通过")
        else:
            failed_tests += 1
            print(f"  ❌ 测试失败")
    
    print("\n" + "=" * 60)
    print(f"Shell交互测试结果: {passed_tests} 通过, {failed_tests} 失败")
    print("=" * 60)
    
    return failed_tests == 0

def generate_test_report():
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("生成测试报告...")
    print("=" * 60)
    
    report_content = f"""
# 测试执行报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 测试概述

本报告包含了大学生自控力与注意稳定性智能分析系统的完整测试结果。

## 测试类型

### 1. 单元测试 (Unit Tests)
- **测试文件:** evaluation/tests/test_*.py
- **测试框架:** pytest
- **覆盖范围:** 
  - 量表创建和管理
  - 数据导入导出
  - 统计分析功能
  - 数据管理功能
  - 可视化功能

### 2. Shell交互测试 (Shell Interaction Tests)
- **测试计划:** evaluation/detailed_test_plan.json
- **测试类型:** 命令行界面功能验证
- **覆盖范围:**
  - 程序启动和帮助信息
  - 各模块入口点验证
  - 数据导入导出命令
  - 分析命令执行

### 3. 文件比较测试 (File Comparison Tests)
- **测试内容:** 输出文件与期望文件的比较
- **覆盖范围:**
  - 量表导出文件格式
  - 报告生成文件内容
  - 图表导出文件质量

## 测试文件结构

```
evaluation/
├── detailed_test_plan.json     # 详细测试计划
├── pytest.ini                  # pytest配置
├── run_tests.py                # 测试执行脚本
├── tests/                      # 单元测试目录
│   ├── test_scale_creation.py
│   ├── test_scale_import_export.py
│   ├── test_statistical_analysis.py
│   ├── test_data_management.py
│   ├── test_visualization.py
│   └── test_data_export.py
├── test_*.csv                  # 测试输入文件
├── expected_*.csv              # 期望输出文件
└── temp_*                      # 临时测试文件
```

## 运行测试

### 运行所有测试
```bash
python evaluation/run_tests.py
```

### 运行特定测试
```bash
cd evaluation
pytest tests/test_scale_creation.py -v
```

### 运行Shell交互测试
```bash
python src/main.py --help
python src/main.py init
python src/main.py scales list
```

## 测试结果解读

- ✅ **通过:** 功能正常工作，符合预期
- ❌ **失败:** 功能存在问题，需要修复
- ⏰ **超时:** 执行时间过长，可能存在性能问题
- ⚠️ **警告:** 功能基本正常，但有改进空间

## 注意事项

1. 测试前请确保已安装所有依赖包
2. 某些测试需要创建临时文件，测试后会自动清理
3. 大数据集测试可能需要较长时间
4. 网络相关功能测试需要网络连接

## 故障排除

如果测试失败，请检查：
1. Python环境和依赖包是否正确安装
2. 数据库连接是否正常
3. 文件权限是否足够
4. 系统资源是否充足

---

*此报告由自动化测试系统生成*
"""
    
    report_file = Path(__file__).parent / "TEST_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content.strip())
    
    print(f"✅ 测试报告已生成: {report_file}")

def main():
    """主函数"""
    print("🚀 大学生自控力与注意稳定性智能分析系统 - 自动化测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行单元测试
    unit_test_success = run_pytest_tests()
    
    # 运行Shell交互测试
    shell_test_success = run_shell_tests()
    
    # 生成测试报告
    generate_test_report()
    
    # 总结
    print("\n" + "🎯" * 20)
    print("测试执行完成!")
    print("🎯" * 20)
    
    if unit_test_success and shell_test_success:
        print("🎉 所有测试通过! 系统功能正常。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查上述输出并修复问题。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)