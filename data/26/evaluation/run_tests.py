#!/usr/bin/env python3
"""
OA系统测试执行器
自动化执行所有测试用例并生成测试报告
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

class TestRunner:
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
        
    def run_command(self, command, input_data=None, timeout=30):
        """执行命令并返回结果"""
        try:
            if input_data:
                process = subprocess.run(
                    command,
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    cwd=current_dir.parent
                )
            else:
                process = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    cwd=current_dir.parent
                )
            
            return {
                'returncode': process.returncode,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'success': process.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def run_unit_tests(self):
        """运行单元测试"""
        print("=" * 60)
        print("运行单元测试")
        print("=" * 60)
        
        # 检查pytest是否可用
        pytest_check = self.run_command(['python', '-m', 'pytest', '--version'])
        if not pytest_check['success']:
            print("❌ pytest未安装，跳过单元测试")
            print("请运行: pip install pytest")
            return
        
        # 运行所有单元测试
        test_files = [
            'evaluation/tests/test_system_init.py::test_database_initialization',
            'evaluation/tests/test_auth_service.py::test_user_authentication', 
            'evaluation/tests/test_workflow_service.py::test_workflow_operations'
        ]
        
        for test_file in test_files:
            print(f"\n运行测试: {test_file}")
            result = self.run_command(['python', '-m', 'pytest', test_file, '-v'])
            
            self.total_tests += 1
            if result['success']:
                print(f"✅ 通过: {test_file}")
                self.passed_tests += 1
            else:
                print(f"❌ 失败: {test_file}")
                print(f"错误信息: {result['stderr']}")
                self.failed_tests += 1
            
            self.test_results.append({
                'type': 'unit_test',
                'name': test_file,
                'success': result['success'],
                'output': result['stdout'],
                'error': result['stderr']
            })
    
    def run_shell_interaction_tests(self):
        """运行命令行交互测试"""
        print("\n" + "=" * 60)
        print("运行命令行交互测试")
        print("=" * 60)
        
        # 加载测试计划
        try:
            with open(current_dir / 'detailed_test_plan.json', 'r', encoding='utf-8') as f:
                test_plan = json.load(f)
        except Exception as e:
            print(f"❌ 无法加载测试计划: {e}")
            return
        
        # 筛选shell_interaction类型的测试
        shell_tests = [test for test in test_plan if test['type'] == 'shell_interaction']
        
        for test in shell_tests[:5]:  # 只运行前5个测试作为示例
            print(f"\n运行测试: {test['metric']}")
            
            for testcase in test['testcases']:
                command = testcase['test_command'].split()
                input_file = testcase.get('test_input')
                
                # 读取输入数据
                input_data = None
                if input_file:
                    try:
                        with open(current_dir / input_file, 'r', encoding='utf-8') as f:
                            input_data = f.read()
                    except Exception as e:
                        print(f"❌ 无法读取输入文件 {input_file}: {e}")
                        continue
                
                # 执行命令
                result = self.run_command(command, input_data)
                
                self.total_tests += 1
                
                # 简单的成功判断（程序不崩溃即为成功）
                if result['success'] or result['returncode'] == 0:
                    print(f"✅ 通过: {' '.join(command)}")
                    self.passed_tests += 1
                    success = True
                else:
                    print(f"❌ 失败: {' '.join(command)}")
                    print(f"错误信息: {result['stderr']}")
                    self.failed_tests += 1
                    success = False
                
                self.test_results.append({
                    'type': 'shell_interaction',
                    'name': test['metric'],
                    'command': ' '.join(command),
                    'success': success,
                    'output': result['stdout'][:500],  # 限制输出长度
                    'error': result['stderr']
                })
    
    def run_file_comparison_tests(self):
        """运行文件对比测试"""
        print("\n" + "=" * 60)
        print("运行文件对比测试")
        print("=" * 60)
        
        # 加载测试计划
        try:
            with open(current_dir / 'detailed_test_plan.json', 'r', encoding='utf-8') as f:
                test_plan = json.load(f)
        except Exception as e:
            print(f"❌ 无法加载测试计划: {e}")
            return
        
        # 筛选file_comparison类型的测试
        file_tests = [test for test in test_plan if test['type'] == 'file_comparison']
        
        for test in file_tests:
            print(f"\n运行测试: {test['metric']}")
            
            for testcase in test['testcases']:
                command = testcase['test_command'].split()
                input_file = testcase.get('test_input')
                
                # 读取输入数据
                input_data = None
                if input_file:
                    try:
                        with open(current_dir / input_file, 'r', encoding='utf-8') as f:
                            input_data = f.read()
                    except Exception as e:
                        print(f"❌ 无法读取输入文件 {input_file}: {e}")
                        continue
                
                # 执行命令
                result = self.run_command(command, input_data)
                
                self.total_tests += 1
                
                # 检查是否生成了预期文件
                expected_files = test.get('expected_output_files', [])
                files_exist = True
                
                for expected_file in expected_files:
                    if not os.path.exists(expected_file):
                        files_exist = False
                        break
                
                if result['success'] and files_exist:
                    print(f"✅ 通过: {' '.join(command)}")
                    self.passed_tests += 1
                    success = True
                else:
                    print(f"❌ 失败: {' '.join(command)}")
                    if not files_exist:
                        print("预期文件未生成")
                    if result['stderr']:
                        print(f"错误信息: {result['stderr']}")
                    self.failed_tests += 1
                    success = False
                
                self.test_results.append({
                    'type': 'file_comparison',
                    'name': test['metric'],
                    'command': ' '.join(command),
                    'success': success,
                    'output': result['stdout'][:500],
                    'error': result['stderr']
                })
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)
        
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests}")
        print(f"失败: {self.failed_tests}")
        print(f"成功率: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        # 按类型统计
        unit_tests = [r for r in self.test_results if r['type'] == 'unit_test']
        shell_tests = [r for r in self.test_results if r['type'] == 'shell_interaction']
        file_tests = [r for r in self.test_results if r['type'] == 'file_comparison']
        
        print(f"\n按类型统计:")
        print(f"单元测试: {len(unit_tests)} 个")
        print(f"命令行交互测试: {len(shell_tests)} 个")
        print(f"文件对比测试: {len(file_tests)} 个")
        
        # 保存详细报告
        report_file = current_dir / 'test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total': self.total_tests,
                    'passed': self.passed_tests,
                    'failed': self.failed_tests,
                    'success_rate': (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
                },
                'results': self.test_results,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存到: {report_file}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始执行OA系统测试套件")
        print("=" * 60)
        
        # 检查系统是否初始化
        print("检查系统状态...")
        db_file = current_dir.parent / "oa_system.db"
        if not db_file.exists():
            print("⚠️  数据库文件不存在，建议先初始化系统")
            print("运行: python src/main.py 然后选择 '2. 初始化系统'")
        
        # 运行各类测试
        self.run_unit_tests()
        self.run_shell_interaction_tests()
        self.run_file_comparison_tests()
        
        # 生成报告
        self.generate_report()


def main():
    """主函数"""
    runner = TestRunner()
    runner.run_all_tests()


if __name__ == '__main__':
    main()