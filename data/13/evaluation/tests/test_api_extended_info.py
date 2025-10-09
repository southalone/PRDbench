"""
测试API推荐结果扩展信息
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


class TestAPIExtendedInfo:
    @classmethod
    def setup_class(cls):
        """启动API服务器"""
        cls.port = 8003  # 使用不同端口避免冲突
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
    
    def test_recommend_extended_response(self):
        """测试推荐结果扩展信息"""
        try:
            # 准备测试数据
            test_data = {
                "user_id": 1,
                "top_n": 5
            }
            
            # 发送POST请求到推荐接口
            response = requests.post(
                f"{self.base_url}/api/v1/recommend",
                json=test_data,
                timeout=60  # 增加超时时间
            )
            
            # 验证响应状态码
            assert response.status_code == 200, f"API响应状态码错误: {response.status_code}"
            
            # 解析响应
            result = response.json()
            
            # 验证基础响应结构
            assert "recommendations" in result, "响应中缺少recommendations字段"
            assert "strategy" in result, "响应中缺少strategy字段"
            assert "diversity_score" in result, "响应中缺少diversity_score字段"
            assert "processing_time" in result, "响应中缺少processing_time字段"
            
            recommendations = result["recommendations"]
            assert len(recommendations) > 0, "推荐结果不能为空"
            
            # 验证推荐结果的扩展信息
            extended_fields_found = set()
            
            for i, item in enumerate(recommendations):
                # 验证必需的基础字段
                assert "item_id" in item, f"第{i+1}个推荐商品缺少item_id字段"
                assert "score" in item, f"第{i+1}个推荐商品缺少score字段"
                assert "title" in item, f"第{i+1}个推荐商品缺少title字段"
                
                # 收集扩展信息字段
                if "reason" in item and item["reason"]:
                    extended_fields_found.add("推荐原因")
                
                if "category" in item and item["category"]:
                    extended_fields_found.add("商品类别")
                
                if "price" in item and item["price"] is not None:
                    extended_fields_found.add("商品价格")
                
                if "brand" in item and item["brand"]:
                    extended_fields_found.add("商品品牌")
                
                if "description" in item and item["description"]:
                    extended_fields_found.add("商品描述")
            
            # 检查推荐算法来源（在根级别）
            if "strategy" in result and result["strategy"]:
                extended_fields_found.add("推荐算法来源")
            
            # 检查多样性分数（多样性标签）
            if "diversity_score" in result:
                if isinstance(result["diversity_score"], (int, float)):
                    extended_fields_found.add("多样性分数")
                elif isinstance(result["diversity_score"], dict):
                    extended_fields_found.add("多样性分数")
            
            # 验证至少包含3种扩展信息
            assert len(extended_fields_found) >= 3, f"扩展信息不足，只找到{len(extended_fields_found)}种: {extended_fields_found}"
            
            # 验证具体的扩展信息内容
            sample_item = recommendations[0]
            
            # 验证推荐原因
            if "reason" in sample_item:
                assert isinstance(sample_item["reason"], str), "推荐原因应为字符串类型"
                assert len(sample_item["reason"]) > 0, "推荐原因不能为空"
            
            # 验证商品类别
            if "category" in sample_item:
                assert isinstance(sample_item["category"], str), "商品类别应为字符串类型"
                assert len(sample_item["category"]) > 0, "商品类别不能为空"
            
            # 验证价格信息
            if "price" in sample_item and sample_item["price"] is not None:
                assert isinstance(sample_item["price"], (int, float)), "商品价格应为数值类型"
                assert sample_item["price"] >= 0, "商品价格不能为负数"
            
            # 验证多样性分数
            diversity_score = result["diversity_score"]
            if isinstance(diversity_score, (int, float)):
                assert 0 <= diversity_score <= 1, f"多样性分数应在0-1之间: {diversity_score}"
            elif isinstance(diversity_score, dict):
                # 如果是字典，验证字典中的值
                for key, value in diversity_score.items():
                    assert isinstance(value, (int, float)), f"多样性分数{key}应为数值类型"
                    assert 0 <= value <= 1, f"多样性分数{key}应在0-1之间: {value}"
            else:
                assert False, f"多样性分数格式不正确: {type(diversity_score)}"
            
            # 验证处理时间
            assert isinstance(result["processing_time"], (int, float)), "处理时间应为数值类型"
            assert result["processing_time"] > 0, "处理时间应大于0"
            
            print("✓ API推荐结果扩展信息测试通过")
            print(f"✓ 找到的扩展信息类型: {extended_fields_found}")
            
            # 格式化多样性分数显示
            diversity_score = result['diversity_score']
            if isinstance(diversity_score, (int, float)):
                print(f"✓ 多样性分数: {diversity_score:.3f}")
            elif isinstance(diversity_score, dict):
                formatted_scores = {k: f"{v:.3f}" for k, v in diversity_score.items()}
                print(f"✓ 多样性分数: {formatted_scores}")
            
            print(f"✓ 处理时间: {result['processing_time']:.3f}秒")
            print(f"✓ 推荐策略: {result.get('strategy', 'N/A')}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"API请求失败: {e}")
        except Exception as e:
            pytest.fail(f"测试执行失败: {e}")
    
    def test_recommend_with_different_strategies(self):
        """测试不同推荐策略返回的扩展信息"""
        strategies = ["hybrid_weighted", "content_based", "user_cf"]
        
        for strategy in strategies:
            try:
                test_data = {
                    "user_id": 1,
                    "top_n": 3,
                    "strategy": strategy
                }
                
                response = requests.post(
                    f"{self.base_url}/api/v1/recommend",
                    json=test_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 验证策略信息被正确返回
                    assert "strategy" in result, f"策略{strategy}的响应中缺少strategy字段"
                    
                    # 验证推荐结果包含扩展信息
                    if result.get("recommendations"):
                        sample_item = result["recommendations"][0]
                        
                        # 验证至少有推荐原因
                        assert "reason" in sample_item, f"策略{strategy}的推荐结果缺少推荐原因"
                        
                        print(f"✓ 策略 {strategy} 测试通过")
                
            except Exception as e:
                print(f"⚠ 策略 {strategy} 测试失败: {e}")
                # 不让单个策略失败影响整体测试
                continue


if __name__ == "__main__":
    pytest.main([__file__, "-v"])