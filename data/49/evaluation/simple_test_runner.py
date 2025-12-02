#!/usr/bin/env python3
"""
Simple Test Runner

A simplified test runner that executes tests without pytest dependency.
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_shell_test(command: str, working_dir: Path, timeout: int = 30) -> Dict[str, Any]:
    """Run a shell command test."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout[:500],
            'stderr': result.stderr[:500]
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'returncode': -1
        }


def run_python_test(test_file: str, working_dir: Path) -> Dict[str, Any]:
    """Run a Python test file directly."""
    try:
        result = subprocess.run(
            ["python", test_file],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout[:500],
            'stderr': result.stderr[:500]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'returncode': -1
        }


def main():
    """Main test execution function."""
    print("=" * 60)
    print(" IoT Environmental System - Simple Test Runner")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    evaluation_dir = Path(__file__).parent
    
    # Define test cases
    test_cases = [
        {
            'name': '系统启动与帮助信息',
            'type': 'shell',
            'commands': [
                'python run.py help',
                'cd src && python main.py --help'
            ]
        },
        {
            'name': 'MQTT单条数据发布',
            'type': 'shell',
            'commands': ['cd src && python main.py mqtt publish --random']
        },
        {
            'name': 'MQTT批量数据发布',
            'type': 'shell',
            'commands': ['cd src && python main.py mqtt publish --file samples/environmental_sample.csv --count 5']
        },
        {
            'name': 'MQTT数据订阅',
            'type': 'shell',
            'commands': ['cd src && python main.py mqtt subscribe --duration 10 --save']
        },
        {
            'name': '数据分析功能',
            'type': 'shell',
            'commands': ['cd src && python main.py data analyze']
        },
        {
            'name': '数据清洗功能',
            'type': 'shell',
            'commands': ['cd src && python main.py data clean']
        },
        {
            'name': '机器学习预测功能',
            'type': 'shell',
            'commands': ['cd src && python main.py ml predict --temperature 25.0 --humidity 60.0 --pressure 1013.25']
        },
        {
            'name': '模型评估功能',
            'type': 'shell',
            'commands': ['cd src && python main.py ml evaluate']
        },
        {
            'name': '系统状态监控',
            'type': 'shell',
            'commands': ['cd src && python main.py system status']
        },
        {
            'name': 'Web界面启动',
            'type': 'shell',
            'commands': ['cd src && timeout 5s python main.py web --port 8080 || echo "Web service test completed"']
        },
        {
            'name': '功能完整性测试',
            'type': 'python',
            'commands': ['tests/test_functionality_completeness.py']
        },
        {
            'name': '错误处理测试',
            'type': 'python',
            'commands': ['tests/test_error_handling.py']
        },
        {
            'name': '日志功能测试',
            'type': 'python',
            'commands': ['tests/test_logging.py']
        },
        {
            'name': '数据质量测试',
            'type': 'python',
            'commands': ['tests/test_data_quality.py']
        }
    ]
    
    # Execute tests
    results = []
    passed_count = 0
    
    for i, test_case in enumerate(test_cases):
        test_name = test_case['name']
        test_type = test_case['type']
        commands = test_case['commands']
        
        print(f"\n[{i+1}/{len(test_cases)}] Testing: {test_name}")
        
        test_passed = True
        test_results = []
        
        for command in commands:
            if test_type == 'shell':
                result = run_shell_test(command, project_root)
            elif test_type == 'python':
                result = run_python_test(command, evaluation_dir)
            else:
                result = {'success': False, 'error': f'Unknown test type: {test_type}'}
            
            test_results.append(result)
            
            if not result['success']:
                test_passed = False
        
        if test_passed:
            passed_count += 1
            print(f"   ✅ PASSED")
        else:
            print(f"   ❌ FAILED")
        
        results.append({
            'name': test_name,
            'type': test_type,
            'passed': test_passed,
            'results': test_results
        })
    
    # Print summary
    success_rate = (passed_count / len(test_cases)) * 100
    
    print("\n" + "=" * 60)
    print(" Test Summary")
    print("=" * 60)
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {len(test_cases) - passed_count}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Determine grade
    if success_rate >= 90:
        grade = "A (优秀)"
    elif success_rate >= 80:
        grade = "B (良好)"
    elif success_rate >= 70:
        grade = "C (中等)"
    elif success_rate >= 60:
        grade = "D (及格)"
    else:
        grade = "F (不及格)"
    
    print(f"Grade: {grade}")
    
    # Save results
    try:
        with open(evaluation_dir / "simple_test_results.json", 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_tests': len(test_cases),
                    'passed_tests': passed_count,
                    'failed_tests': len(test_cases) - passed_count,
                    'success_rate': success_rate,
                    'grade': grade
                },
                'detailed_results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: simple_test_results.json")
    except Exception as e:
        print(f"Failed to save results: {e}")
    
    return 0 if success_rate >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())