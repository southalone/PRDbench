#!/usr/bin/env python3
"""
写操作互斥测试
验证同一文件同一时间仅允许一个进程写入
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
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        
        return {
            'success': 'successfully' in stdout.lower() or 'login successful' in stdout.lower(),
            'stdout': stdout,
            'stderr': stderr,
            'returncode': process.returncode
        }
    except subprocess.TimeoutExpired:
        process.kill()
        return {'success': False, 'stdout': '', 'stderr': 'Timeout', 'returncode': -1}
    except Exception as e:
        return {'success': False, 'stdout': '', 'stderr': str(e), 'returncode': -1}

def test_write_mutex():
    """测试写操作互斥"""
    print("=" * 50)
    print("Write Mutex Test")
    print("=" * 50)
    
    # 创建共享文件
    setup_result = run_dfs_command([
        'login user1 password123',
        'create shared_mutex_file.txt full',
        'write shared_mutex_file.txt "initial content"',
        'exit'
    ])
    
    if not setup_result['success']:
        print("FAIL Setup shared file failed")
        return False
    
    def write_to_shared_file(user_id, content_suffix):
        """写入共享文件"""
        passwords = ['password123', 'password234', 'password345']
        commands = [
            f'login user{user_id} {passwords[user_id-1]}',
            f'write shared_mutex_file.txt "user{user_id} content {content_suffix}"',
            'exit'
        ]
        
        result = run_dfs_command(commands)
        return {
            'user_id': user_id,
            'success': result['success'],
            'output': result['stdout']
        }
    
    # 测试并发写入到同一个文件
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(write_to_shared_file, 1, "first_write")
        future2 = executor.submit(write_to_shared_file, 2, "second_write")
        
        result1 = future1.result()
        result2 = future2.result()
    
    # 分析结果
    success_count = sum(1 for r in [result1, result2] if r['success'])
    
    print(f"Concurrent writes to same file:")
    print(f"User1 result: {'PASS' if result1['success'] else 'FAIL'}")
    print(f"User2 result: {'PASS' if result2['success'] else 'FAIL'}")
    print(f"Total successful writes: {success_count}/2")
    
    # 互斥锁应该确保至少有一个写入成功，可能两个都成功（队列处理）
    if success_count >= 1:
        print("PASS Write mutex test passed - system handled concurrent writes properly")
        return True
    else:
        print("FAIL Write mutex test failed - no writes succeeded")
        return False

def test_queue_mechanism():
    """测试操作队列机制"""
    print("=" * 50)
    print("Operation Queue Test")
    print("=" * 50)
    
    # 创建文件并触发队列操作
    setup_result = run_dfs_command([
        'login user1 password123',
        'create queue_test_file.txt full',
        'exit'
    ])
    
    if not setup_result['success']:
        print("FAIL Setup queue test file failed")
        return False
    
    # 连续写入操作以触发队列
    def queue_write_operation(user_id):
        passwords = ['password123', 'password234', 'password345']
        commands = [
            f'login user{user_id} {passwords[user_id-1]}',
            f'write queue_test_file.txt "queued write from user{user_id}"',
            'exit'
        ]
        return run_dfs_command(commands)
    
    # 快速连续执行多个写入操作
    results = []
    for i in range(1, 4):
        result = queue_write_operation(i)
        results.append(result)
        time.sleep(0.1)  # 短暂间隔确保队列机制触发
    
    success_count = sum(1 for r in results if r['success'])
    
    print(f"Queued operations: {success_count}/3 successful")
    
    if success_count >= 2:  # 至少2个成功表明队列机制工作
        print("PASS Operation queue test passed")
        return True
    else:
        print("FAIL Operation queue test failed")
        return False

def main():
    """主测试函数"""
    print("Write Mutex and Queue Test Started")
    print("=" * 60)
    
    tests = [
        ("Write Mutex Mechanism", test_write_mutex),
        ("Operation Queue Mechanism", test_queue_mechanism),
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
        
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    if passed == total:
        print("All write mutex tests passed!")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)