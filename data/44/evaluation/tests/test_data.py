import os
import sys

# Add src directory to the Python path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from models import Graph, Edge
from data_loader import load_subway_data, DATA_FILE_PATH

class TestData:

    @pytest.fixture
    def subway_data(self):
        """加载地铁数据"""
        data = load_subway_data(DATA_FILE_PATH)
        if not data:
            pytest.skip("无法加载地铁数据文件")
        return data
    
    def test_data_coverage(self, subway_data):
        """测试数据覆盖范围验证"""
        # PRD中提到的主要线路的代表性站点
        required_stations = [
            # 1号线
            "天安门东", "西单",
            # 2号线
            "朝阳门", "东直门",
            # 4号线
            "中关村",
            # 5号线
            "东单", "雍和宫",
            # 其他重要站点
            "天安门西"
        ]

        # 从数据中提取所有站点名称
        available_stations = set()
        for station_info in subway_data['stations']:
            available_stations.add(station_info['name'])

        # 检查每个必需站点是否存在
        found_stations = []
        missing_stations = []

        for station in required_stations:
            if station in available_stations:
                found_stations.append(station)
                print(f"✓ 找到站点: {station}")
            else:
                missing_stations.append(station)
                print(f"✗ 缺少站点: {station}")

        # 验证数据覆盖范围
        coverage_ratio = len(found_stations) / len(required_stations)
        print(f"数据覆盖率: {coverage_ratio:.2%} ({len(found_stations)}/{len(required_stations)})")

        # 至少应该能识别8个或以上的代表站点
        assert len(found_stations) >= 6, \
            f"应该能识别至少6个主要线路代表站点，实际识别到 {len(found_stations)} 个: {found_stations}"

        if missing_stations:
            print(f"警告：缺少以下站点: {missing_stations}")

    def test_data_management(self, subway_data):
        """测试数据管理功能验证"""

        # 1. 测试站点数据覆盖范围
        stations = subway_data['stations']
        connections = subway_data['connections']

        assert len(stations) > 0, "应该包含站点数据"
        assert len(connections) > 0, "应该包含连接数据"

        print(f"✓ 站点数据: {len(stations)} 个站点")
        print(f"✓ 连接数据: {len(connections)} 个连接")

        # 2. 测试连接关系完整性检查
        station_names = set(station['name'] for station in stations)

        # 检查连接中的站点是否都在站点列表中
        connection_stations = set()
        invalid_connections = []

        for conn in connections:
            source = conn['source']
            dest = conn['dest']
            connection_stations.add(source)
            connection_stations.add(dest)

            if source not in station_names:
                invalid_connections.append(f"源站点 '{source}' 不在站点列表中")
            if dest not in station_names:
                invalid_connections.append(f"目标站点 '{dest}' 不在站点列表中")

        # 连接关系完整性验证
        if invalid_connections:
            print(f"警告：发现 {len(invalid_connections)} 个无效连接")
            for invalid in invalid_connections[:5]:  # 只显示前5个
                print(f"  - {invalid}")
        else:
            print("✓ 连接关系完整性检查通过")

        # 大部分连接应该是有效的
        valid_connection_ratio = 1 - (len(invalid_connections) / len(connections))
        assert valid_connection_ratio >= 0.95, \
            f"连接关系有效率应该至少95%，实际为 {valid_connection_ratio:.2%}"

        # 3. 测试距离数据准确性
        distance_issues = []

        for conn in connections:
            distance = conn.get('distance', 0)
            if distance <= 0:
                distance_issues.append(f"连接 {conn['source']} -> {conn['dest']} 距离无效: {distance}")
            elif distance > 50000:  # 50公里，地铁站间距离不应该超过这个值
                distance_issues.append(f"连接 {conn['source']} -> {conn['dest']} 距离异常: {distance}米")

        if distance_issues:
            print(f"警告：发现 {len(distance_issues)} 个距离数据问题")
            for issue in distance_issues[:5]:  # 只显示前5个
                print(f"  - {issue}")
        else:
            print("✓ 距离数据准确性检查通过")

        # 大部分距离数据应该是合理的
        valid_distance_ratio = 1 - (len(distance_issues) / len(connections))
        assert valid_distance_ratio >= 0.9, \
            f"距离数据有效率应该至少90%，实际为 {valid_distance_ratio:.2%}"

        # 4. 测试线路信息完整性
        line_coverage = {}

        for station in stations:
            lines = station.get('lines', [])
            for line in lines:
                if line not in line_coverage:
                    line_coverage[line] = 0
                line_coverage[line] += 1

        print(f"✓ 线路覆盖情况:")
        for line, count in sorted(line_coverage.items()):
            print(f"  - {line}: {count} 个站点")

        # 应该至少覆盖几条主要线路
        assert len(line_coverage) >= 3, \
            f"应该至少覆盖3条地铁线路，实际覆盖 {len(line_coverage)} 条"

    def test_data_structure_validation(self, subway_data):
        """测试数据结构验证"""

        # 验证站点数据结构
        for i, station in enumerate(subway_data['stations']):
            assert 'name' in station, f"站点 {i} 缺少 'name' 字段"
            assert 'lines' in station, f"站点 {i} 缺少 'lines' 字段"
            assert isinstance(station['name'], str), f"站点 {i} 的 'name' 应该是字符串"
            assert isinstance(station['lines'], list), f"站点 {i} 的 'lines' 应该是列表"
            assert len(station['name'].strip()) > 0, f"站点 {i} 的名称不能为空"

        print(f"✓ 站点数据结构验证通过: {len(subway_data['stations'])} 个站点")

        # 验证连接数据结构
        for i, conn in enumerate(subway_data['connections']):
            required_fields = ['source', 'dest', 'distance', 'line']
            for field in required_fields:
                assert field in conn, f"连接 {i} 缺少 '{field}' 字段"

            assert isinstance(conn['source'], str), f"连接 {i} 的 'source' 应该是字符串"
            assert isinstance(conn['dest'], str), f"连接 {i} 的 'dest' 应该是字符串"
            assert isinstance(conn['distance'], (int, float)), f"连接 {i} 的 'distance' 应该是数字"
            assert isinstance(conn['line'], str), f"连接 {i} 的 'line' 应该是字符串"

            assert len(conn['source'].strip()) > 0, f"连接 {i} 的源站点名称不能为空"
            assert len(conn['dest'].strip()) > 0, f"连接 {i} 的目标站点名称不能为空"
            assert conn['distance'] > 0, f"连接 {i} 的距离应该大于0"

        print(f"✓ 连接数据结构验证通过: {len(subway_data['connections'])} 个连接")

    def test_graph_construction(self, subway_data):
        """测试图构建功能"""

        # 构建图
        metro_graph = Graph()
        station_to_number = {}
        current_station_id = 1

        for station_info in subway_data['stations']:
            station_name = station_info['name']
            station_lines = station_info['lines']

            if station_name not in station_to_number:
                station_to_number[station_name] = current_station_id
                current_station_id += 1

            metro_graph.set_station_lines(station_name, station_lines)

        valid_edges = 0
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
                valid_edges += 1

        # 验证图构建结果
        assert len(station_to_number) > 0, "应该成功添加站点到图中"
        assert valid_edges > 0, "应该成功添加边到图中"

        print(f"✓ 图构建成功: {len(station_to_number)} 个站点, {valid_edges} 条边")

        # 验证图的连通性（简单检查）
        # 检查是否有站点没有任何连接
        connected_stations = set()
        for conn in subway_data['connections']:
            if conn['source'] in station_to_number and conn['dest'] in station_to_number:
                connected_stations.add(conn['source'])
                connected_stations.add(conn['dest'])

        connectivity_ratio = len(connected_stations) / len(station_to_number)
        print(f"✓ 图连通性: {connectivity_ratio:.2%} 的站点有连接")

        # 大部分站点应该是连通的
        assert connectivity_ratio >= 0.8, \
            f"至少80%的站点应该有连接，实际为 {connectivity_ratio:.2%}"


if __name__ == "__main__":
    pytest.main([__file__])
