# -*- coding: utf-8 -*-
"""
单元测试用例设计质量测试
检查单元测试文件和测试用例的完整性
"""

import pytest
import os
import sys
import ast
import inspect
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestUnitTestCoverage:
    """单元测试用例设计测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_path = Path(__file__).parent
        self.src_path = Path(__file__).parent.parent.parent / 'src'
        self.expected_coverage = 0.8  # 80%核心功能覆盖率
        
    def test_unit_test_files_existence(self):
        """测试单元测试文件存在性
        
        验证：
        1. 存在完整的单元测试用例
        2. 测试用例设计合理
        3. 覆盖核心功能≥80%
        """
        
        # 查找所有测试文件
        test_files = list(self.test_path.glob('test_*.py'))
        test_files = [f for f in test_files if f.name != 'test_unit_test_coverage.py']  # 排除自身
        
        print(f"发现的测试文件:")
        for test_file in test_files:
            print(f"  - {test_file.name}")
        
        # 验证测试文件数量合理
        assert len(test_files) >= 7, \
            f"单元测试文件数量{len(test_files)}少于7个，可能覆盖不足"
        
        # 验证测试文件命名规范
        for test_file in test_files:
            assert test_file.name.startswith('test_'), \
                f"测试文件{test_file.name}不符合test_开头的命名规范"
            assert test_file.name.endswith('.py'), \
                f"测试文件{test_file.name}不是Python文件"
        
        print(f"单元测试文件检查: {len(test_files)}个文件符合规范")
        print("单元测试文件存在性验证通过")
    
    def test_test_case_design_quality(self):
        """测试测试用例设计质量"""
        
        test_files = list(self.test_path.glob('test_*.py'))
        test_files = [f for f in test_files if f.name != 'test_unit_test_coverage.py']
        
        total_test_methods = 0
        total_test_classes = 0
        well_designed_tests = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # 统计测试类和测试方法
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        total_test_classes += 1
                        
                        # 检查测试类是否有setup_method
                        has_setup = any(isinstance(child, ast.FunctionDef) and child.name == 'setup_method' 
                                      for child in node.body)
                        
                        # 统计测试方法
                        test_methods = [child for child in node.body 
                                      if isinstance(child, ast.FunctionDef) and child.name.startswith('test_')]
                        
                        total_test_methods += len(test_methods)
                        
                        # 检查测试方法质量
                        for method in test_methods:
                            # 检查是否有文档字符串
                            has_docstring = ast.get_docstring(method) is not None
                            
                            # 检查是否有断言语句
                            has_assertions = any(
                                isinstance(stmt, ast.Assert) or 
                                (isinstance(stmt, ast.Expr) and 
                                 isinstance(stmt.value, ast.Call) and
                                 getattr(stmt.value.func, 'attr', None) == 'assert')
                                for stmt in ast.walk(method)
                            )
                            
                            if has_docstring and has_assertions:
                                well_designed_tests += 1
                
            except (SyntaxError, UnicodeDecodeError):
                print(f"跳过测试文件（语法或编码错误）: {test_file}")
        
        print(f"测试用例设计质量统计:")
        print(f"测试类数量: {total_test_classes}")
        print(f"测试方法数量: {total_test_methods}")
        print(f"设计良好的测试: {well_designed_tests}")
        
        # 验证测试用例设计合理
        if total_test_methods > 0:
            quality_ratio = well_designed_tests / total_test_methods
            assert quality_ratio >= 0.7, \
                f"设计良好的测试比例{quality_ratio:.1%}低于70%"
        
        assert total_test_classes >= 5, \
            f"测试类数量{total_test_classes}少于5个"
        
        assert total_test_methods >= 15, \
            f"测试方法数量{total_test_methods}少于15个"
        
        print("测试用例设计质量验证通过")
    
    def test_core_functionality_coverage(self):
        """测试核心功能覆盖度"""
        
        # 定义核心功能模块和预期测试覆盖
        core_modules = {
            'data_processing.py': ['DataProcessor'],
            'models/sir_model.py': ['SIRModel'],
            'models/seir_model.py': ['SEIRModel'],
            'models/isolation_seir_model.py': ['IsolationSEIRModel'],
            'models/spatial_brownian_model.py': ['SpatialBrownianModel', 'Individual'],
            'utils.py': ['calculate_mse', 'calculate_mae', 'check_data_quality']
        }
        
        # 预期的测试覆盖映射
        expected_test_coverage = {
            'DataProcessor': ['test_data_field_extraction.py'],
            'SIRModel': ['test_runtime_performance.py'],
            'SEIRModel': ['test_runtime_performance.py'],
            'IsolationSEIRModel': ['test_isolation_effectiveness.py'],
            'SpatialBrownianModel': ['test_spatial_distance_calculation.py', 'test_spatial_transmission_probability.py'],
            'Individual': ['test_brownian_motion.py', 'test_spatial_isolation_management.py']
        }
        
        # 检查实际测试文件
        test_files = list(self.test_path.glob('test_*.py'))
        test_file_names = [f.name for f in test_files]
        
        coverage_results = {}
        total_core_components = 0
        covered_components = 0
        
        for component, expected_tests in expected_test_coverage.items():
            total_core_components += 1
            
            # 检查是否有对应的测试文件
            has_test = any(test_name in test_file_names for test_name in expected_tests)
            
            if has_test:
                covered_components += 1
                coverage_results[component] = True
            else:
                coverage_results[component] = False
        
        # 计算覆盖率
        coverage_rate = covered_components / total_core_components if total_core_components > 0 else 0
        
        print(f"核心功能测试覆盖情况:")
        for component, covered in coverage_results.items():
            status = "✓" if covered else "✗"
            print(f"  {status} {component}")
        
        print(f"覆盖率: {covered_components}/{total_core_components} ({coverage_rate:.1%})")
        
        # 验证核心功能覆盖≥80%
        assert coverage_rate >= self.expected_coverage, \
            f"核心功能测试覆盖率{coverage_rate:.1%}低于{self.expected_coverage:.0%}要求"
        
        print("核心功能覆盖度测试通过")
    
    def test_test_method_completeness(self):
        """测试测试方法完整性"""
        
        test_files = list(self.test_path.glob('test_*.py'))
        test_files = [f for f in test_files if f.name != 'test_unit_test_coverage.py']
        
        # 分析各个测试文件的测试方法数量和质量
        file_stats = {}
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                test_methods = []
                setup_methods = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith('test_'):
                            test_methods.append(node.name)
                        elif node.name in ['setup_method', 'setUp', 'tearDown']:
                            setup_methods.append(node.name)
                
                file_stats[test_file.name] = {
                    'test_methods': len(test_methods),
                    'setup_methods': len(setup_methods),
                    'methods': test_methods
                }
                
            except (SyntaxError, UnicodeDecodeError):
                print(f"跳过测试文件（语法或编码错误）: {test_file}")
        
        print(f"测试方法统计:")
        total_test_methods = 0
        for filename, stats in file_stats.items():
            print(f"  {filename}: {stats['test_methods']}个测试方法")
            total_test_methods += stats['test_methods']
        
        print(f"总测试方法数: {total_test_methods}")
        
        # 验证测试方法数量充足
        assert total_test_methods >= 20, \
            f"测试方法总数{total_test_methods}少于20个，可能测试不够充分"
        
        # 验证每个测试文件的测试方法数量合理
        for filename, stats in file_stats.items():
            assert stats['test_methods'] >= 1, \
                f"测试文件{filename}应至少包含1个测试方法"
            
            # 较大的测试文件应该有setup方法
            if stats['test_methods'] >= 3:
                assert stats['setup_methods'] >= 1, \
                    f"复杂测试文件{filename}应包含setup_method"
        
        print("测试方法完整性验证通过")
    
    def test_assertion_quality(self):
        """测试断言质量"""
        
        test_files = list(self.test_path.glob('test_*.py'))
        test_files = [f for f in test_files if f.name != 'test_unit_test_coverage.py']
        
        assertion_stats = {
            'total_test_methods': 0,
            'methods_with_assertions': 0,
            'total_assertions': 0,
            'descriptive_assertions': 0  # 带有描述性消息的断言
        }
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # 分析测试方法中的断言
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        assertion_stats['total_test_methods'] += 1
                        
                        method_assertions = []
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assert):
                                method_assertions.append(child)
                                assertion_stats['total_assertions'] += 1
                                
                                # 检查断言是否有描述性消息
                                if child.msg:
                                    assertion_stats['descriptive_assertions'] += 1
                        
                        if method_assertions:
                            assertion_stats['methods_with_assertions'] += 1
                
            except (SyntaxError, UnicodeDecodeError):
                print(f"跳过测试文件（语法或编码错误）: {test_file}")
        
        # 计算断言质量指标
        methods_with_assertions_rate = (assertion_stats['methods_with_assertions'] / 
                                      assertion_stats['total_test_methods'] 
                                      if assertion_stats['total_test_methods'] > 0 else 0)
        
        avg_assertions_per_method = (assertion_stats['total_assertions'] / 
                                   assertion_stats['total_test_methods'] 
                                   if assertion_stats['total_test_methods'] > 0 else 0)
        
        descriptive_assertions_rate = (assertion_stats['descriptive_assertions'] / 
                                     assertion_stats['total_assertions'] 
                                     if assertion_stats['total_assertions'] > 0 else 0)
        
        print(f"断言质量统计:")
        print(f"测试方法总数: {assertion_stats['total_test_methods']}")
        print(f"有断言的方法: {assertion_stats['methods_with_assertions']} ({methods_with_assertions_rate:.1%})")
        print(f"总断言数: {assertion_stats['total_assertions']}")
        print(f"平均断言数/方法: {avg_assertions_per_method:.1f}")
        print(f"描述性断言: {assertion_stats['descriptive_assertions']} ({descriptive_assertions_rate:.1%})")
        
        # 验证断言质量
        assert methods_with_assertions_rate >= 0.9, \
            f"包含断言的测试方法比例{methods_with_assertions_rate:.1%}低于90%"
        
        assert avg_assertions_per_method >= 2.0, \
            f"平均断言数{avg_assertions_per_method:.1f}低于2.0，测试可能不够充分"
        
        assert descriptive_assertions_rate >= 0.7, \
            f"描述性断言比例{descriptive_assertions_rate:.1%}低于70%"
        
        print("断言质量测试通过")
    
    def test_test_case_design_patterns(self):
        """测试测试用例设计模式"""
        
        # 检查测试是否遵循AAA模式（Arrange-Act-Assert）
        test_files = list(self.test_path.glob('test_*.py'))
        test_files = [f for f in test_files if f.name != 'test_unit_test_coverage.py']
        
        pattern_analysis = {
            'total_test_methods': 0,
            'methods_with_aaa_comments': 0,
            'methods_with_docstrings': 0,
            'methods_with_setup': 0
        }
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # 找到测试类
                for class_node in ast.walk(tree):
                    if isinstance(class_node, ast.ClassDef) and class_node.name.startswith('Test'):
                        
                        # 检查是否有setup_method
                        has_class_setup = any(isinstance(method, ast.FunctionDef) and method.name == 'setup_method' 
                                            for method in class_node.body)
                        
                        # 分析测试方法
                        for method in class_node.body:
                            if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'):
                                pattern_analysis['total_test_methods'] += 1
                                
                                # 检查文档字符串
                                if ast.get_docstring(method):
                                    pattern_analysis['methods_with_docstrings'] += 1
                                    
                                    # 检查文档字符串是否包含验证说明
                                    docstring = ast.get_docstring(method)
                                    if '验证：' in docstring or 'Assert:' in docstring:
                                        pattern_analysis['methods_with_aaa_comments'] += 1
                                
                                if has_class_setup:
                                    pattern_analysis['methods_with_setup'] += 1
                
            except (SyntaxError, UnicodeDecodeError):
                print(f"跳过测试文件（语法或编码错误）: {test_file}")
        
        # 计算设计模式符合度
        docstring_rate = (pattern_analysis['methods_with_docstrings'] / 
                         pattern_analysis['total_test_methods'] 
                         if pattern_analysis['total_test_methods'] > 0 else 0)
        
        aaa_rate = (pattern_analysis['methods_with_aaa_comments'] / 
                   pattern_analysis['total_test_methods'] 
                   if pattern_analysis['total_test_methods'] > 0 else 0)
        
        setup_rate = (pattern_analysis['methods_with_setup'] / 
                     pattern_analysis['total_test_methods'] 
                     if pattern_analysis['total_test_methods'] > 0 else 0)
        
        print(f"测试设计模式分析:")
        print(f"总测试方法: {pattern_analysis['total_test_methods']}")
        print(f"有文档字符串: {pattern_analysis['methods_with_docstrings']} ({docstring_rate:.1%})")
        print(f"有验证说明: {pattern_analysis['methods_with_aaa_comments']} ({aaa_rate:.1%})")
        print(f"有setup方法: {pattern_analysis['methods_with_setup']} ({setup_rate:.1%})")
        
        # 验证设计模式质量
        assert docstring_rate >= 0.8, \
            f"测试方法文档覆盖率{docstring_rate:.1%}低于80%"
        
        assert aaa_rate >= 0.6, \
            f"包含验证说明的测试方法比例{aaa_rate:.1%}低于60%"
        
        print("测试用例设计模式验证通过")
    
    def test_test_independence(self):
        """测试测试用例独立性"""
        
        test_files = list(self.test_path.glob('test_*.py'))
        test_files = [f for f in test_files if f.name != 'test_unit_test_coverage.py']
        
        independence_issues = []
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有全局变量（可能影响测试独立性）
                tree = ast.parse(content)
                
                global_vars = []
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                global_vars.append(target.id)
                
                # 检查测试方法是否修改全局变量
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assign):
                                for target in child.targets:
                                    if isinstance(target, ast.Name) and target.id in global_vars:
                                        independence_issues.append(
                                            f"{test_file.name}:{node.name} 可能修改全局变量{target.id}"
                                        )
                
            except (SyntaxError, UnicodeDecodeError):
                print(f"跳过测试文件（语法或编码错误）: {test_file}")
        
        print(f"测试独立性检查:")
        print(f"发现{len(independence_issues)}个潜在独立性问题")
        
        for issue in independence_issues[:3]:  # 显示前3个
            print(f"  - {issue}")
        
        # 允许少量独立性问题
        assert len(independence_issues) <= 5, \
            f"测试独立性问题{len(independence_issues)}个过多"
        
        print("测试用例独立性验证通过")
    
    def test_test_naming_consistency(self):
        """测试测试命名一致性"""
        
        test_files = list(self.test_path.glob('test_*.py'))
        test_files = [f for f in test_files if f.name != 'test_unit_test_coverage.py']
        
        naming_consistency = {
            'total_files': len(test_files),
            'consistent_class_names': 0,
            'consistent_method_names': 0,
            'total_classes': 0,
            'total_methods': 0
        }
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                        naming_consistency['total_classes'] += 1
                        
                        # 检查类名是否遵循TestXxx模式
                        if re.match(r'^Test[A-Z][a-zA-Z0-9]*$', node.name):
                            naming_consistency['consistent_class_names'] += 1
                        
                        # 检查方法名
                        for method in node.body:
                            if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'):
                                naming_consistency['total_methods'] += 1
                                
                                # 方法名应该使用snake_case
                                if re.match(r'^test_[a-z][a-z0-9_]*$', method.name):
                                    naming_consistency['consistent_method_names'] += 1
                
            except (SyntaxError, UnicodeDecodeError):
                print(f"跳过测试文件（语法或编码错误）: {test_file}")
        
        # 计算命名一致性
        class_naming_rate = (naming_consistency['consistent_class_names'] / 
                           naming_consistency['total_classes'] 
                           if naming_consistency['total_classes'] > 0 else 0)
        
        method_naming_rate = (naming_consistency['consistent_method_names'] / 
                            naming_consistency['total_methods'] 
                            if naming_consistency['total_methods'] > 0 else 0)
        
        print(f"测试命名一致性:")
        print(f"类命名一致性: {naming_consistency['consistent_class_names']}/{naming_consistency['total_classes']} ({class_naming_rate:.1%})")
        print(f"方法命名一致性: {naming_consistency['consistent_method_names']}/{naming_consistency['total_methods']} ({method_naming_rate:.1%})")
        
        # 验证命名一致性
        assert class_naming_rate >= 0.9, \
            f"测试类命名一致性{class_naming_rate:.1%}低于90%"
        
        assert method_naming_rate >= 0.9, \
            f"测试方法命名一致性{method_naming_rate:.1%}低于90%"
        
        print("测试命名一致性验证通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestUnitTestCoverage()
    test_instance.setup_method()
    
    try:
        test_instance.test_unit_test_files_existence()
        test_instance.test_test_case_design_quality()
        test_instance.test_core_functionality_coverage()
        test_instance.test_test_method_completeness()
        test_instance.test_assertion_quality()
        test_instance.test_test_independence()
        test_instance.test_test_naming_consistency()
        print("\n所有单元测试用例设计测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")