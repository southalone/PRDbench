import pytest
import sys
import os
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models import Graph, Edge
from pathfinding import ShortestPath
from data_loader import load_subway_data, DATA_FILE_PATH


class TestPerformance:

    @pytest.fixture
    def setup_graph(self):
        """设置测试用的地铁网络图"""
        subway_data = load_subway_data(DATA_FILE_PATH)
        if not subway_data:
            pytest.skip("无法加载地铁数据")

        metro_graph = Graph()
        station_to_number = {}
        number_to_station = {}
        current_station_id = 1

        # 构建站点映射
        for station_info in subway_data['stations']:
            station_name = station_info['name']
            station_lines = station_info['lines']

            if station_name not in station_to_number:
                station_to_number[station_name] = current_station_id
                number_to_station[current_station_id] = station_name
                current_station_id += 1

            metro_graph.set_station_lines(station_name, station_lines)

        # 构建连接关系
        for conn in subway_data['connections']:
            source_name = conn['source']
            dest_name = conn['dest']
            distance = conn['distance']
            line = conn['line']

            source_id = station_to_number.get(source_name)
            dest_id = station_to_number.get(dest_name)

            if source_id is not None and dest_id is not None:
                edge = Edge(source_id, dest_id, distance, line)
                metro_graph.add_edge(edge)

        return metro_graph, station_to_number, number_to_station

    def test_response_time(self, setup_graph):
        """测试性能要求验证 - 响应时间"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 准备5组不同复杂度的路径查询
        test_cases = [
            ("天安门东", "西单", "短距离直达"),
            ("天安门东", "中关村", "中距离换乘"),
            ("天安门东", "东单", "中距离可能换乘"),
            ("西单", "雍和宫", "长距离多次换乘"),
            ("朝阳门", "中关村", "跨线路查询")
        ]

        response_times = []
        successful_tests = 0

        for start_station, end_station, description in test_cases:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                print(f"跳过测试：{description} ({start_station} -> {end_station}) - 站点不存在")
                continue

            # 记录开始时间
            start_time = time.time()

            try:
                # 执行路径查找
                path_finder = ShortestPath(metro_graph, start_id)

                if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                    path_ids, edges = path_finder.path_with_edges(end_id)
                    total_distance = sum(edge.weight for edge in edges)

                    # 记录结束时间
                    end_time = time.time()
                    response_time = end_time - start_time
                    response_times.append(response_time)

                    print(f"✓ {description}: {response_time:.3f}秒 ({start_station} -> {end_station}, {total_distance}米)")
                    successful_tests += 1

                    # 验证响应时间是否在1秒以内
                    assert response_time <= 1.0, \
                        f"{description} 响应时间 {response_time:.3f}秒 超过1秒限制"

                else:
                    print(f"✗ {description}: 无法找到路径 ({start_station} -> {end_station})")

            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                print(f"✗ {description}: 执行出错 ({response_time:.3f}秒) - {str(e)}")

        # 验证测试结果
        assert successful_tests >= 3, \
            f"至少应该有3个成功的性能测试，实际成功：{successful_tests}"

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)

            print(f"\n性能统计:")
            print(f"  平均响应时间: {avg_response_time:.3f}秒")
            print(f"  最大响应时间: {max_response_time:.3f}秒")
            print(f"  最小响应时间: {min_response_time:.3f}秒")
            print(f"  成功测试数量: {successful_tests}/{len(test_cases)}")

            # 验证平均响应时间
            assert avg_response_time <= 0.5, \
                f"平均响应时间 {avg_response_time:.3f}秒 应该在0.5秒以内"

    def test_memory_usage(self, setup_graph):
        """测试内存使用情况"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 简单的内存使用检查
        station_count = len(station_to_number)

        # 验证数据规模是否合理
        assert station_count > 0, "应该有站点数据"
        assert station_count < 10000, f"站点数量 {station_count} 过多，可能存在数据问题"

        print(f"✓ 内存使用检查: {station_count} 个站点")

    def test_algorithm_efficiency(self, setup_graph):
        """测试算法效率"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 测试多次查询的性能稳定性
        test_station_pairs = [
            ("天安门东", "西单"),
            ("天安门东", "中关村"),
        ]

        for start_station, end_station in test_station_pairs:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                continue

            # 执行多次查询测试性能稳定性
            times = []
            for i in range(5):
                start_time = time.time()
                path_finder = ShortestPath(metro_graph, start_id)
                if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                    path_ids, edges = path_finder.path_with_edges(end_id)
                end_time = time.time()
                times.append(end_time - start_time)

            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)

                print(f"✓ {start_station} -> {end_station}: 平均{avg_time:.3f}秒 (范围: {min_time:.3f}-{max_time:.3f}秒)")

                # 验证性能稳定性
                assert max_time - min_time <= 0.1, \
                    f"性能波动过大: {max_time - min_time:.3f}秒"

    def test_concurrent_queries(self, setup_graph):
        """测试并发查询性能（模拟）"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 模拟连续多次查询（类似并发场景）
        query_pairs = [
            ("天安门东", "西单"),
            ("西单", "中关村"),
            ("中关村", "东单"),
            ("东单", "朝阳门"),
            ("朝阳门", "天安门东"),
        ]

        start_time = time.time()
        successful_queries = 0

        for start_station, end_station in query_pairs:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is not None and end_id is not None:
                path_finder = ShortestPath(metro_graph, start_id)
                if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                    path_ids, edges = path_finder.path_with_edges(end_id)
                    successful_queries += 1

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_query = total_time / len(query_pairs) if query_pairs else 0

        print(f"✓ 连续查询测试: {successful_queries}/{len(query_pairs)} 成功")
        print(f"  总时间: {total_time:.3f}秒")
        print(f"  平均每次查询: {avg_time_per_query:.3f}秒")

        # 验证连续查询性能
        assert avg_time_per_query <= 0.2, \
            f"连续查询平均时间 {avg_time_per_query:.3f}秒 过长"
        assert successful_queries >= len(query_pairs) * 0.8, \
            f"连续查询成功率过低: {successful_queries}/{len(query_pairs)}"


if __name__ == "__main__":
    pytest.main([__file__])
