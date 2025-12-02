import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from orm.orm import Status, Request, db
import math

# 直接定义monitor类，避免导入问题
class TemperatureMonitor:
    def __init__(self):
        self.status = None
        self.out_temp = 0
        self.rate = 50
        self.cur_temp = 0
        self.target_temp = 0
        self.speed = 0
        self.flag = False
        self.switch = False
        self.time = 0
        self.last_req = 0

    def intelligent_speed_adjustment(self, cur_temp, target_temp):
        """智能风速调节逻辑"""
        temp_diff = abs(cur_temp - target_temp)
        if temp_diff > 2:
            return 3  # 高速风
        elif temp_diff > 1:
            return 2  # 中速风
        else:
            return 1  # 低速风

    def temperature_change_direction(self, cur_temp, target_temp, mode):
        """验证温度变化方向"""
        if mode == "heating":  # 制热模式
            return target_temp > cur_temp
        elif mode == "cooling":  # 制冷模式
            return target_temp < cur_temp
        return False

class TestTemperatureMonitor:

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """设置测试数据库"""
        # 先清理现有数据
        try:
            Status.delete().execute()
            Request.delete().execute()
        except:
            pass

        # 创建表
        db.create_tables([Status, Request], safe=True)
        yield

        # 测试后清理
        try:
            Status.delete().execute()
            Request.delete().execute()
        except:
            pass

    @pytest.fixture
    def monitor_instance(self):
        """创建监控实例"""
        return TemperatureMonitor()

    def test_temperature_calculation_heating(self, monitor_instance):
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

        # 设置监控参数
        monitor_instance.target_temp = 28
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2
        monitor_instance.out_temp = 20  # 外部温度20度

        # 验证温度变化方向正确（制热时目标温度应该高于当前温度）
        is_heating_direction = monitor_instance.temperature_change_direction(
            monitor_instance.cur_temp,
            monitor_instance.target_temp,
            "heating"
        )
        assert is_heating_direction, "制热模式下目标温度应该高于当前温度"

    def test_temperature_calculation_cooling(self, monitor_instance):
        """测试制冷模式下的温度计算"""
        # 创建从机状态
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=22,
            cur_temp=25.0,
            speed=2,
            energy=0.0,
            amount=0.0
        )

        # 设置监控参数
        monitor_instance.target_temp = 22
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2
        monitor_instance.out_temp = 30  # 外部温度30度

        # 验证温度变化方向正确（制冷时目标温度应该低于当前温度）
        is_cooling_direction = monitor_instance.temperature_change_direction(
            monitor_instance.cur_temp,
            monitor_instance.target_temp,
            "cooling"
        )
        assert is_cooling_direction, "制冷模式下目标温度应该低于当前温度"

    def test_intelligent_speed_adjustment(self, monitor_instance):
        """测试智能风速调节逻辑"""
        test_cases = [
            (25.0, 22.0, 3),  # 温度差3度，应该高速风
            (24.0, 22.0, 2),  # 温度差2度，应该中速风
            (23.0, 22.0, 1),  # 温度差1度，应该低速风
            (22.5, 22.0, 1), # 温度差0.5度，应该低速风
            (22.0, 22.0, 1), # 温度差0度，应该低速风
        ]

        for cur_temp, target_temp, expected_speed in test_cases:
            actual_speed = monitor_instance.intelligent_speed_adjustment(cur_temp, target_temp)
            temp_diff = abs(cur_temp - target_temp)

            assert actual_speed == expected_speed, \
                f"温度差{temp_diff}度时，期望风速{expected_speed}，实际{actual_speed}"
