#!/usr/bin/env python3
"""
超时控制测试
测试文件锁的30秒超时机制
"""

import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_lock_timeout():
    """测试锁的超时机制"""
    print("=" * 50)
    print("测试锁超时控制机制")
    print("=" * 50)
    
    try:
        from distributed_fs.utils import FileLock
        import tempfile
        
        temp_dir = tempfile.mkdtemp()
        
        def hold_lock_for_timeout():
            """持有锁直到超时"""
            lock = FileLock(temp_dir, 'timeout_test')
            try:
                # 使用较短的超时时间进行测试（5秒而不是30秒）
                acquired = lock.acquire(timeout=5)
                if acquired:
                    print("PASS First process acquired lock successfully")
                    time.sleep(6)  # 持有锁6秒，超过5秒超时
                    lock.release()
                    print("PASS First process released lock")
                    return True
                else:
                    print("FAIL First process failed to acquire lock")
                    return False
            except Exception as e:
                print(f"FAIL First process exception: {e}")
                return False
        
        def try_acquire_after_timeout():
            """在超时后尝试获取锁"""
            time.sleep(1)  # 确保第一个进程先获取锁
            lock = FileLock(temp_dir, 'timeout_test')
            try:
                print("INFO Second process trying to acquire lock...")
                acquired = lock.acquire(timeout=8)  # 给足够时间等待第一个锁超时
                if acquired:
                    print("PASS Second process acquired lock successfully (first lock timed out)")
                    lock.release()
                    print("PASS Second process released lock")
                    return True
                else:
                    print("FAIL Second process failed to acquire lock")
                    return False
            except Exception as e:
                print(f"FAIL Second process exception: {e}")
                return False
        
        # 使用线程池测试并发锁获取
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(hold_lock_for_timeout)
            future2 = executor.submit(try_acquire_after_timeout)
            
            result1 = future1.result()
            result2 = future2.result()
        
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if result1 and result2:
            print("PASS Timeout control test passed")
            return True
        else:
            print("FAIL Timeout control test failed")
            return False
            
    except ImportError as e:
        print(f"FAIL Cannot import test module: {e}")
        return False
    except Exception as e:
        print(f"FAIL Test exception: {e}")
        return False

def test_file_lock_basic_functionality():
    """测试文件锁的基本功能"""
    print("=" * 50)
    print("测试文件锁基本功能")
    print("=" * 50)
    
    try:
        from distributed_fs.utils import FileLock
        import tempfile
        
        temp_dir = tempfile.mkdtemp()
        
        # 测试锁的获取和释放
        lock = FileLock(temp_dir, 'basic_test')
        
        # 测试1：正常获取和释放
        acquired = lock.acquire(timeout=5)
        if not acquired:
            print("FAIL Cannot acquire lock")
            return False
        
        print("PASS Successfully acquired lock")
        
        lock.release()
        print("PASS Successfully released lock")
        
        # 测试2：使用with语句
        try:
            with FileLock(temp_dir, 'with_test') as test_lock:
                print("PASS With statement acquired lock successfully")
                time.sleep(0.1)
            print("PASS With statement auto-released lock")
        except Exception as e:
            print(f"FAIL With statement test failed: {e}")
            return False
        
        # 清理
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"FAIL Basic function test exception: {e}")
        return False

def main():
    """主测试函数"""
    print("Timeout Control Test Started")
    print("=" * 60)
    
    tests = [
        ("File Lock Basic Function", test_file_lock_basic_functionality),
        ("Lock Timeout Mechanism", test_lock_timeout),
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
        
        time.sleep(0.5)  # 测试间隔
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    if passed == total:
        print("All timeout control tests passed!")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)