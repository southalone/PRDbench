

import pytest
import sys
import os
from unittest.mock import patch

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Now import the functions
from cost_calculator import calculate_ingredient_cost, calculate_combo_cost

# Mock data that the data_manager would normally provide
MOCK_INGREDIENTS = {
    "五常大米": {'采购单价': 10, '加工损耗率': 10, '单位': 'kg'},
    "鸡胸肉": {'采购单价': 15, '加工损耗率': 5, '单位': 'kg'},
    "零损耗食材": {'采购单价': 20, '加工损耗率': 0, '单位': 'kg'},
}

MOCK_EXTRA_COSTS = {
    "打包盒": 1.5,
    "一次性餐具": 0.8
}

@pytest.fixture
def mock_data_manager():
    """Pytest fixture to mock the data_manager functions."""
    with patch('cost_calculator.find_ingredient_by_name', side_effect=lambda name: MOCK_INGREDIENTS.get(name)), \
         patch('cost_calculator.get_extra_costs', return_value=MOCK_EXTRA_COSTS):
        yield

# Metric: 2.2.1 单项食材成本计算 (with boundary conditions)
@pytest.mark.parametrize("name, usage, expected_cost", [
    ("五常大米", 0.15, 1.65),      # Standard case from metric
    ("鸡胸肉", 0.2, 3.15),        # Another standard case
    ("零损耗食材", 1, 20.0),       # Boundary: Zero waste loss
    ("五常大米", 0, 0.0),         # Boundary: Zero quantity
    ("不存在的食材", 0.1, 0.0),    # Edge: Ingredient not found
])
def test_calculate_ingredient_cost(mock_data_manager, name, usage, expected_cost):
    cost, _ = calculate_ingredient_cost(name, usage)
    assert cost == pytest.approx(expected_cost)

# Metric: 2.2.2a 总成本计算 - 成本汇总
def test_calculate_combo_cost(mock_data_manager):
    ingredients_list = [
        {'name': '五常大米', 'usage': 0.15}, # Cost: 1.65
        {'name': '鸡胸肉', 'usage': 0.35}  # Cost: 5.5125 -> 5.51
    ]
    extra_cost_names = ["打包盒"] # Cost: 1.5
    # Expected: 1.65 + 5.51 + 1.5 = 8.66
    
    total_cost, _, _ = calculate_combo_cost(ingredients_list, extra_cost_names)
    assert total_cost == pytest.approx(8.66)

def test_calculate_combo_cost_with_all_extras(mock_data_manager):
    ingredients_list = [{'name': '五常大米', 'usage': 0.15}] # Cost: 1.65
    extra_cost_names = ["打包盒", "一次性餐具"] # Cost: 1.5 + 0.8 = 2.3
    # Expected: 1.65 + 2.3 = 3.95
    
    total_cost, _, _ = calculate_combo_cost(ingredients_list, extra_cost_names)
    assert total_cost == pytest.approx(3.95)

def test_calculate_combo_cost_no_extras(mock_data_manager):
    ingredients_list = [{'name': '五常大米', 'usage': 0.15}] # Cost: 1.65
    extra_cost_names = []
    # Expected: 1.65
    
    total_cost, _, _ = calculate_combo_cost(ingredients_list, extra_cost_names)
    assert total_cost == pytest.approx(1.65)
