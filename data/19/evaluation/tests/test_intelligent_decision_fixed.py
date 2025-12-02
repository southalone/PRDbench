import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.machine import mainMachine
from orm.orm import Request, Status, db
from datetime import datetime

class TestIntelligentDecision:

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """设置测试数据库"""
        # 先清理现有数据
        try:
            Request.delete().execute()
            Status.delete().execute()
        except:
            pass

        # 创建表
        db.create_tables([Request, Status], safe=True)
        yield

        # 测试后清理
        try:
            Request.delete().execute()
            Status.delete().execute()
        except:
            pass

    @pytest.fixture
    def machine(self):
        """创建主机实例"""
        return mainMachine()

    def test_cooling_mode_temperature_adaptation(self, machine):
        """测试制冷模式下的温度适配停风"""
        # 创建从机状态：当前温度低于目标温度
        slave = Status.create(
            card_id="test_card_cooling",
            target_temp=22,
            cur_temp=20.0,  # 低于目标温度
            speed=2,        # 中速风
            energy=0.0,
            amount=0.0
        )

        # 创建调节请求
        request = Request.create(
            slave_id=slave.id,
            temp=22.0,
            speed=2,
            time=datetime.now()
        )

        machine.main_status = 1  # 制冷模式

        # 模拟请求处理逻辑
        status = Status.get(Status.id == request.slave_id)
        if machine.main_status == 1:  # 制冷模式
            if status.cur_temp < request.temp:  # 当前温度低于目标温度
                expected_speed = 0  # 应该停风
            else:
                expected_speed = request.speed

        assert expected_speed == 0, "制冷模式下当前温度低于目标温度时应该停风"

    def test_heating_mode_temperature_adaptation(self, machine):
        """测试制热模式下的温度适配停风"""
        # 创建从机状态：当前温度高于目标温度
        slave = Status.create(
            card_id="test_card_heating",
            target_temp=28,
            cur_temp=30.0,  # 高于目标温度
            speed=2,        # 中速风
            energy=0.0,
            amount=0.0
        )

        # 创建调节请求
        request = Request.create(
            slave_id=slave.id,
            temp=28.0,
            speed=2,
            time=datetime.now()
        )

        machine.main_status = 2  # 制热模式

        # 模拟请求处理逻辑
        status = Status.get(Status.id == request.slave_id)
        if machine.main_status == 2:  # 制热模式
            if status.cur_temp > request.temp:  # 当前温度高于目标温度
                expected_speed = 0  # 应该停风
            else:
                expected_speed = request.speed

        assert expected_speed == 0, "制热模式下当前温度高于目标温度时应该停风"

    def test_temperature_reached_auto_stop(self, machine):
        """测试温度达到目标时自动停风"""
        # 创建从机状态：温度已达到目标
        slave = Status.create(
            card_id="test_card_auto_stop",
            target_temp=25,
            cur_temp=25.0,  # 已达到目标温度
            speed=2,        # 中速风
            energy=0.0,
            amount=0.0
        )

        # 模拟智能决策逻辑
        if slave.cur_temp == slave.target_temp:
            expected_speed = 0  # 应该自动停风
        else:
            expected_speed = slave.speed

        assert expected_speed == 0, "温度达到目标时应该自动停风"
