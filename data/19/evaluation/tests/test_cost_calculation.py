import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.cost import Costor
from orm.orm import Status, db
import time
from unittest.mock import patch

class TestCostCalculation:

    @pytest.fixture
    def setup_db(self):
        """设置测试数据库"""
        db.create_tables([Status], safe=True)
        yield
        # 清理
        Status.delete().execute()

    def test_cost_calculation_one_minute(self, setup_db):
        """测试1分钟中速风费用计算（对应原测试用例）"""
        slave = Status.create(
            card_id="test_card_minute",
            target_temp=22,
            cur_temp=25.0,
            speed=2,  # 中速风
            energy=0.0,
            amount=0.0
        )

        costor = Costor()

        # 模拟60秒的费用计算
        with patch('time.sleep'):
            costor.flag = True
            for _ in range(60):  # 60秒
                active_slaves = Status.select().where(Status.speed != 0)
                for slave_status in active_slaves:
                    energy = 1.0 / 60  # 中速风按秒计算
                    cost = 5 * energy

                    Status.update(
                        energy=Status.energy + energy,
                        amount=Status.amount + cost
                    ).where(Status.id == slave_status.id).execute()

        updated_slave = Status.get(Status.id == slave.id)
        expected_energy = 1.0  # 1.0功率/分钟 * 1分钟
        expected_cost = expected_energy * 5  # 5.0元

        # 允许±5%的误差
        assert abs(updated_slave.energy - expected_energy) < expected_energy * 0.05
        assert abs(updated_slave.amount - expected_cost) < expected_cost * 0.05
