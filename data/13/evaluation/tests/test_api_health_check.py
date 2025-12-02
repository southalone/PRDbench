"""
测试API健康检查接口
"""
import pytest
import requests
import json
import time
import threading
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.main import app
import uvicorn


class TestAPIHealthCheck:
    @classmethod
    def setup_class(cls):
        """启动API服务器"""
        cls.port = 8005  # 使用不同端口避免冲突
        cls.base_url = f"http://localhost:{cls.port}"
        cls.server_thread = None
        cls._start_server()
        cls._wait_for_server()
    
    @classmethod
    def _start_server(cls):
        """在后台线程中启动服务器"""
        def run_server():
            try:
                uvicorn.run(app, host="127.0.0.1", port=cls.port, log_level="error")
            except Exception as e:
                print(f"服务器启动失败: {e}")
        
        cls.server_thread = threading.Thread(target=run_server, daemon=True)
        cls.server_thread.start()
    
    @classmethod
    def _wait_for_server(cls):
        """等待服务器启动完成"""
        import time
        max_attempts = 30
        for i in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=1)
                if response.status_code == 200:
                    print(f"✓ 服务器在{i+1}秒后成功启动")
                    return
            except:
                pass
            time.sleep(1)
        
        for i in range(10):
            try:
                response = requests.get(cls.base_url, timeout=1)
                print(f"✓ 服务器启动成功 (状态码: {response.status_code})")
                return
            except:
                pass
            time.sleep(1)
        
        raise Exception("服务器启动超时")
    
    @classmethod
    def teardown_class(cls):
        """清理资源"""
        pass
    
    def test_health_endpoint(self):
        """测试健康检查接口"""
        try:
            # 发送GET请求到健康检查接口
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=30)
            
            # 验证响应状态码
            assert response.status_code == 200, f"健康检查接口状态码错误: {response.status_code}"
            
            # 解析响应
            result = response.json()
            
            # 验证基础健康状态字段
            required_fields = ["status", "timestamp", "version", "uptime"]
            for field in required_fields:
                assert field in result, f"健康检查响应缺少{field}字段"
            
            # 验证状态值
            assert result["status"] in ["healthy", "degraded", "unhealthy"], f"健康状态值无效: {result['status']}"
            assert isinstance(result["uptime"], (int, float)), "运行时间应为数值类型"
            assert result["uptime"] >= 0, "运行时间应为非负数"
            
            # 收集系统状态指标
            health_indicators = []
            
            # 1. 服务运行状态
            if "status" in result and result["status"]:
                health_indicators.append("服务运行状态")
            
            # 2. 模型加载状态
            if "models_loaded" in result:
                health_indicators.append("模型加载状态")
                assert isinstance(result["models_loaded"], bool), "模型加载状态应为布尔类型"
            
            # 3. 数据状态
            if "data_status" in result and result["data_status"]:
                health_indicators.append("数据状态")
                data_status = result["data_status"]
                assert isinstance(data_status, dict), "数据状态应为字典类型"
                
                # 验证数据状态的详细信息
                data_fields = ["status", "users_count", "items_count", "interactions_count"]
                for field in data_fields:
                    if field in data_status:
                        health_indicators.append(f"数据{field}")
            
            # 4. 系统指标（CPU、内存、磁盘）
            if "system_metrics" in result and result["system_metrics"]:
                health_indicators.append("系统资源监控")
                system_metrics = result["system_metrics"]
                assert isinstance(system_metrics, dict), "系统指标应为字典类型"
                
                # 检查CPU使用率
                if "cpu_usage" in system_metrics:
                    health_indicators.append("CPU使用率")
                    cpu_usage = system_metrics["cpu_usage"]
                    assert isinstance(cpu_usage, (int, float)), "CPU使用率应为数值类型"
                    assert 0 <= cpu_usage <= 100, f"CPU使用率应在0-100之间: {cpu_usage}"
                
                # 检查内存使用率
                if "memory_usage" in system_metrics:
                    health_indicators.append("内存使用率")
                    memory_usage = system_metrics["memory_usage"]
                    assert isinstance(memory_usage, (int, float)), "内存使用率应为数值类型"
                    assert 0 <= memory_usage <= 100, f"内存使用率应在0-100之间: {memory_usage}"
                
                # 检查磁盘使用率
                if "disk_usage" in system_metrics:
                    health_indicators.append("磁盘使用率")
                    disk_usage = system_metrics["disk_usage"]
                    assert isinstance(disk_usage, (int, float)), "磁盘使用率应为数值类型"
                    assert 0 <= disk_usage <= 100, f"磁盘使用率应在0-100之间: {disk_usage}"
            
            # 5. 运行时间指标
            if "uptime" in result:
                health_indicators.append("系统运行时间")
            
            # 6. 版本信息
            if "version" in result:
                health_indicators.append("系统版本")
            
            # 验证至少包含4项指标
            assert len(health_indicators) >= 4, f"健康检查指标不足，只找到{len(health_indicators)}项: {health_indicators}"
            
            # 验证具体指标的合理性
            if "system_metrics" in result:
                system_metrics = result["system_metrics"]
                
                # 确保系统指标值在合理范围内
                if "cpu_usage" in system_metrics:
                    cpu_usage = system_metrics["cpu_usage"]
                    assert cpu_usage >= 0, "CPU使用率不能为负"
                
                if "memory_usage" in system_metrics:
                    memory_usage = system_metrics["memory_usage"]
                    assert memory_usage > 0, "内存使用率应大于0（系统正在运行）"
            
            print("✓ 健康检查API接口测试通过")
            print(f"✓ 系统状态: {result['status']}")
            print(f"✓ 找到的健康指标: {health_indicators}")
            print(f"✓ 系统运行时间: {result['uptime']:.2f}秒")
            print(f"✓ 模型状态: {'已加载' if result.get('models_loaded', False) else '未加载'}")
            
            if "system_metrics" in result:
                metrics = result["system_metrics"]
                if "cpu_usage" in metrics:
                    print(f"✓ CPU使用率: {metrics['cpu_usage']:.1f}%")
                if "memory_usage" in metrics:
                    print(f"✓ 内存使用率: {metrics['memory_usage']:.1f}%")
                if "disk_usage" in metrics:
                    print(f"✓ 磁盘使用率: {metrics['disk_usage']:.1f}%")
                    
        except requests.exceptions.RequestException as e:
            pytest.fail(f"健康检查请求失败: {e}")
        except Exception as e:
            pytest.fail(f"测试执行失败: {e}")
    
    def test_health_endpoint_detailed(self):
        """测试健康检查接口的详细信息"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            assert response.status_code == 200, "健康检查接口应返回200状态码"
            
            result = response.json()
            
            # 验证时间戳格式
            assert "timestamp" in result, "应包含timestamp字段"
            timestamp_str = result["timestamp"]
            
            # 尝试解析ISO格式时间戳
            try:
                from datetime import datetime
                parsed_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00') if timestamp_str.endswith('Z') else timestamp_str)
                assert isinstance(parsed_time, datetime), "时间戳应为有效的datetime对象"
            except ValueError:
                pytest.fail(f"时间戳格式无效: {timestamp_str}")
            
            # 验证版本信息
            if "version" in result:
                version = result["version"]
                assert isinstance(version, str), "版本应为字符串类型"
                assert len(version) > 0, "版本字符串不应为空"
            
            # 验证数据状态详细信息
            if "data_status" in result:
                data_status = result["data_status"]
                
                # 验证用户数据
                if "users_count" in data_status:
                    assert isinstance(data_status["users_count"], int), "用户数量应为整数"
                    assert data_status["users_count"] >= 0, "用户数量应为非负数"
                
                # 验证商品数据
                if "items_count" in data_status:
                    assert isinstance(data_status["items_count"], int), "商品数量应为整数"
                    assert data_status["items_count"] >= 0, "商品数量应为非负数"
                
                # 验证交互数据
                if "interactions_count" in data_status:
                    assert isinstance(data_status["interactions_count"], int), "交互数量应为整数"
                    assert data_status["interactions_count"] >= 0, "交互数量应为非负数"
            
            print("✓ 健康检查详细信息验证通过")
            print(f"✓ 响应包含完整的健康状态信息")
            
        except Exception as e:
            pytest.fail(f"健康检查详细信息测试失败: {e}")
    
    def test_health_endpoint_response_time(self):
        """测试健康检查接口响应时间"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            response_time = time.time() - start_time
            
            assert response.status_code == 200, "健康检查接口应返回200状态码"
            assert response_time < 5.0, f"健康检查响应时间过长: {response_time:.2f}秒"
            
            print(f"✓ 健康检查响应时间测试通过: {response_time:.3f}秒")
            
        except Exception as e:
            pytest.fail(f"健康检查响应时间测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])