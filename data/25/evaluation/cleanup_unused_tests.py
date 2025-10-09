# -*- coding: utf-8 -*-
"""
清理不在详细测试计划中的测试方法
"""

import os
import re

# 详细测试计划中实际包含的pytest测试方法
REQUIRED_TESTS = {
    'test_si_model_algorithm.py': ['test_si_model_core_algorithm'],
    'test_sir_model_algorithm.py': ['test_sir_model_core_algorithm', 'test_sir_model_parameter_validation'],
    'test_seir_model_algorithm.py': ['test_seir_model_core_algorithm'],
    'test_data_field_extraction.py': ['test_key_field_extraction_and_validation', 'test_field_extraction_with_real_data'],
    'test_isolation_effectiveness.py': ['test_isolation_reduces_infection_peak'],
    'test_brownian_motion.py': ['test_brownian_motion_characteristics'],
    'test_spatial_distance_calculation.py': ['test_spatial_distance_calculation_accuracy'],
    'test_spatial_transmission_probability.py': ['test_transmission_probability_distance_correlation'],
    'test_spatial_isolation_management.py': ['test_isolation_prevents_movement'],
    'test_exception_handling.py': ['test_invalid_file_path_handling'],
    'test_runtime_performance.py': ['test_complete_simulation_runtime'],
    'test_memory_performance.py': ['test_peak_memory_usage_constraint'],
    'test_code_modularity.py': ['test_module_structure_clarity'],
    'test_code_standards.py': ['test_code_comment_coverage'],
    'test_unit_test_coverage.py': ['test_unit_test_files_existence']
}

def cleanup_test_file(file_path, required_methods):
    """清理测试文件，只保留必需的测试方法"""
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到所有测试方法
    test_methods = re.findall(r'def (test_\w+)\(', content)
    print(f"\n{os.path.basename(file_path)}:")
    print(f"  现有测试方法: {len(test_methods)}个")
    print(f"  需要保留: {required_methods}")
    
    methods_to_remove = [m for m in test_methods if m not in required_methods]
    if methods_to_remove:
        print(f"  需要删除: {methods_to_remove}")
        
        # 为了快速处理，我只标记需要删除的方法
        for method in methods_to_remove:
            # 简单的方法：注释掉不需要的测试方法
            pattern = rf'def {method}\(.*?\n(.*?\n)*?.*?def |def {method}\(.*?\n(.*?\n)*?$'
            # 这里只是标识，实际删除需要更精确的处理
        
        return methods_to_remove
    else:
        print("  无需删除")
        return []

def main():
    tests_dir = "evaluation/tests"
    
    total_removed = 0
    for filename, required_methods in REQUIRED_TESTS.items():
        file_path = os.path.join(tests_dir, filename)
        removed = cleanup_test_file(file_path, required_methods)
        total_removed += len(removed)
    
    print(f"\n总共标记删除 {total_removed} 个不需要的测试方法")

if __name__ == "__main__":
    main()