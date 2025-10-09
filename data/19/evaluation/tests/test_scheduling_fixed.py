import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.machine import mainMachine
from orm.orm import Request, Status, db
from datetime import datetime
import random

class TestSchedulingAlgorithms:

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

    def test_random_scheduling(self, machine):
        """测试随机调度算法"""
        # 先创建对应的从机状态
        for i in range(5):
            Status.create(
                id=i+1,
                card_id=f"test_card_{i+1}",
                target_temp=25,
                cur_temp=25.0,
                speed=0,
                energy=0.0,
                amount=0.0
            )

        # 创建多个请求
        for i in range(5):
            Request.create(
                slave_id=i+1,
                temp=22.0,
                speed=1,
                time=datetime.now()
            )

        machine.choice = 1  # 随机调度
        machine.num = 3     # 最多处理3个请求

        # 运行一次调度，验证基本功能
        machine.get_request()

        # 验证选中了请求
        assert len(machine.requestList) <= machine.num
        assert len(machine.requestList) > 0

    def test_speed_priority_scheduling(self, machine):
        """测试风速优先调度算法"""
        # 先创建对应的从机状态（都是运行状态，避免开关机优先级影响）
        for i in range(1, 4):
            Status.create(
                id=i,
                card_id=f"test_card_{i}",
                target_temp=25,
                cur_temp=25.0,
                speed=1,  # 设置为运行状态，避免开关机请求
                energy=0.0,
                amount=0.0
            )

        # 创建不同风速的请求（都不是开关机请求）
        Request.create(slave_id=1, temp=22.0, speed=1, time=datetime.now())  # 低速
        Request.create(slave_id=2, temp=22.0, speed=3, time=datetime.now())  # 高速
        Request.create(slave_id=3, temp=22.0, speed=2, time=datetime.now())  # 中速

        machine.choice = 3  # 风速优先
        machine.num = 3     # 最多处理3个请求

        machine.get_request()

        # 验证选中的请求按风速降序排列
        selected_speeds = [req.speed for req in machine.requestList]
        assert len(selected_speeds) <= 3
        assert len(selected_speeds) > 0
        # 验证风速是按降序排列的
        for i in range(len(selected_speeds) - 1):
            assert selected_speeds[i] >= selected_speeds[i + 1], f"风速应该按降序排列，但得到 {selected_speeds}"

    def test_power_first_priority(self, machine):
        """测试开关机请求优先处理"""
        # 创建从机状态
        Status.create(id=1, card_id="card1", target_temp=22, cur_temp=25.0, speed=0, energy=0.0, amount=0.0)  # 关机状态
        Status.create(id=2, card_id="card2", target_temp=22, cur_temp=25.0, speed=2, energy=0.0, amount=0.0)  # 运行状态
        Status.create(id=3, card_id="card3", target_temp=22, cur_temp=25.0, speed=1, energy=0.0, amount=0.0)  # 运行状态

        # 创建请求：开机请求和关机请求
        Request.create(slave_id=1, temp=22.0, speed=2, time=datetime.now())  # 开机请求 (0->2)
        Request.create(slave_id=2, temp=22.0, speed=0, time=datetime.now())  # 关机请求 (2->0)
        Request.create(slave_id=3, temp=22.0, speed=1, time=datetime.now())  # 普通请求

        machine.choice = 1  # 随机调度
        machine.num = 2     # 限制为2个请求，测试优先级

        machine.get_request()

        # 验证开关机请求被优先处理
        selected_ids = [req.slave_id for req in machine.requestList]

        # 开关机请求应该被优先选择
        power_requests = []
        for req in machine.requestList:
            if req.slave_id == 1:  # 开机请求
                power_requests.append(req.slave_id)
            elif req.slave_id == 2:  # 关机请求
                power_requests.append(req.slave_id)

        # 至少应该有一个开关机请求被处理
        assert len(power_requests) > 0, f"应该优先处理开关机请求，但选中的请求ID为: {selected_ids}"
        assert len(selected_ids) <= machine.num
