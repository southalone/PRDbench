
import pytest
import sys
import os
import shutil

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Correctly import the function
from combo_generator import generate_combos
from data_manager import find_ingredient_by_name # We need this for assertions

# Define paths for test data
TEST_DATA_DIR = os.path.dirname(__file__)
APP_DATA_DIR = os.path.abspath(os.path.join(TEST_DATA_DIR, '../../src/data'))
APP_INGREDIENTS_FILE = os.path.join(APP_DATA_DIR, 'ingredients.csv')

@pytest.fixture
def setup_test_ingredients():
    """
    Fixture to replace the main ingredients file with a test version
    before a test, and restore it afterwards.
    """
    # Backup original file if it exists
    original_file_backup = APP_INGREDIENTS_FILE + ".bak"
    if os.path.exists(APP_INGREDIENTS_FILE):
        shutil.copy(APP_INGREDIENTS_FILE, original_file_backup)

    # Copy test data to the location the app uses
    test_ingredients_src = os.path.join(TEST_DATA_DIR, '../ingredients_for_test_2.3.2.csv')
    shutil.copy(test_ingredients_src, APP_INGREDIENTS_FILE)

    yield # This is where the test runs

    # Teardown: Restore the original file
    if os.path.exists(original_file_backup):
        shutil.move(original_file_backup, APP_INGREDIENTS_FILE)
    elif os.path.exists(APP_INGREDIENTS_FILE):
        # If there was no original file, clean up the one we created
        os.remove(APP_INGREDIENTS_FILE)


def test_combo_generation_nutrition_constraints(setup_test_ingredients):
    """
    Tests that all generated combos adhere to the nutritional constraints.
    Metric: 2.3.2 核心组合逻辑与营养约束
    """
    # Arrange: The fixture has already prepared the data file.
    
    # Act: Call the function directly. It will now read our test data.
    combos = generate_combos(
        combo_type='单人餐',
        discount=0.9,
        stock_priority='高',
        target_profit_rate=0.3
    )

    # Assert
    assert combos is not None, "套餐生成失败，返回了None"
    assert len(combos) > 0, "未生成任何候选套餐"

    for combo in combos:
        ingredients = combo['ingredients']
        
        # Get the full ingredient details using the real data_manager function
        full_ingredient_details = [find_ingredient_by_name(item['name']) for item in ingredients]

        # Check for presence and quantity of each category
        has_main = any(ing['类别'] == '主食' and next(item['usage'] for item in ingredients if item['name'] == ing['名称']) >= 0.1 for ing in full_ingredient_details if ing)
        has_protein = any(ing['类别'] == '蛋白质' and next(item['usage'] for item in ingredients if item['name'] == ing['名称']) >= 0.08 for ing in full_ingredient_details if ing)
        has_veg = any(ing['类别'] == '蔬菜' and next(item['usage'] for item in ingredients if item['name'] == ing['名称']) >= 0.1 for ing in full_ingredient_details if ing)

        assert has_main, f"套餐缺少主食或用量不足"
        assert has_protein, f"套餐缺少蛋白质或用量不足"
        assert has_veg, f"套餐缺少蔬菜或用量不足"
