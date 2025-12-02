"""
测试API基础推荐接口
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
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from api.main import app
    import uvicorn
except ImportError as e:
    print(f"导入失败: {e}")
    print(f"当前Python路径: {sys.path[:3]}")
    raise


class TestAPIBasicRecommend:
    @classmethod
    def setup_class(cls):
        """启动API服务器"""
        cls.port = 8002  # 使用不同端口避免冲突
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
        max_attempts = 30  # 最多等待30秒
        for i in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=1)
                if response.status_code == 200:
                    print(f"✓ 服务器在{i+1}秒后成功启动")
                    return
            except:
                pass
            time.sleep(1)
        
        # 如果健康检查失败，尝试直接测试根路径
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
        # 服务器线程会在测试结束时自动终止（daemon=True）
        pass
    
    def test_recommend_endpoint(self):
        """测试基础推荐接口"""
        try:
            # 准备测试数据
            test_data = {
                "user_id": 1,  # 使用整数类型的user_id
                "top_n": 10
            }
            
            # 发送POST请求到推荐接口
            response = requests.post(
                f"{self.base_url}/api/v1/recommend",
                json=test_data,
                timeout=60  # 增加超时时间到60秒，因为推荐系统需要训练时间
            )
            
            # 验证响应状态码
            assert response.status_code == 200, f"API响应状态码错误: {response.status_code}"
            
            # 验证响应是JSON格式
            try:
                result = response.json()
            except json.JSONDecodeError:
                pytest.fail("API响应不是有效的JSON格式")
            
            # 验证响应结构
            assert "recommendations" in result, "响应中缺少recommendations字段"
            recommendations = result["recommendations"]
            
            # 验证推荐数量
            assert len(recommendations) == 10, f"推荐商品数量错误，期望10个，实际{len(recommendations)}个"
            
            # 验证每个推荐商品的字段
            required_fields = ["item_id", "score", "title"]
            for i, item in enumerate(recommendations):
                for field in required_fields:
                    assert field in item, f"第{i+1}个推荐商品缺少{field}字段"
                
                # 验证字段类型和值
                assert isinstance(item["item_id"], str), f"item_id应为字符串类型"
                assert isinstance(item["score"], (int, float)), f"score应为数值类型"
                assert isinstance(item["title"], str), f"title应为字符串类型"
                assert item["score"] >= 0, f"推荐分数应为非负数，实际值: {item['score']}"
            
            # 验证推荐结果按分数降序排列
            scores = [item["score"] for item in recommendations]
            assert scores == sorted(scores, reverse=True), "推荐结果应按分数降序排列"
            
            print("✓ API基础推荐接口测试通过")
            print(f"✓ 成功返回{len(recommendations)}个推荐商品")
            print(f"✓ 每个商品包含必需字段: {required_fields}")
            print(f"✓ 推荐分数范围: {min(scores):.3f} - {max(scores):.3f}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"API请求失败: {e}")
        except Exception as e:
            pytest.fail(f"测试执行失败: {e}")
    
    def test_api_health_check(self):
        """测试API健康检查接口"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            assert response.status_code == 200, "健康检查接口应返回200状态码"
            
            result = response.json()
            assert "status" in result, "健康检查响应应包含status字段"
            assert result["status"] == "healthy", "服务状态应为healthy"
            
            print("✓ API健康检查接口正常")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"健康检查请求失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])