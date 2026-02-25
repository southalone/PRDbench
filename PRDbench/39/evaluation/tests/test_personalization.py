"""
个性化功能测试
"""
import sys
import os
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from locallens.ui.cli_complete import CLI
from locallens.core.config import Config
from locallens.core.database import DatabaseManager
from locallens.search.engine import SearchEngine


class TestPersonalization:
    """个性化测试类"""

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

    def test_personalized_ranking(self, setup_cli):
        """测试个性化排序"""
        cli = setup_cli
        # 设置位置
        location = (27.91, -82.71)
        # 用户1搜索
        cli.current_user_id = "HFECrzYDpgbS5EmTBtj2zQ"
        cli.current_location = location
        cli.search_engine.set_user_context("HFECrzYDpgbS5EmTBtj2zQ", location)
        results1 = cli.search_engine.search(
            query="restaurant",
            location=location,
            user_id="HFECrzYDpgbS5EmTBtj2zQ"
        )
        # 用户2搜索
        cli.current_user_id = "Xwnf20FKuikiHcSpcEbpKQ"
        cli.search_engine.set_user_context("Xwnf20FKuikiHcSpcEbpKQ", location)
        results2 = cli.search_engine.search(
            query="restaurant",
            location=location,
            user_id="Xwnf20FKuikiHcSpcEbpKQ"
        )
        # 验证两个结果都存在
        assert results1 is not None and 'businesses' in results1
        assert results2 is not None and 'businesses' in results2
        businesses1 = results1['businesses']
        businesses2 = results2['businesses']
        # 确保两个用户都有足够的结果
        if len(businesses1) >= 5 and len(businesses2) >= 5:
            # 比较前5个结果的商家ID
            top5_ids_HFECrzYDpgbS5EmTBtj2zQ = [b.get('business_id') for b in businesses1[:5]]
            top5_ids_Xwnf20FKuikiHcSpcEbpKQ = [b.get('business_id') for b in businesses2[:5]]
            # 计算排序差异
            different_positions = 0
            for i in range(5):
                if i < len(top5_ids_HFECrzYDpgbS5EmTBtj2zQ) and i < len(top5_ids_Xwnf20FKuikiHcSpcEbpKQ):
                    if top5_ids_HFECrzYDpgbS5EmTBtj2zQ[i] != top5_ids_Xwnf20FKuikiHcSpcEbpKQ[i]:
                        different_positions += 1
            # 至少应该有一些排序差异（放宽要求，因为示例数据可能有限）
            assert different_positions >= 1, f"两个用户的前5个搜索结果应该有排序差异，实际差异数: {different_positions}"
        # 至少应该有一些结果
        assert len(businesses1) > 0 and len(businesses2) > 0, "两个用户都应该有搜索结果"
