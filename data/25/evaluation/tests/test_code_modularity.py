# -*- coding: utf-8 -*-
"""
代码模块化设计单元测试
测试代码结构和模块划分的合理性
"""

import pytest
import os
import sys
import ast
import importlib
import inspect
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestCodeModularity:
    """代码模块化设计测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.src_path = Path(__file__).parent.parent.parent / 'src'
        self.expected_modules = [
            'config.py',
            'data_processing.py',
            'main.py',
            'model_evaluation.py',
            'parameter_estimation.py',
            'utils.py',
            'models/__init__.py',
            'models/isolation_seir_model.py',
            'models/seir_model.py',
            'models/si_model.py',
            'models/sir_model.py',
            'models/spatial_brownian_model.py'
        ]
        
    def test_module_structure_clarity(self):
        """测试模块化设计清晰性
        
        验证：
        1. 模块化设计清晰
        2. 功能模块独立
        3. 接口定义合理
        4. 模块间耦合度低
        """
        
        # 验证预期的模块文件都存在
        missing_modules = []
        for module_path in self.expected_modules:
            full_path = self.src_path / module_path
            if not full_path.exists():
                missing_modules.append(module_path)
        
        assert len(missing_modules) == 0, \
            f"缺少预期模块: {missing_modules}"
        
        # 验证models包结构
        models_path = self.src_path / 'models'
        assert models_path.is_dir(), "models应该是一个包目录"
        
        model_files = [f for f in models_path.iterdir() if f.suffix == '.py']
        assert len(model_files) >= 5, f"models包应该包含≥5个模型文件，实际{len(model_files)}个"
        
        print(f"发现{len(model_files)}个模型模块")
        print("模块结构清晰性验证通过")
    
    def test_functional_module_independence(self):
        """测试功能模块独立性"""
        
        # 导入并检查各功能模块
        modules_to_test = {
            'config': 'config',
            'data_processing': 'data_processing',
            'utils': 'utils',
            'model_evaluation': 'model_evaluation',
            'parameter_estimation': 'parameter_estimation'
        }
        
        successfully_imported = {}
        
        for module_name, import_name in modules_to_test.items():
            try:
                module = importlib.import_module(import_name)
                successfully_imported[module_name] = module
                
                # 检查模块是否有明确的功能边界
                module_functions = [name for name, obj in inspect.getmembers(module) 
                                  if inspect.isfunction(obj) and not name.startswith('_')]
                module_classes = [name for name, obj in inspect.getmembers(module) 
                                if inspect.isclass(obj) and not name.startswith('_')]
                
                print(f"{module_name}模块: {len(module_classes)}个类, {len(module_functions)}个函数")
                
            except ImportError as e:
                print(f"模块{module_name}导入失败: {e}")
        
        # 验证关键模块能够独立导入
        assert 'config' in successfully_imported, "配置模块应该能够独立导入"
        assert 'utils' in successfully_imported, "工具模块应该能够独立导入"
        assert 'data_processing' in successfully_imported, "数据处理模块应该能够独立导入"
        
        print("功能模块独立性验证通过")
    
    def test_interface_definition_quality(self):
        """测试接口定义合理性"""
        
        # 检查主要类的接口设计
        from data_processing import DataProcessor
        from models.sir_model import SIRModel
        from models.seir_model import SEIRModel
        
        classes_to_check = [
            (DataProcessor, ['load_raw_data', 'validate_data', 'calculate_seir_states']),
            (SIRModel, ['__init__', 'solve_ode', 'plot_results']),
            (SEIRModel, ['__init__', 'solve_ode', 'plot_results'])
        ]
        
        for cls, expected_methods in classes_to_check:
            # 检查类是否有预期的公共方法
            actual_methods = [name for name, method in inspect.getmembers(cls) 
                            if inspect.ismethod(method) or inspect.isfunction(method)]
            
            for expected_method in expected_methods:
                assert expected_method in actual_methods or hasattr(cls, expected_method), \
                    f"类{cls.__name__}缺少预期方法{expected_method}"
            
            # 检查方法是否有文档字符串
            public_methods = [name for name in actual_methods if not name.startswith('_')]
            documented_methods = 0
            
            for method_name in public_methods:
                method = getattr(cls, method_name, None)
                if method and hasattr(method, '__doc__') and method.__doc__:
                    documented_methods += 1
            
            if len(public_methods) > 0:
                doc_ratio = documented_methods / len(public_methods)
                assert doc_ratio >= 0.7, \
                    f"类{cls.__name__}方法文档覆盖率{doc_ratio:.1%}低于70%"
            
            print(f"{cls.__name__}类: {len(public_methods)}个公共方法, 文档覆盖率{doc_ratio:.1%}")
        
        print("接口定义合理性验证通过")
    
    def test_module_coupling_analysis(self):
        """测试模块间耦合度"""
        
        # 分析模块间的导入依赖关系
        dependency_map = {}
        
        for module_file in self.expected_modules:
            if module_file.endswith('.py'):
                file_path = self.src_path / module_file
                if file_path.exists():
                    # 解析Python文件的AST
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            tree = ast.parse(f.read())
                            imports = []
                            
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        imports.append(alias.name)
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        imports.append(node.module)
                            
                            # 过滤出项目内部导入
                            internal_imports = [imp for imp in imports 
                                              if any(expected.replace('.py', '').replace('/', '.') in imp 
                                                   for expected in self.expected_modules)]
                            
                            dependency_map[module_file] = internal_imports
                            
                        except SyntaxError:
                            print(f"语法错误，跳过文件: {module_file}")
        
        # 分析耦合度
        total_dependencies = sum(len(deps) for deps in dependency_map.values())
        avg_dependencies = total_dependencies / len(dependency_map) if dependency_map else 0
        
        print(f"模块依赖分析:")
        for module, deps in dependency_map.items():
            print(f"  {module}: {len(deps)}个内部依赖")
        
        print(f"平均模块依赖数: {avg_dependencies:.1f}")
        
        # 验证耦合度合理（平均依赖数不应过高）
        assert avg_dependencies <= 5.0, \
            f"平均模块依赖数{avg_dependencies:.1f}过高，模块间耦合度过大"
        
        # 检查循环依赖（简单检查）
        for module, deps in dependency_map.items():
            for dep in deps:
                dep_file = dep.replace('.', '/') + '.py'
                if dep_file in dependency_map:
                    reverse_deps = dependency_map[dep_file]
                    module_name = module.replace('.py', '').replace('/', '.')
                    assert module_name not in [d for d in reverse_deps if d], \
                        f"检测到可能的循环依赖: {module} <-> {dep_file}"
        
        print("模块间耦合度验证通过")
    
    def test_separation_of_concerns(self):
        """测试关注点分离"""
        
        # 验证不同类型的功能被适当分离
        
        # 1. 配置管理应该集中在config.py
        import config
        config_items = [name for name in dir(config) if name.isupper()]
        assert len(config_items) >= 5, f"配置文件应包含≥5个配置项，实际{len(config_items)}个"
        
        # 2. 工具函数应该集中在utils.py
        import utils
        util_functions = [name for name, obj in inspect.getmembers(utils) 
                         if inspect.isfunction(obj) and not name.startswith('_')]
        assert len(util_functions) >= 8, f"工具模块应包含≥8个工具函数，实际{len(util_functions)}个"
        
        # 3. 各个模型应该在单独的模块中
        model_modules = ['si_model', 'sir_model', 'seir_model', 
                        'isolation_seir_model', 'spatial_brownian_model']
        
        for model_name in model_modules:
            try:
                module = importlib.import_module(f'models.{model_name}')
                model_classes = [name for name, obj in inspect.getmembers(module) 
                               if inspect.isclass(obj) and not name.startswith('_')]
                assert len(model_classes) >= 1, f"模型模块{model_name}应至少包含1个模型类"
                print(f"{model_name}: {len(model_classes)}个模型类")
                
            except ImportError:
                print(f"模型模块{model_name}导入失败")
        
        print("关注点分离验证通过")
    
    # 已删除test_code_organization_best_practices - 不在详细测试计划中
        
        print("代码组织最佳实践验证通过")
    
    def test_class_design_principles(self):
        """测试类设计原则"""
        
        from models.sir_model import SIRModel
        from models.seir_model import SEIRModel
        from data_processing import DataProcessor
        
        classes_to_analyze = [SIRModel, SEIRModel, DataProcessor]
        
        for cls in classes_to_analyze:
            # 检查类是否有合理的方法数量（不应过多，避免违反单一职责）
            public_methods = [name for name, method in inspect.getmembers(cls) 
                            if (inspect.ismethod(method) or inspect.isfunction(method)) 
                            and not name.startswith('_')]
            
            assert len(public_methods) <= 15, \
                f"类{cls.__name__}有{len(public_methods)}个公共方法，可能违反单一职责原则"
            
            # 检查构造函数参数合理性
            init_method = getattr(cls, '__init__', None)
            if init_method:
                sig = inspect.signature(init_method)
                param_count = len([p for p in sig.parameters.values() if p.name != 'self'])
                assert param_count <= 5, \
                    f"类{cls.__name__}构造函数有{param_count}个参数，过多可能影响可用性"
            
            # 检查类是否有文档字符串
            assert cls.__doc__ is not None and len(cls.__doc__.strip()) > 0, \
                f"类{cls.__name__}应该有文档字符串"
            
            print(f"{cls.__name__}类: {len(public_methods)}个方法, 构造参数{param_count}个")
        
        print("类设计原则验证通过")
    
    def test_import_dependency_reasonableness(self):
        """测试导入依赖的合理性"""
        
        # 检查是否存在不必要的依赖
        files_to_check = [
            'config.py',      # 配置文件应该依赖最少
            'utils.py',       # 工具文件应该依赖最少
            'main.py'         # 主文件可能依赖较多
        ]
        
        for filename in files_to_check:
            file_path = self.src_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            imports.extend(alias.name for alias in node.names)
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            imports.append(node.module)
                    
                    # 过滤标准库导入
                    third_party_imports = [imp for imp in imports 
                                         if imp not in ['os', 'sys', 'time', 'ast', 'inspect'] 
                                         and not imp.startswith('__')]
                    
                    print(f"{filename}: {len(third_party_imports)}个第三方/项目依赖")
                    
                    # 配置文件和工具文件的依赖应该相对较少
                    if filename == 'config.py':
                        assert len(third_party_imports) <= 3, \
                            f"配置文件依赖过多: {len(third_party_imports)}"
                    elif filename == 'utils.py':
                        assert len(third_party_imports) <= 5, \
                            f"工具文件依赖过多: {len(third_party_imports)}"
        
        print("导入依赖合理性验证通过")
    
    def test_code_reusability(self):
        """测试代码可复用性"""
        
        # 检查工具函数的通用性
        import utils
        
        util_functions = [name for name, obj in inspect.getmembers(utils) 
                         if inspect.isfunction(obj) and not name.startswith('_')]
        
        # 检查是否有数学计算相关的通用函数
        math_functions = [f for f in util_functions if any(keyword in f.lower() 
                         for keyword in ['calculate', 'mse', 'mae', 'r_squared'])]
        
        assert len(math_functions) >= 3, \
            f"应该有≥3个数学计算工具函数，实际{len(math_functions)}个"
        
        # 检查是否有数据处理相关的通用函数
        data_functions = [f for f in util_functions if any(keyword in f.lower() 
                         for keyword in ['save', 'load', 'normalize', 'smooth'])]
        
        assert len(data_functions) >= 3, \
            f"应该有≥3个数据处理工具函数，实际{len(data_functions)}个"
        
        # 检查是否有可视化相关的通用函数
        viz_functions = [f for f in util_functions if any(keyword in f.lower() 
                        for keyword in ['plot', 'setup', 'create', 'matplotlib'])]
        
        assert len(viz_functions) >= 2, \
            f"应该有≥2个可视化工具函数，实际{len(viz_functions)}个"
        
        print(f"工具函数分类:")
        print(f"  数学计算: {math_functions}")
        print(f"  数据处理: {data_functions}")
        print(f"  可视化: {viz_functions}")
        
        print("代码可复用性验证通过")
    
    def test_configuration_centralization(self):
        """测试配置集中化"""
        
        import config
        
        # 检查配置项的完整性
        config_categories = [
            'SI_CONFIG',
            'SIR_CONFIG',
            'SEIR_CONFIG',
            'ISOLATION_SEIR_CONFIG',
            'SPATIAL_BROWNIAN_CONFIG',
            'OUTPUT_DIRS',
            'DATA_FILES'
        ]
        
        for config_name in config_categories:
            assert hasattr(config, config_name), \
                f"配置文件应该包含{config_name}"
            
            config_value = getattr(config, config_name)
            assert isinstance(config_value, dict), \
                f"{config_name}应该是字典类型"
            assert len(config_value) > 0, \
                f"{config_name}不应该为空"
        
        print(f"发现{len(config_categories)}个配置类别")
        print("配置集中化验证通过")
    
    def test_error_handling_consistency(self):
        """测试错误处理一致性"""
        
        from data_processing import DataProcessor
        
        # 检查主要方法是否有错误处理
        processor = DataProcessor()
        
        # 测试错误处理的一致性
        error_handling_methods = ['load_raw_data', 'validate_data', 'calculate_seir_states']
        
        for method_name in error_handling_methods:
            method = getattr(processor, method_name)
            
            # 检查方法是否返回状态指示（布尔值或None）
            # 这里我们通过检查方法的行为来验证错误处理
            if method_name == 'load_raw_data':
                # 测试加载不存在文件的错误处理
                result = method('non_existent_file.xlsx')
                assert result == False, f"{method_name}应该返回False表示失败"
        
        print("错误处理一致性验证通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestCodeModularity()
    test_instance.setup_method()
    
    try:
        test_instance.test_module_structure_clarity()
        test_instance.test_functional_module_independence()
        test_instance.test_interface_definition_quality()
        test_instance.test_module_coupling_analysis()
        test_instance.test_separation_of_concerns()
        test_instance.test_code_organization_best_practices()
        test_instance.test_class_design_principles()
        test_instance.test_import_dependency_reasonableness()
        test_instance.test_code_reusability()
        test_instance.test_configuration_centralization()
        test_instance.test_error_handling_consistency()
        print("\n所有代码模块化设计测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")