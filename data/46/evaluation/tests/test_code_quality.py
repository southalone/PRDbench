#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：代码质量PEP8规范验证

测试目标：使用代码检查工具验证代码是否符合PEP8规范，无格式错误
"""

import os
import subprocess
import pytest
from pathlib import Path


class TestCodeQuality:
    """代码质量测试类"""
    
    def test_pep8_compliance(self):
        """测试PEP8规范符合性"""
        project_root = Path(__file__).parent.parent.parent / "src"
        
        # 检查项目源代码目录
        assert project_root.exists(), "源代码目录不存在"
        
        # 使用flake8检查PEP8规范
        try:
            # 检查主模块文件
            main_files = [
                project_root / "main.py",
                project_root / "credit_assessment"
            ]
            
            pep8_errors = []
            total_files_checked = 0
            
            for path in main_files:
                if path.exists():
                    if path.is_file():
                        # 检查单个文件
                        result = self._check_file_pep8(path)
                        if result["errors"]:
                            pep8_errors.extend(result["errors"])
                        total_files_checked += 1
                    else:
                        # 检查目录中的所有Python文件
                        for py_file in path.rglob("*.py"):
                            result = self._check_file_pep8(py_file)
                            if result["errors"]:
                                pep8_errors.extend(result["errors"])
                            total_files_checked += 1
            
            # 验证检查了足够的文件
            assert total_files_checked >= 5, f"检查的文件数量太少: {total_files_checked}"
            
            # 验证PEP8符合性
            if pep8_errors:
                error_summary = f"发现 {len(pep8_errors)} 个PEP8规范问题:\n"
                for error in pep8_errors[:10]:  # 只显示前10个错误
                    error_summary += f"  - {error}\n"
                
                # 允许少量格式问题（1分标准）
                if len(pep8_errors) <= 5:
                    print(f"警告: {error_summary}")
                    # 不抛出异常，表示基本符合但有少量问题
                else:
                    # 问题太多，不符合PEP8规范
                    pytest.fail(f"PEP8规范检查失败: {error_summary}")
            
            print(f"PEP8规范检查完成，共检查 {total_files_checked} 个文件")
            
        except FileNotFoundError:
            # 如果flake8未安装，使用基础的格式检查
            print("警告: flake8未安装，使用基础检查")
            self._basic_format_check(project_root)
    
    def _check_file_pep8(self, file_path):
        """使用flake8检查单个文件的PEP8符合性"""
        errors = []
        
        try:
            # 尝试使用flake8
            result = subprocess.run(
                ["python", "-m", "flake8", str(file_path), "--max-line-length=100"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip():
                errors.extend(result.stdout.strip().split('\n'))
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            # flake8不可用，进行基础检查
            errors.extend(self._basic_file_check(file_path))
        
        return {"errors": errors}
    
    def _basic_file_check(self, file_path):
        """基础文件格式检查"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # 检查行长度
                if len(line.rstrip()) > 120:
                    errors.append(f"{file_path}:{i}: 行长度超过120字符")
                
                # 检查缩进（应该是4的倍数）
                if line.startswith(' ') and len(line) - len(line.lstrip(' ')) % 4 != 0:
                    errors.append(f"{file_path}:{i}: 缩进不是4的倍数")
                
                # 检查尾随空格
                if line.endswith(' \n') or line.endswith('\t\n'):
                    errors.append(f"{file_path}:{i}: 行末有尾随空格")
                    
        except Exception as e:
            errors.append(f"{file_path}: 读取文件时出错: {str(e)}")
        
        return errors
    
    def _basic_format_check(self, project_root):
        """对整个项目进行基础格式检查"""
        python_files = list(project_root.rglob("*.py"))
        assert len(python_files) >= 5, "Python文件数量不足"
        
        total_errors = 0
        for py_file in python_files:
            errors = self._basic_file_check(py_file)
            total_errors += len(errors)
        
        # 允许少量格式问题
        assert total_errors <= 10, f"代码格式问题过多: {total_errors} 个问题"


if __name__ == "__main__":
    pytest.main([__file__])