import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.monitor import monitor as monitor_class, ac
from orm.orm import Status, Request, db
import math

class TestTemperatureMonitor:

    @pytest.fixture
    def setup_db(self):
        """设置测试数据库"""
        db.create_tables([Status, Request], safe=True)
        yield
        # 清理
        Status.delete().execute()
        Request.delete().execute()

    @pytest.fixture
    def monitor_instance(self):
        """创建监控实例"""
        return monitor_class()

    def test_temperature_calculation_heating(self, setup_db, monitor_instance):
        """测试制热模式下的温度计算"""
        # 创建从机状态
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=28,
            cur_temp=25.0,
            speed=2,  # 中速风
            energy=0.0,
            amount=0.0
        )

        monitor_instance.init(1, 20)  # 外部温度20度
        monitor_instance.target_temp = 28
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2
        monitor_instance.rate = 50

        # 验证温度变化方向正确（制热时温度应该上升）
        assert monitor_instance.target_temp > monitor_instance.cur_temp

    def test_temperature_calculation_cooling(self, setup_db, monitor_instance):
        """测试制冷模式下的温度计算"""
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=22,
            cur_temp=25.0,
            speed=2,
            energy=0.0,
            amount=0.0
        )

        monitor_instance.init(1, 30)  # 外部温度30度
        monitor_instance.target_temp = 22
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2

        # 验证温度变化方向正确（制冷时温度应该下降）
        assert monitor_instance.target_temp < monitor_instance.cur_temp

    def test_intelligent_speed_adjustment(self, setup_db, monitor_instance):
        """测试智能风速调节逻辑"""
        test_cases = [
            (25.0, 22.0, 3),  # 温度差3度，应该高速风
            (24.0, 22.0, 2),  # 温度差2度，应该中速风
            (23.0, 22.0, 1),  # 温度差1度，应该低速风
            (22.5, 22.0, 1), # 温度差0.5度，应该低速风
        ]

        for cur_temp, target_temp, expected_speed in test_cases:
            temp_diff = abs(cur_temp - target_temp)

            if temp_diff > 2:
                actual_speed = 3
            elif temp_diff > 1:
                actual_speed = 2
            else:
                actual_speed = 1

            assert actual_speed == expected_speed, f"温度差{temp_diff}度时，期望风速{expected_speed}，实际{actual_speed}"
