import os
import sys
import time

# Add src directory to the Python path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from models import Graph, Edge
from pathfinding import ShortestPath
from fare_calculator import calculate_estimated_time
from data_loader import load_subway_data, DATA_FILE_PATH


class TestPathfinding:

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

    def test_multiple_path_modes(self, setup_graph):
        """测试多种路径查询功能"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 选择需要换乘的站点对进行测试
        start_station = "天安门东"
        end_station = "中关村"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"测试站点 {start_station} 或 {end_station} 不存在")

        # 测试基础最短路径算法
        path_finder = ShortestPath(metro_graph, start_id)

        # 验证能找到路径
        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "应该能找到有效路径"

        # 获取路径信息
        path_ids, edges = path_finder.path_with_edges(end_id)

        # 验证路径的基本属性
        assert len(path_ids) >= 2, "路径应该包含至少起点和终点"
        assert path_ids[0] == start_id, "路径应该从起点开始"
        assert path_ids[-1] == end_id, "路径应该在终点结束"
        assert len(edges) == len(path_ids) - 1, "边的数量应该比站点数量少1"

        # 注意：由于当前实现只有基础最短路径算法，这里主要验证算法的正确性
        # 在实际实现中，应该有不同的路径查询模式
        print(f"找到路径：{' -> '.join([number_to_station[id] for id in path_ids])}")

    def test_path_preferences(self, setup_graph):
        """测试路径偏好设置功能"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 选择测试站点
        start_station = "天安门东"
        end_station = "西单"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"测试站点 {start_station} 或 {end_station} 不存在")

        # 测试基础路径查找
        path_finder = ShortestPath(metro_graph, start_id)

        # 验证能找到路径
        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "应该能找到有效路径"

        # 获取路径信息
        path_ids, edges = path_finder.path_with_edges(end_id)

        # 计算换乘次数
        transfer_count = 0
        previous_line = None
        for edge in edges:
            if previous_line and previous_line != edge.line:
                transfer_count += 1
            previous_line = edge.line

        # 验证路径约束（这里主要验证换乘次数是合理的）
        assert transfer_count <= 5, "换乘次数应该在合理范围内"

        print(f"路径换乘次数：{transfer_count}")

    def test_complex_transfer_handling(self, setup_graph):
        """测试换乘站特殊处理"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 选择包含复杂换乘站的路径
        start_station = "天安门东"
        end_station = "中关村"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"测试站点 {start_station} 或 {end_station} 不存在")

        path_finder = ShortestPath(metro_graph, start_id)

        # 验证能找到路径
        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "应该能找到有效路径"

        # 获取路径信息
        path_ids, edges = path_finder.path_with_edges(end_id)

        # 检查换乘站处理
        transfer_stations = []
        previous_line = None

        for i, edge in enumerate(edges):
            if previous_line and previous_line != edge.line:
                # 发现换乘点
                transfer_station_id = path_ids[i]
                transfer_station_name = number_to_station[transfer_station_id]
                transfer_stations.append(transfer_station_name)

                # 验证换乘站确实支持多条线路
                station_lines = metro_graph.station_lines.get(transfer_station_name, [])
                assert len(station_lines) > 1, f"换乘站 {transfer_station_name} 应该支持多条线路"

            previous_line = edge.line

        print(f"检测到换乘站：{transfer_stations}")

    def test_shortest_path(self, setup_graph):
        """测试最短路径算法验证"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 测试用例1：直达路径
        test_cases = [
            ("天安门东", "西单", 2142),  # 直达或短路径，预期距离
            ("天安门东", "中关村", 13771),  # 需要换乘的路径，预期距离
            ("西单", "东单", 3768)  # 另一个测试路径，预期距离
        ]

        successful_tests = 0

        for start_station, end_station, expected_distance in test_cases:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                print(f"跳过测试：{start_station} -> {end_station}（站点不存在）")
                continue

            from pathfinding import PathfindingConfig # Ensure PathfindingConfig is imported
            config = PathfindingConfig()
            config.mode = "shortest_distance" # Explicitly test shortest_distance mode
            path_finder = ShortestPath(metro_graph, start_id, config)

            if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                path_ids, edges = path_finder.path_with_edges(end_id)
                total_distance = sum(edge.weight for edge in edges)

                # 验证路径的基本属性
                assert len(path_ids) >= 2, f"路径 {start_station} -> {end_station} 应该包含至少起点和终点"
                assert path_ids[0] == start_id, f"路径应该从 {start_station} 开始"
                assert path_ids[-1] == end_id, f"路径应该在 {end_station} 结束"
                assert total_distance > 0, "路径总距离应该大于0"
                
                # 验证是否找到最短路径（通过距离）
                assert total_distance == expected_distance, f"路径 {start_station} -> {end_station} 的总距离不正确。预期: {expected_distance}米, 实际: {total_distance}米"

                successful_tests += 1
                print(f"✓ {start_station} -> {end_station}: {total_distance}米 (预期: {expected_distance}米)")
            else:
                print(f"✗ {start_station} -> {end_station}: 无法找到路径")

        # 至少要有2个成功的测试用例
        assert successful_tests >= 2, f"至少应该有2个成功的路径测试，实际成功：{successful_tests}"

    def test_time_estimation(self, setup_graph):
        """测试预计时间估算功能"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # 测试不同距离和换乘次数的时间估算
        test_cases = [
            ("天安门东", "西单", 3000, 0),  # 短距离，无换乘
            ("天安门东", "中关村", 15000, 2),  # 中距离，有换乘
        ]

        for start_station, end_station, expected_distance, expected_transfers in test_cases:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                continue

            path_finder = ShortestPath(metro_graph, start_id)

            if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                path_ids, edges = path_finder.path_with_edges(end_id)
                total_distance = sum(edge.weight for edge in edges)

                # 计算换乘次数
                transfer_count = 0
                previous_line = None
                for edge in edges:
                    if previous_line and previous_line != edge.line:
                        transfer_count += 1
                    previous_line = edge.line

                # 测试时间估算功能
                estimated_time = calculate_estimated_time(total_distance, transfer_count)

                # 验证时间估算的合理性
                assert estimated_time > 0, "预计时间应该大于0"

                # 基于经验的时间估算验证（每公里1-2分钟，每次换乘增加2-3分钟）
                min_expected_time = (total_distance / 1000) * 1 + transfer_count * 2
                max_expected_time = (total_distance / 1000) * 3 + transfer_count * 5

                assert min_expected_time <= estimated_time <= max_expected_time, \
                    f"时间估算 {estimated_time} 分钟应该在合理范围内 [{min_expected_time:.1f}, {max_expected_time:.1f}]"

                print(f"{start_station} -> {end_station}: {total_distance}米, {transfer_count}次换乘, 预计{estimated_time}分钟")

    def test_least_transfer_mode(self, setup_graph):
        """测试最少换乘模式"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "天安门东"
        end_station = "中关村" # This route typically involves transfers

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"测试站点 {start_station} 或 {end_station} 不存在")

        from pathfinding import PathfindingConfig # Import here to avoid circular dependency if not already imported
        config = PathfindingConfig()
        config.mode = "least_transfer"
        path_finder = ShortestPath(metro_graph, start_id, config)

        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "应该能找到有效路径"
        
        path_ids, edges = path_finder.path_with_edges(end_id)
        transfer_count = path_finder.get_transfer_count(end_id)

        # For "天安门东" to "中关村", the least transfers should be 1 (Line 1 to Line 4)
        # This assertion might need adjustment based on actual data and optimal path
        assert transfer_count == 1, f"最少换乘模式下，换乘次数应为1，实际为{transfer_count}"
        print(f"最少换乘模式：{start_station} -> {end_station}, 换乘次数: {transfer_count}")

    def test_comprehensive_mode(self, setup_graph):
        """测试综合最优模式"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "天安门东"
        end_station = "中关村"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"测试站点 {start_station} 或 {end_station} 不存在")

        from pathfinding import PathfindingConfig
        config = PathfindingConfig()
        config.mode = "comprehensive"
        path_finder = ShortestPath(metro_graph, start_id, config)

        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "应该能找到有效路径"
        
        path_ids, edges = path_finder.path_with_edges(end_id)
        transfer_count = path_finder.get_transfer_count(end_id)
        total_distance = sum(edge.weight for edge in edges)

        # Comprehensive mode should balance distance and transfers.
        # For "天安门东" to "中关村", it's likely 1 transfer, similar to least_transfer,
        # but the exact path might differ slightly if there are multiple 1-transfer options.
        # We can assert that it's not excessively high in transfers or distance.
        assert transfer_count <= 2, f"综合最优模式下，换乘次数不应超过2，实际为{transfer_count}"
        assert total_distance < 20000, f"综合最优模式下，总距离不应过长，实际为{total_distance}"
        print(f"综合最优模式：{start_station} -> {end_station}, 距离: {total_distance}, 换乘次数: {transfer_count}")

    def test_max_transfers_limit(self, setup_graph):
        """测试最大换乘次数限制"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "天安门东"
        end_station = "中关村" # This route requires transfers

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"测试站点 {start_station} 或 {end_station} 不存在")

        # Test with max_transfers = 0 (should find no path for this route)
        from pathfinding import PathfindingConfig
        config_zero_transfers = PathfindingConfig()
        config_zero_transfers.mode = "shortest_distance" # Can be any mode, limit applies
        config_zero_transfers.max_transfers = 0
        path_finder_zero = ShortestPath(metro_graph, start_id, config_zero_transfers)
        assert path_finder_zero.dist_to.get(end_id, float("inf")) == float("inf"), "max_transfers=0时，不应找到需要换乘的路径"
        print(f"max_transfers=0: {start_station} -> {end_station}, 结果: 无路径 (符合预期)")

        # Test with a reasonable max_transfers (e.g., 1)
        config_one_transfer = PathfindingConfig()
        config_one_transfer.mode = "shortest_distance"
        config_one_transfer.max_transfers = 1
        path_finder_one = ShortestPath(metro_graph, start_id, config_one_transfer)
        assert path_finder_one.dist_to.get(end_id, float("inf")) != float("inf"), "max_transfers=1时，应能找到路径"
        transfer_count_one = path_finder_one.get_transfer_count(end_id)
        assert transfer_count_one <= 1, f"max_transfers=1时，换乘次数应<=1，实际为{transfer_count_one}"
        print(f"max_transfers=1: {start_station} -> {end_station}, 换乘次数: {transfer_count_one} (符合预期)")

    def test_line_preference(self, setup_graph):
        """测试线路偏好设置功能"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "天安门东"
        end_station = "中关村" # Route that can use different lines for transfer

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"测试站点 {start_station} 或 {end_station} 不存在")

        # Test with a preferred line (e.g., "1号线")
        from pathfinding import PathfindingConfig
        config_pref_line = PathfindingConfig()
        config_pref_line.mode = "shortest_distance"
        config_pref_line.preferred_lines = ["1号线"] # Line 1 is part of the path
        path_finder_pref = ShortestPath(metro_graph, start_id, config_pref_line)

        assert path_finder_pref.dist_to.get(end_id, float("inf")) != float("inf"), "设置偏好线路后，应能找到路径"
        
        path_ids, edges = path_finder_pref.path_with_edges(end_id)
        # This assertion is tricky due to the current _is_line_acceptable implementation.
        # It only checks if the line is acceptable, not if it's strictly preferred.
        # For now, we can just ensure the path is found and doesn't use avoided lines (if any).
        # A more robust test would require a more robust _is_line_acceptable.
        
        # Check if any edge in the path uses the preferred line (if applicable)
        uses_preferred_line = any("1号线" in edge.line for edge in edges) # Assuming line is a string like "1号线"
        print(f"线路偏好 '1号线': {start_station} -> {end_station}, 路径是否包含1号线: {uses_preferred_line}")
        # For this specific route, it should contain Line 1.
        assert uses_preferred_line, "路径应包含偏好线路 '1号线'"

if __name__ == "__main__":
    pytest.main([__file__])
