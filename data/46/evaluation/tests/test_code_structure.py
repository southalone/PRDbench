#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：代码结构分层架构验证

测试目标：验证项目代码是否按照功能层/服务层/CLI层进行了清晰的分层架构设计
"""

import os
import pytest
from pathlib import Path


class TestCodeStructure:
    """代码结构测试类"""
    
    def test_layered_architecture(self):
        """测试分层架构设计"""
        project_root = Path(__file__).parent.parent.parent / "src"
        
        # 验证主要分层目录存在
        assert (project_root / "credit_assessment").exists(), "主模块目录不存在"
        
        # 验证功能层目录
        functional_dirs = [
            "data",          # 数据处理层
            "algorithms",    # 算法层  
            "evaluation",    # 评估层
            "utils"         # 工具层
        ]
        
        for dir_name in functional_dirs:
            dir_path = project_root / "credit_assessment" / dir_name
            assert dir_path.exists(), f"功能层目录 {dir_name} 不存在"
            assert (dir_path / "__init__.py").exists(), f"功能层目录 {dir_name} 缺少 __init__.py"
        
        # 验证服务层目录（business logic）
        service_dirs = ["algorithms", "data", "evaluation"]
        for dir_name in service_dirs:
            dir_path = project_root / "credit_assessment" / dir_name
            # 检查是否有业务逻辑文件
            py_files = list(dir_path.glob("*.py"))
            assert len(py_files) >= 2, f"服务层目录 {dir_name} 应包含至少2个Python文件（含__init__.py）"
        
        # 验证CLI层目录
        cli_dir = project_root / "credit_assessment" / "cli"
        assert cli_dir.exists(), "CLI层目录不存在"
        assert (cli_dir / "__init__.py").exists(), "CLI层目录缺少 __init__.py"
        assert (cli_dir / "main_cli.py").exists(), "CLI层缺少主CLI文件"
        
        # 验证目录分离清晰性
        # 数据处理功能应该在data目录
        data_files = list((project_root / "credit_assessment" / "data").glob("*.py"))
        data_related_files = [f for f in data_files if "data" in f.name.lower() or "preprocess" in f.name.lower()]
        assert len(data_related_files) >= 1, "数据层缺少数据处理相关文件"
        
        # 算法功能应该在algorithms目录  
        alg_files = list((project_root / "credit_assessment" / "algorithms").glob("*.py"))
        alg_related_files = [f for f in alg_files if "algorithm" in f.name.lower() or "regression" in f.name.lower() or "network" in f.name.lower()]
        assert len(alg_related_files) >= 1, "算法层缺少算法相关文件"
        
        # CLI功能应该在cli目录
        cli_files = list((project_root / "credit_assessment" / "cli").glob("*.py"))
        cli_related_files = [f for f in cli_files if "cli" in f.name.lower() or "menu" in f.name.lower()]
        assert len(cli_related_files) >= 1, "CLI层缺少命令行相关文件"


if __name__ == "__main__":
    # 允许直接运行此测试文件
    pytest.main([__file__])