#!/usr/bin/env python3
"""
并发读取测试
验证多个进程可同时读取同一文件
"""

import os
import sys
import time
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def run_dfs_command(commands, timeout=15):
    """运行分布式文件系统命令"""
    try:
        process = subprocess.Popen(
            ['python', 'src/distributed_fs/main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd='.'
        )
        
        input_text = '\n'.join(commands) + '\n'
        start_time = time.time()
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        end_time = time.time()
        
        return {
            'success': 'successfully' in stdout.lower() or 'login successful' in stdout.lower(),
            'stdout': stdout,
            'stderr': stderr,
            'returncode': process.returncode,
            'duration': end_time - start_time
        }
    except subprocess.TimeoutExpired:
        process.kill()
        return {'success': False, 'stdout': '', 'stderr': 'Timeout', 'returncode': -1, 'duration': timeout}
    except Exception as e:
        return {'success': False, 'stdout': '', 'stderr': str(e), 'returncode': -1, 'duration': 0}

def test_concurrent_reads():
    """测试并发读取操作"""
    print("=" * 50)
    print("Concurrent Reads Test")
    print("=" * 50)
    
    # 设置共享测试文件
    setup_result = run_dfs_command([
        'login user1 password123',
        'create shared_read_file.txt full',
        'write shared_read_file.txt "This is shared content for concurrent reading test"',
        'exit'
    ])
    
    if not setup_result['success']:
        print("FAIL Setup shared read file failed")
        return False
    
    def concurrent_read(user_id):
        """并发读取函数"""
        passwords = ['password123', 'password234', 'password345']
        commands = [
            f'login user{user_id} {passwords[user_id-1]}',
            'read shared_read_file.txt',
            'exit'
        ]
        
        result = run_dfs_command(commands)
        return {
            'user_id': user_id,
            'success': result['success'],
            'duration': result['duration'],
            'content_found': 'shared content for concurrent reading' in result['stdout'],
            'output': result['stdout']
        }
    
    # 启动3个并发读取操作
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(1, 4):
            future = executor.submit(concurrent_read, i)
            futures.append(future)
        
        results = []
        for future in futures:
            results.append(future.result())
    
    # 分析结果
    successful_reads = [r for r in results if r['success'] and r['content_found']]
    fast_reads = [r for r in results if r['duration'] <= 2.0]  # 允许2秒内完成
    
    print(f"Successful reads: {len(successful_reads)}/3")
    print(f"Fast reads (<=2s): {len(fast_reads)}/3")
    
    for result in results:
        print(f"User{result['user_id']}: {'PASS' if result['success'] and result['content_found'] else 'FAIL'} "
              f"({result['duration']:.2f}s)")
    
    if len(successful_reads) >= 3:
        print("PASS Concurrent reads test passed - all clients can read simultaneously")
        return True
    else:
        print("FAIL Concurrent reads test failed - some reads failed")
        return False

def test_read_performance():
    """测试读取性能"""
    print("=" * 50)
    print("Read Performance Test")
    print("=" * 50)
    
    # 创建性能测试文件
    setup_result = run_dfs_command([
        'login user1 password123',
        'create performance_test.txt full',
        'write performance_test.txt "Performance test content for timing verification"',
        'exit'
    ])
    
    if not setup_result['success']:
        print("FAIL Setup performance test file failed")
        return False
    
    # 测试多次读取的性能
    def timed_read():
        commands = [
            'login user1 password123',
            'read performance_test.txt',
            'read performance_test.txt',  # 第二次应该命中缓存
            'read performance_test.txt',  # 第三次也应该命中缓存
            'exit'
        ]
        
        return run_dfs_command(commands)
    
    result = timed_read()
    
    if result['success'] and result['duration'] <= 3.0:  # 3次读取应该在3秒内完成
        print(f"PASS Read performance test passed ({result['duration']:.2f}s for 3 reads)")
        return True
    else:
        print(f"FAIL Read performance test failed ({result['duration']:.2f}s for 3 reads)")
        return False

def main():
    """主测试函数"""
    print("Concurrent Reads Test Started")
    print("=" * 60)
    
    tests = [
        ("Concurrent Read Operations", test_concurrent_reads),
        ("Read Performance", test_read_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nExecuting Test: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"PASS {test_name}: Success")
            else:
                print(f"FAIL {test_name}: Failed")
        except Exception as e:
            print(f"FAIL {test_name}: Exception - {e}")
        
        time.sleep(1)  # 测试间隔
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    if passed == total:
        print("All concurrent reads tests passed!")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)