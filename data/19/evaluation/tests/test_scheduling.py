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

    @pytest.fixture
    def setup_db(self):
        """设置测试数据库"""
        db.create_tables([Request, Status], safe=True)
        yield
        # 清理
        Request.delete().execute()
        Status.delete().execute()

    @pytest.fixture
    def machine(self):
        """创建主机实例"""
        return mainMachine()

    def test_random_scheduling(self, setup_db, machine):
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

        # 多次运行随机调度，验证结果的随机性
        results = []
        for _ in range(10):
            # 重新创建请求（因为get_request会删除处理的请求）
            Request.delete().execute()
            for i in range(5):
                Request.create(
                    slave_id=i+1,
                    temp=22.0,
                    speed=1,
                    time=datetime.now()
                )

            machine.get_request()
            # 记录被选中的请求ID
            selected_ids = [req.slave_id for req in machine.requestList]
            results.append(tuple(sorted(selected_ids)))

        # 验证结果有一定的随机性（不是每次都完全相同）
        unique_results = set(results)
        assert len(unique_results) > 1, "随机调度应该产生不同的结果"

    def test_speed_priority_scheduling(self, setup_db, machine):
        """测试风速优先调度算法"""
        # 创建不同风速的请求
        Request.create(slave_id=1, temp=22.0, speed=1, time=datetime.now())  # 低速
        Request.create(slave_id=2, temp=22.0, speed=3, time=datetime.now())  # 高速
        Request.create(slave_id=3, temp=22.0, speed=2, time=datetime.now())  # 中速

        machine.choice = 3  # 风速优先
        machine.num = 3     # 最多处理3个请求

        machine.get_request()

        # 验证选中的请求按风速降序排列
        selected_speeds = [req.speed for req in machine.requestList]
        assert len(selected_speeds) <= 3
        assert selected_speeds == sorted(selected_speeds, reverse=True)

    def test_power_first_priority(self, setup_db, machine):
        """测试开关机请求优先处理"""
        # 创建从机状态
        Status.create(id=1, card_id="card1", target_temp=22, cur_temp=25.0, speed=0, energy=0.0, amount=0.0)  # 关机状态
        Status.create(id=2, card_id="card2", target_temp=22, cur_temp=25.0, speed=2, energy=0.0, amount=0.0)  # 运行状态

        # 创建请求：开机请求和关机请求
        Request.create(slave_id=1, temp=22.0, speed=2, time=datetime.now())  # 开机请求 (0->2)
        Request.create(slave_id=2, temp=22.0, speed=0, time=datetime.now())  # 关机请求 (2->0)
        Request.create(slave_id=3, temp=22.0, speed=1, time=datetime.now())  # 普通请求

        machine.choice = 1  # 随机调度
        machine.num = 2     # 最多处理2个请求

        machine.get_request()

        # 验证开关机请求被优先处理
        selected_ids = [req.slave_id for req in machine.requestList]
        assert 1 in selected_ids  # 开机请求
        assert 2 in selected_ids  # 关机请求
        assert len(selected_ids) == 2
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.machine import mainMachine
from orm.orm import Request, Status, db
from datetime import datetime
import random

class TestSchedulingAlgorithms:

    @pytest.fixture
    def setup_db(self):
        """设置测试数据库"""
        db.create_tables([Request, Status], safe=True)
        yield
        # 清理
        Request.delete().execute()
        Status.delete().execute()

    @pytest.fixture
    def machine(self):
        """创建主机实例"""
        return mainMachine()

    def test_random_scheduling(self, setup_db, machine):
        """测试随机调度算法"""
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

        # 多次运行随机调度，验证结果的随机性
        results = []
        for _ in range(10):
            # 重新创建请求（因为get_request会删除处理的请求）
            Request.delete().execute()
            for i in range(5):
                Request.create(
                    slave_id=i+1,
                    temp=22.0,
                    speed=1,
                    time=datetime.now()
                )

            machine.get_request()
            # 记录被选中的请求ID
            selected_ids = [req.slave_id for req in machine.requestList]
            results.append(tuple(sorted(selected_ids)))

        # 验证结果有一定的随机性（不是每次都完全相同）
        unique_results = set(results)
        assert len(unique_results) > 1, "随机调度应该产生不同的结果"

    def test_speed_priority_scheduling(self, setup_db, machine):
        """测试风速优先调度算法"""
        # 创建不同风速的请求
        Request.create(slave_id=1, temp=22.0, speed=1, time=datetime.now())  # 低速
        Request.create(slave_id=2, temp=22.0, speed=3, time=datetime.now())  # 高速
        Request.create(slave_id=3, temp=22.0, speed=2, time=datetime.now())  # 中速

        machine.choice = 3  # 风速优先
        machine.num = 3     # 最多处理3个请求

        machine.get_request()

        # 验证选中的请求按风速降序排列
        selected_speeds = [req.speed for req in machine.requestList]
        assert len(selected_speeds) <= 3
        assert selected_speeds == sorted(selected_speeds, reverse=True)

    def test_power_first_priority(self, setup_db, machine):
        """测试开关机请求优先处理"""
        # 创建从机状态
        Status.create(id=1, card_id="card1", target_temp=22, cur_temp=25.0, speed=0, energy=0.0, amount=0.0)  # 关机状态
        Status.create(id=2, card_id="card2", target_temp=22, cur_temp=25.0, speed=2, energy=0.0, amount=0.0)  # 运行状态

        # 创建请求：开机请求和关机请求
        Request.create(slave_id=1, temp=22.0, speed=2, time=datetime.now())  # 开机请求 (0->2)
        Request.create(slave_id=2, temp=22.0, speed=0, time=datetime.now())  # 关机请求 (2->0)
        Request.create(slave_id=3, temp=22.0, speed=1, time=datetime.now())  # 普通请求

        machine.choice = 1  # 随机调度
        machine.num = 2     # 最多处理2个请求

        machine.get_request()

        # 验证开关机请求被优先处理
        selected_ids = [req.slave_id for req in machine.requestList]
        assert 1 in selected_ids  # 开机请求
        assert 2 in selected_ids  # 关机请求
        assert len(selected_ids) == 2
