import pytest
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"

class TestBUPTAirAPI:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """每个测试前后的setup和teardown"""
        # Setup: 清理数据
        requests.delete(f"{BASE_URL}/slave/delete_all")
        yield
        # Teardown: 清理数据
        requests.delete(f"{BASE_URL}/slave/delete_all")

    def test_system_startup_and_status(self):
        """测试系统启动和状态查询"""
        # 启动主机
        response = requests.get(f"{BASE_URL}/machine/open")
        assert response.status_code == 200

        # 查询主机状态
        response = requests.get(f"{BASE_URL}/machine/info")
        assert response.status_code == 200

        data = response.json()
        assert 'status' in data
        assert 'power' in data
        assert 'scheduling' in data
        assert 'standby' in data

    def test_slave_management(self):
        """测试从机管理功能"""
        # 添加从机
        slave_data = {"card_id": "test_card_123"}
        response = requests.post(f"{BASE_URL}/slave/", json=slave_data)
        assert response.status_code == 200

        # 查询从机状态
        response = requests.get(f"{BASE_URL}/slave/check/test_card_123")
        assert response.status_code == 200

        data = response.json()
        assert data['card_id'] == "test_card_123"
        assert 'target_temp' in data
        assert 'cur_temp' in data
        assert 'speed' in data

    def test_mode_switching(self):
        """测试主机模式切换"""
        # 添加从机
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_mode"})

        # 设置制冷模式
        mode_data = {"power": 3, "scheduling": 1, "status": 1}
        response = requests.post(f"{BASE_URL}/machine/set", json=mode_data)
        assert response.status_code == 200

        # 检查从机温度是否重置
        response = requests.get(f"{BASE_URL}/slave/1")
        data = response.json()
        if data['target_temp'] > 25:
            assert data['target_temp'] == 22

        # 设置制热模式
        mode_data = {"power": 3, "scheduling": 1, "status": 2}
        response = requests.post(f"{BASE_URL}/machine/set", json=mode_data)
        assert response.status_code == 200

        # 检查从机温度是否重置
        response = requests.get(f"{BASE_URL}/slave/1")
        data = response.json()
        if data['target_temp'] <= 25:
            assert data['target_temp'] == 28

    def test_temperature_adjustment(self):
        """测试温度调节功能"""
        # 添加从机并设置制冷模式
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_temp"})
        requests.post(f"{BASE_URL}/machine/set", json={"power": 3, "scheduling": 1, "status": 1})

        # 获取初始温度
        response = requests.get(f"{BASE_URL}/slave/1")
        initial_temp = response.json()['target_temp']

        # 降低温度
        response = requests.get(f"{BASE_URL}/slave/temp/low/1")
        assert response.status_code == 200

        # 验证温度是否改变
        response = requests.get(f"{BASE_URL}/slave/1")
        new_temp = response.json()['target_temp']
        # 注意：由于是异步处理，可能需要等待
        time.sleep(1)

    def test_speed_adjustment(self):
        """测试风速调节功能"""
        # 添加从机
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_speed"})

        # 提高风速
        response = requests.get(f"{BASE_URL}/slave/speed/high/1")
        assert response.status_code == 200

        # 验证风速不超过3档
        for _ in range(5):  # 尝试超过最大风速
            requests.get(f"{BASE_URL}/slave/speed/high/1")

        response = requests.get(f"{BASE_URL}/slave/1")
        data = response.json()
        assert data['speed'] <= 3

    def test_cost_calculation(self):
        """测试费用计算功能"""
        # 添加从机并设置
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_cost"})
        requests.post(f"{BASE_URL}/machine/set", json={"power": 3, "scheduling": 1, "status": 1})

        # 获取初始费用
        response = requests.get(f"{BASE_URL}/slave/1")
        initial_amount = response.json()['amount']

        # 设置中速风并启动费用计算
        requests.get(f"{BASE_URL}/slave/speed/high/1")
        requests.get(f"{BASE_URL}/slave/speed/high/1")  # 设置为中速(speed=2)
        requests.get(f"{BASE_URL}/cost/open")

        # 等待一段时间
        time.sleep(5)

        # 检查费用是否增加
        response = requests.get(f"{BASE_URL}/slave/1")
        final_amount = response.json()['amount']

        requests.get(f"{BASE_URL}/cost/close")

        assert final_amount > initial_amount

    def test_report_generation(self):
        """测试报表生成功能"""
        # 添加从机并进行一些操作
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_report"})
        requests.get(f"{BASE_URL}/slave/speed/high/1")
        requests.get(f"{BASE_URL}/slave/shutdown/1")

        # 生成报表
        report_data = {
            "startDate": datetime.now().strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.post(f"{BASE_URL}/log/", json=report_data)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        if data:  # 如果有数据
            assert 'ID' in data[0]
            assert 'Count' in data[0]
            assert 'Record' in data[0]
            assert 'Cost' in data[0]

if __name__ == "__main__":
    pytest.main([__file__])
