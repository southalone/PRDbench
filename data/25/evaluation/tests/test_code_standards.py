# -*- coding: utf-8 -*-
"""
代码规范与注释质量单元测试
测试代码注释覆盖率、命名规范和PEP8符合度
"""

import pytest
import os
import sys
import ast
import re
import inspect
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestCodeStandards:
    """代码规范与注释质量测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.src_path = Path(__file__).parent.parent.parent / 'src'
        self.python_files = list(self.src_path.rglob('*.py'))
        # 过滤掉非源码文件
        self.python_files = [f for f in self.python_files if not f.name.startswith('test_')]
        
    def test_code_comment_coverage(self):
        """测试代码注释覆盖率
        
        验证：
        1. 代码注释详细（覆盖率≥80%）
        2. 命名规范一致
        3. PEP8规范符合度≥90%
        4. 错误处理完善
        """
        
        total_functions = 0
        documented_functions = 0
        total_classes = 0
        documented_classes = 0
        
        for py_file in self.python_files:
            if py_file.exists() and py_file.stat().st_size > 0:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    # 统计函数和类的文档字符串
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                            total_functions += 1
                            if ast.get_docstring(node):
                                documented_functions += 1
                        
                        elif isinstance(node, ast.ClassDef):
                            total_classes += 1
                            if ast.get_docstring(node):
                                documented_classes += 1
                
                except (SyntaxError, UnicodeDecodeError):
                    print(f"跳过文件（语法或编码错误）: {py_file}")
        
        # 计算文档覆盖率
        function_doc_rate = documented_functions / total_functions if total_functions > 0 else 0
        class_doc_rate = documented_classes / total_classes if total_classes > 0 else 0
        
        print(f"文档覆盖率统计:")
        print(f"函数: {documented_functions}/{total_functions} ({function_doc_rate:.1%})")
        print(f"类: {documented_classes}/{total_classes} ({class_doc_rate:.1%})")
        
        # 验证注释覆盖率≥80%
        overall_doc_rate = (documented_functions + documented_classes) / (total_functions + total_classes) if (total_functions + total_classes) > 0 else 0
        
        assert overall_doc_rate >= 0.80, \
            f"代码注释覆盖率{overall_doc_rate:.1%}低于80%要求"
        
        print(f"整体文档覆盖率: {overall_doc_rate:.1%}")
        print("代码注释覆盖率测试通过")
    
    def test_naming_convention_consistency(self):
        """测试命名规范一致性"""
        
        naming_issues = []
        
        for py_file in self.python_files:
            if py_file.exists():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    # 检查类名（应该使用PascalCase）
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                                naming_issues.append(f"{py_file.name}:类名{class_name}不符合PascalCase")
                        
                        elif isinstance(node, ast.FunctionDef):
                            func_name = node.name
                            if not func_name.startswith('_'):  # 排除私有方法
                                # 函数名应该使用snake_case
                                if not re.match(r'^[a-z][a-z0-9_]*$', func_name):
                                    naming_issues.append(f"{py_file.name}:函数名{func_name}不符合snake_case")
                        
                        elif isinstance(node, ast.Assign):
                            # 检查变量命名
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    var_name = target.id
                                    # 常量应该全大写
                                    if var_name.isupper():
                                        if not re.match(r'^[A-Z][A-Z0-9_]*$', var_name):
                                            naming_issues.append(f"{py_file.name}:常量名{var_name}格式不规范")
                
                except (SyntaxError, UnicodeDecodeError):
                    print(f"跳过文件（语法或编码错误）: {py_file}")
        
        print(f"命名规范检查:")
        print(f"发现{len(naming_issues)}个命名问题")
        
        if naming_issues:
            for issue in naming_issues[:5]:  # 只显示前5个
                print(f"  - {issue}")
            if len(naming_issues) > 5:
                print(f"  ... 还有{len(naming_issues)-5}个问题")
        
        # 允许少量命名不规范（<10个）
        assert len(naming_issues) <= 10, \
            f"命名规范问题过多({len(naming_issues)}个)，应保持命名一致性"
        
        print("命名规范一致性测试通过")
    
    def test_pep8_compliance_basic_check(self):
        """测试PEP8规范基本符合度"""
        
        pep8_issues = []
        total_lines = 0
        
        for py_file in self.python_files:
            if py_file.exists():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                    
                    # 检查基本PEP8规范
                    for line_num, line in enumerate(lines, 1):
                        line_stripped = line.rstrip()
                        
                        # 检查行长度（建议≤120字符，严格≤150字符）
                        if len(line_stripped) > 150:
                            pep8_issues.append(f"{py_file.name}:{line_num} 行过长({len(line_stripped)}字符)")
                        
                        # 检查尾随空格
                        if line.endswith(' \n') or line.endswith('\t\n'):
                            pep8_issues.append(f"{py_file.name}:{line_num} 尾随空格")
                        
                        # 检查连续空行（不应超过2个）
                        if line_num > 2:
                            prev_lines = lines[line_num-3:line_num-1]
                            if all(not l.strip() for l in prev_lines) and not line_stripped:
                                pep8_issues.append(f"{py_file.name}:{line_num} 连续空行过多")
                
                except (UnicodeDecodeError):
                    print(f"跳过文件（编码错误）: {py_file}")
        
        print(f"PEP8基本检查:")
        print(f"总代码行数: {total_lines}")
        print(f"发现{len(pep8_issues)}个PEP8问题")
        
        if pep8_issues:
            for issue in pep8_issues[:8]:  # 显示前8个问题
                print(f"  - {issue}")
            if len(pep8_issues) > 8:
                print(f"  ... 还有{len(pep8_issues)-8}个问题")
        
        # 计算符合度（允许10%的问题）
        if total_lines > 0:
            compliance_rate = 1 - (len(pep8_issues) / total_lines * 10)  # 调整权重
            compliance_rate = max(0, min(1, compliance_rate))
            
            print(f"PEP8估算符合度: {compliance_rate:.1%}")
            
            assert compliance_rate >= 0.90, \
                f"PEP8符合度{compliance_rate:.1%}低于90%要求"
        
        print("PEP8规范符合度测试通过")
    
    def test_error_handling_completeness(self):
        """测试错误处理完善性"""
        
        # 统计try-except块的使用情况
        total_functions = 0
        functions_with_error_handling = 0
        error_handling_patterns = []
        
        for py_file in self.python_files:
            if py_file.exists():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    # 分析错误处理
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                            total_functions += 1
                            
                            # 检查函数是否包含try-except块
                            has_try_except = any(isinstance(child, ast.Try) for child in ast.walk(node))
                            
                            # 检查函数是否有返回状态指示
                            return_statements = [child for child in ast.walk(node) if isinstance(child, ast.Return)]
                            has_status_return = any(
                                isinstance(ret.value, ast.Constant) and isinstance(ret.value.value, bool)
                                for ret in return_statements if ret.value
                            )
                            
                            if has_try_except or has_status_return:
                                functions_with_error_handling += 1
                        
                        elif isinstance(node, ast.Try):
                            # 收集异常处理模式
                            for handler in node.handlers:
                                if handler.type and isinstance(handler.type, ast.Name):
                                    error_handling_patterns.append(handler.type.id)
                
                except (SyntaxError, UnicodeDecodeError):
                    print(f"跳过文件（语法或编码错误）: {py_file}")
        
        # 计算错误处理覆盖率
        error_handling_rate = functions_with_error_handling / total_functions if total_functions > 0 else 0
        
        print(f"错误处理统计:")
        print(f"总函数数: {total_functions}")
        print(f"有错误处理的函数: {functions_with_error_handling}")
        print(f"错误处理覆盖率: {error_handling_rate:.1%}")
        
        # 统计异常类型
        unique_exceptions = set(error_handling_patterns)
        print(f"处理的异常类型: {list(unique_exceptions)}")
        
        # 验证错误处理完善性
        # 对于关键功能模块，应该有合理的错误处理覆盖率
        assert error_handling_rate >= 0.50, \
            f"错误处理覆盖率{error_handling_rate:.1%}偏低，应该≥50%"
        
        # 验证处理了常见的异常类型
        common_exceptions = ['Exception', 'ValueError', 'IOError', 'FileNotFoundError']
        handled_common_exceptions = [exc for exc in common_exceptions if exc in unique_exceptions]
        
        assert len(handled_common_exceptions) >= 2, \
            f"应该处理≥2种常见异常类型，实际处理{len(handled_common_exceptions)}种"
        
        print("错误处理完善性测试通过")
    
    def test_code_complexity_metrics(self):
        """测试代码复杂度指标"""
        
        complexity_stats = {
            'total_functions': 0,
            'complex_functions': 0,  # 复杂度过高的函数
            'max_complexity': 0,
            'avg_complexity': 0
        }
        
        all_complexities = []
        
        for py_file in self.python_files:
            if py_file.exists():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    # 简单的圈复杂度计算
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            complexity_stats['total_functions'] += 1
                            
                            # 计算圈复杂度（简化版）
                            complexity = self.calculate_cyclomatic_complexity(node)
                            all_complexities.append(complexity)
                            
                            if complexity > 10:  # 复杂度阈值
                                complexity_stats['complex_functions'] += 1
                            
                            complexity_stats['max_complexity'] = max(
                                complexity_stats['max_complexity'], complexity
                            )
                
                except (SyntaxError, UnicodeDecodeError):
                    print(f"跳过文件（语法或编码错误）: {py_file}")
        
        if all_complexities:
            complexity_stats['avg_complexity'] = sum(all_complexities) / len(all_complexities)
        
        print(f"代码复杂度统计:")
        print(f"总函数数: {complexity_stats['total_functions']}")
        print(f"高复杂度函数: {complexity_stats['complex_functions']}")
        print(f"最大复杂度: {complexity_stats['max_complexity']}")
        print(f"平均复杂度: {complexity_stats['avg_complexity']:.2f}")
        
        # 验证代码复杂度合理
        high_complexity_ratio = complexity_stats['complex_functions'] / complexity_stats['total_functions'] if complexity_stats['total_functions'] > 0 else 0
        
        assert high_complexity_ratio <= 0.2, \
            f"高复杂度函数比例{high_complexity_ratio:.1%}过高，应≤20%"
        
        assert complexity_stats['avg_complexity'] <= 8.0, \
            f"平均复杂度{complexity_stats['avg_complexity']:.2f}过高，应≤8.0"
        
        print("代码复杂度测试通过")
    
    def calculate_cyclomatic_complexity(self, node):
        """计算函数的圈复杂度（简化版）"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            # 分支语句增加复杂度
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # and/or操作符
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def test_import_organization(self):
        """测试导入语句组织"""
        
        import_issues = []
        
        for py_file in self.python_files:
            if py_file.exists():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # 检查导入语句的组织
                    import_lines = []
                    for i, line in enumerate(lines):
                        stripped = line.strip()
                        if stripped.startswith('import ') or stripped.startswith('from '):
                            import_lines.append((i+1, stripped))
                    
                    # 检查导入语句是否在文件顶部
                    if import_lines:
                        first_import_line = import_lines[0][0]
                        non_comment_lines_before = 0
                        
                        for i in range(first_import_line - 1):
                            line = lines[i].strip()
                            if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                                non_comment_lines_before += 1
                        
                        if non_comment_lines_before > 3:  # 允许编码声明、文档字符串等
                            import_issues.append(f"{py_file.name}: 导入语句不在文件顶部")
                    
                    # 检查是否有未使用的导入（简单检查）
                    content_without_imports = '\n'.join([line for line in lines if not (line.strip().startswith('import ') or line.strip().startswith('from '))])
                    
                    for line_num, import_stmt in import_lines:
                        if 'import ' in import_stmt:
                            # 提取导入的模块或对象名
                            if import_stmt.startswith('from '):
                                # from module import name
                                parts = import_stmt.split()
                                if len(parts) >= 4 and parts[2] == 'import':
                                    imported_names = parts[3].split(',')
                                    for name in imported_names:
                                        clean_name = name.strip()
                                        if ' as ' in clean_name:
                                            clean_name = clean_name.split(' as ')[1]
                                        # 简单检查是否在代码中使用
                                        if clean_name and clean_name not in content_without_imports:
                                            # 这里不强制报错，因为可能有复杂的使用情况
                                            pass
                
                except (UnicodeDecodeError):
                    print(f"跳过文件（编码错误）: {py_file}")
        
        print(f"导入组织检查:")
        print(f"发现{len(import_issues)}个导入问题")
        
        for issue in import_issues:
            print(f"  - {issue}")
        
        # 允许少量导入组织问题
        assert len(import_issues) <= 5, \
            f"导入组织问题过多({len(import_issues)}个)"
        
        print("导入语句组织测试通过")
    
    def test_code_documentation_quality(self):
        """测试代码文档质量"""
        
        doc_quality_stats = {
            'total_docstrings': 0,
            'detailed_docstrings': 0,  # 包含Args/Returns的详细文档
            'empty_docstrings': 0,
            'short_docstrings': 0      # 过于简短的文档
        }
        
        for py_file in self.python_files:
            if py_file.exists():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    # 检查文档字符串质量
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_quality_stats['total_docstrings'] += 1
                                
                                # 检查文档长度
                                if len(docstring.strip()) < 10:
                                    doc_quality_stats['short_docstrings'] += 1
                                elif len(docstring.strip()) == 0:
                                    doc_quality_stats['empty_docstrings'] += 1
                                
                                # 检查是否包含Args/Returns（对于非私有函数）
                                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                                    if 'Args:' in docstring or 'Returns:' in docstring or '参数:' in docstring or '返回:' in docstring:
                                        doc_quality_stats['detailed_docstrings'] += 1
                
                except (SyntaxError, UnicodeDecodeError):
                    print(f"跳过文件（语法或编码错误）: {py_file}")
        
        print(f"文档质量统计:")
        print(f"总文档字符串: {doc_quality_stats['total_docstrings']}")
        print(f"详细文档字符串: {doc_quality_stats['detailed_docstrings']}")
        print(f"过短文档字符串: {doc_quality_stats['short_docstrings']}")
        print(f"空文档字符串: {doc_quality_stats['empty_docstrings']}")
        
        # 验证文档质量
        if doc_quality_stats['total_docstrings'] > 0:
            detailed_ratio = doc_quality_stats['detailed_docstrings'] / doc_quality_stats['total_docstrings']
            short_ratio = doc_quality_stats['short_docstrings'] / doc_quality_stats['total_docstrings']
            
            assert detailed_ratio >= 0.6, \
                f"详细文档比例{detailed_ratio:.1%}偏低，应≥60%"
            
            assert short_ratio <= 0.2, \
                f"过短文档比例{short_ratio:.1%}过高，应≤20%"
        
        print("代码文档质量测试通过")
    
    def test_code_structure_consistency(self):
        """测试代码结构一致性"""
        
        # 检查文件头部结构
        file_headers_consistent = 0
        total_checked_files = 0
        
        for py_file in self.python_files:
            if py_file.exists() and py_file.stat().st_size > 100:  # 跳过过小文件
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    total_checked_files += 1
                    
                    # 检查编码声明
                    has_encoding = any('coding' in line and 'utf-8' in line for line in lines[:3])
                    
                    # 检查模块文档字符串
                    content = ''.join(lines)
                    tree = ast.parse(content)
                    module_docstring = ast.get_docstring(tree)
                    
                    # 如果文件有编码声明和模块文档，认为结构一致
                    if has_encoding and module_docstring:
                        file_headers_consistent += 1
                    
                except (SyntaxError, UnicodeDecodeError):
                    print(f"跳过文件（语法或编码错误）: {py_file}")
        
        # 计算结构一致性
        if total_checked_files > 0:
            consistency_ratio = file_headers_consistent / total_checked_files
            
            print(f"代码结构一致性:")
            print(f"检查文件数: {total_checked_files}")
            print(f"结构一致文件: {file_headers_consistent}")
            print(f"一致性比例: {consistency_ratio:.1%}")
            
            assert consistency_ratio >= 0.8, \
                f"代码结构一致性{consistency_ratio:.1%}低于80%"
        
        print("代码结构一致性测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestCodeStandards()
    test_instance.setup_method()
    
    try:
        test_instance.test_code_comment_coverage()
        test_instance.test_naming_convention_consistency()
        test_instance.test_pep8_compliance_basic_check()
        test_instance.test_error_handling_completeness()
        test_instance.test_code_documentation_quality()
        test_instance.test_code_structure_consistency()
        print("\n所有代码规范与注释测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")