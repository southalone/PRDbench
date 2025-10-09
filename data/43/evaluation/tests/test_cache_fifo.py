#!/usr/bin/env python3
"""
单元测试：缓存替换策略 - FIFO策略测试
测试Client类的缓存管理功能，验证FIFO（先进先出）策略是否正确实现。
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import Mock

# 添加src目录到路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from distributed_fs.client import Client


class TestCacheFIFO:
    """测试Client类的FIFO缓存策略"""
    
    def setup_method(self):
        """每个测试方法执行前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_proxy = Mock()
        self.mock_proxy.system_config = {'cache_size': 5}
        
        self.client = Client(self.mock_proxy)
        self.client.session_id = "test_session_123"
        self.client.username = "test_user"
        self.client.client_id = "test_client"
        self.client.cache_dir = os.path.join(self.temp_dir, 'cache')
        os.makedirs(self.client.cache_dir, exist_ok=True)
        self.client.cache_size = 5
        self.client.cache_queue.clear()
    
    def teardown_method(self):
        """每个测试方法执行后的清理工作"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def assert_equal(self, actual, expected, message=""):
        """简单的断言函数"""
        if actual != expected:
            raise AssertionError(f"断言失败: 期望 {expected}, 实际 {actual}. {message}")
        print(f"OK 断言通过: {message}")
    
    def test_cache_fifo_strategy(self):
        """测试FIFO缓存策略核心功能"""
        print("=" * 50)
        print("FIFO缓存策略单元测试")
        print("=" * 50)
        
        # 配置mock proxy
        def mock_read_file(session_id, file_name):
            return f"Content of {file_name}"
        
        self.mock_proxy.read_file = mock_read_file
        
        # 测试1: 填满缓存
        print("测试1: 填满缓存容量")
        for i in range(1, 6):  # file1.txt to file5.txt
            file_name = f'file{i}.txt'
            self.client.read_file(file_name)
        
        self.assert_equal(len(self.client.cache_queue), 5, "缓存队列大小为5")
        self.assert_equal(len(os.listdir(self.client.cache_dir)), 5, "缓存目录文件数量为5")
        
        # 测试2: FIFO淘汰
        print("测试2: FIFO淘汰机制")
        self.client.read_file('file6.txt')
        
        self.assert_equal(len(self.client.cache_queue), 5, "淘汰后队列大小仍为5")
        cached_files = os.listdir(self.client.cache_dir)
        if 'file1.txt' in cached_files:
            raise AssertionError("最早的文件file1.txt应该被淘汰")
        if 'file6.txt' not in cached_files:
            raise AssertionError("新文件file6.txt应该在缓存中")
        
        expected_queue = ['file2.txt', 'file3.txt', 'file4.txt', 'file5.txt', 'file6.txt']
        self.assert_equal(list(self.client.cache_queue), expected_queue, "FIFO淘汰后的队列顺序")
        
        print("=" * 50)
        print("所有FIFO缓存策略测试通过！")
        print("OK 缓存容量限制为5个文件")
        print("OK 先进先出(FIFO)的淘汰策略")
        print("=" * 50)
        
        return True


def test_cache_fifo_strategy():
    """主要测试函数"""
    test_instance = TestCacheFIFO()
    test_instance.setup_method()
    
    try:
        return test_instance.test_cache_fifo_strategy()
    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    success = test_cache_fifo_strategy()
    if not success:
        exit(1)