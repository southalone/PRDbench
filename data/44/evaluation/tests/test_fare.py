import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fare_calculator import Sum_money


class TestFare:

    def test_fare_calculation(self):
        """测试基础计费计算功能"""
        # 测试用例：短距离（预期3元）、中距离（预期4-5元）、长距离（预期6元以上）
        test_cases = [
            # (距离(米), 预期票价(元))
            (3000, 3),    # 3公里，应该是3元
            (5000, 3),    # 5公里，应该是3元
            (8000, 4),    # 8公里，应该是4元
            (15000, 5),   # 15公里，应该是5元
            (25000, 6),   # 25公里，应该是6元
        ]

        for distance, expected_fare in test_cases:
            actual_fare = Sum_money(distance)
            assert actual_fare == expected_fare, \
                f"距离 {distance}米 的票价应该是 {expected_fare}元，实际计算为 {actual_fare}元"
            print(f"✓ {distance}米 -> {actual_fare}元")

    def test_fare_boundary_conditions(self):
        """测试计费规则边界处理"""
        # 测试边界情况：距离接近6公里、12公里、22公里、32公里的站点对
        boundary_test_cases = [
            # (距离(米), 预期票价(元), 描述)
            (5999, 3, "接近6公里边界（下）"),
            (6000, 4, "6公里边界"),
            (6001, 4, "接近6公里边界（上）"),
            (11999, 4, "接近12公里边界（下）"),
            (12000, 5, "12公里边界"),
            (12001, 5, "接近12公里边界（上）"),
            (21999, 5, "接近22公里边界（下）"),
            (22000, 6, "22公里边界"),
            (22001, 6, "接近22公里边界（上）"),
            (31999, 6, "接近32公里边界（下）"),
            (32000, 7, "32公里边界"),
            (32001, 7, "接近32公里边界（上）"),
        ]

        for distance, expected_fare, description in boundary_test_cases:
            actual_fare = Sum_money(distance)
            assert actual_fare == expected_fare, \
                f"{description}: 距离 {distance}米 的票价应该是 {expected_fare}元，实际计算为 {actual_fare}元"
            print(f"✓ {description}: {distance}米 -> {actual_fare}元")

    def test_extended_fare_rules(self):
        """测试扩展计费规则验证"""
        # 测试32公里以上每增加20公里增加1元的扩展计费规则
        extended_test_cases = [
            # (距离(米), 预期票价(元), 描述)
            (35000, 7, "32-52公里范围"),
            (45000, 7, "32-52公里范围中段"),
            (51999, 7, "接近52公里边界（下）"),
            (52000, 8, "52公里边界"),
            (52001, 8, "接近52公里边界（上）"),
            (65000, 8, "52-72公里范围"),
            (71999, 8, "接近72公里边界（下）"),
            (72000, 9, "72公里边界"),
            (72001, 9, "接近72公里边界（上）"),
            (85000, 9, "72-92公里范围"),
            (92000, 10, "92公里边界"),
            (100000, 10, "100公里"),
        ]

        for distance, expected_fare, description in extended_test_cases:
            actual_fare = Sum_money(distance)
            assert actual_fare == expected_fare, \
                f"{description}: 距离 {distance}米 的票价应该是 {expected_fare}元，实际计算为 {actual_fare}元"
            print(f"✓ {description}: {distance}米 -> {actual_fare}元")

    def test_fare_calculation_edge_cases(self):
        """测试计费计算的边界情况"""
        # 测试一些特殊情况
        edge_cases = [
            (0, 3),      # 0距离，最低票价
            (1, 3),      # 1米，最低票价
            (100, 3),    # 100米，最低票价
            (1000, 3),   # 1公里，最低票价
        ]

        for distance, expected_fare in edge_cases:
            actual_fare = Sum_money(distance)
            assert actual_fare == expected_fare, \
                f"边界情况：距离 {distance}米 的票价应该是 {expected_fare}元，实际计算为 {actual_fare}元"
            print(f"✓ 边界情况: {distance}米 -> {actual_fare}元")

    def test_fare_calculation_consistency(self):
        """测试计费计算的一致性"""
        # 确保相同距离总是返回相同票价
        test_distance = 15000  # 15公里
        expected_fare = Sum_money(test_distance)

        # 多次计算应该得到相同结果
        for _ in range(10):
            actual_fare = Sum_money(test_distance)
            assert actual_fare == expected_fare, \
                f"计费计算应该保持一致性，距离 {test_distance}米 应该始终返回 {expected_fare}元"

        print(f"✓ 一致性测试通过: {test_distance}米 始终返回 {expected_fare}元")


if __name__ == "__main__":
    pytest.main([__file__])
