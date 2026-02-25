"""
性能测试
"""
import sys
import os
import pytest
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from locallens.ui.cli_complete import CLI
from locallens.core.config import Config
from locallens.core.database import DatabaseManager
from locallens.search.engine import SearchEngine


class TestPerformance:
    """性能测试类"""

    @pytest.fixture
    def setup_cli(self):
        """设置测试环境"""
        cli = CLI()

        # 初始化配置和数据库连接
        config = Config()
        db_manager = DatabaseManager(config.database_path)
        search_engine = SearchEngine(config, db_manager)

        # 设置CLI组件
        cli.config = config
        cli.db_manager = db_manager
        cli.search_engine = search_engine

        return cli

    def test_search_response_time(self, setup_cli):
        """测试搜索响应时间"""
        cli = setup_cli

        # 设置位置
        cli.current_location = (27.91, -82.71)
        cli.search_engine.set_user_context(None, cli.current_location)

        # 准备5个不同的搜索查询
        queries = [
            "restaurant",
            "coffee",
            "pizza",
            "italian",
            "food"
        ]

        response_times = []

        # 执行5次搜索并记录响应时间
        for query in queries:
            start_time = time.time()

            results = cli.search_engine.search(
                query=query,
                location=cli.current_location
            )

            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)

            # 验证搜索成功
            assert results is not None, f"搜索 '{query}' 应该返回结果"

            # 验证单次搜索在5秒内完成
            assert response_time <= 5.0, f"搜索 '{query}' 响应时间 {response_time:.2f}s 超过5秒限制"

        # 计算平均响应时间
        avg_response_time = sum(response_times) / len(response_times)

        # 验证平均响应时间在3秒以内
        assert avg_response_time <= 3.0, f"平均响应时间 {avg_response_time:.2f}s 超过3秒限制"

        # 输出性能统计信息（用于调试）
        print(f"\n性能统计:")
        print(f"单次搜索响应时间: {[f'{t:.2f}s' for t in response_times]}")
        print(f"平均响应时间: {avg_response_time:.2f}s")
        print(f"最大响应时间: {max(response_times):.2f}s")
        print(f"最小响应时间: {min(response_times):.2f}s")
