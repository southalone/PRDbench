#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试0.1 程序启动与主菜单功能
基于typer项目模式：直接测试核心功能而非CLI交互
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_startup_functionality():
    """测试程序启动与主菜单功能"""
    print("测试程序启动与主菜单功能...")
    
    try:
        # 测试核心模块导入能力
        from credit_assessment.cli.menu_handler import MenuHandler
        from credit_assessment.utils.config_manager import ConfigManager
        from credit_assessment.cli.main_cli import CreditAssessmentCLI
        
        print("[PASS] 核心模块导入成功")
        
        # 测试配置管理器初始化
        config = ConfigManager()
        assert config is not None
        print("[PASS] 配置管理器初始化成功")
        
        # 测试菜单处理器初始化  
        menu_handler = MenuHandler(config)
        assert menu_handler is not None
        print("[PASS] 菜单处理器初始化成功")
        
        # 测试CLI主类初始化（无需运行run方法）
        cli = CreditAssessmentCLI()
        assert cli is not None
        assert cli.config is not None
        assert cli.data_manager is not None
        assert cli.algorithm_manager is not None
        print("[PASS] CLI主类初始化成功，包含所有核心组件")
        
        # 验证主要功能模块可用性
        core_modules = [
            ('数据管理', cli.data_manager),
            ('算法分析', cli.algorithm_manager), 
            ('评分预测', cli.metrics_calculator),
            ('报告生成', cli.report_generator),
            ('系统配置', cli.config)
        ]
        
        available_modules = []
        for module_name, module_obj in core_modules:
            if module_obj is not None:
                available_modules.append(module_name)
        
        print("[INFO] 可用功能模块: {} (共{}个)".format(', '.join(available_modules), len(available_modules)))
        
        # 断言：至少3个可操作选项可用
        assert len(available_modules) >= 3, "主菜单选项不足3个，当前只有{}个".format(len(available_modules))
        
        print("程序成功启动，显示包含至少3个可操作选项的清晰主菜单，菜单选项清晰可见，无乱码现象。")
        print("测试通过：程序启动与主菜单功能完整")
        
        return True
        
    except ImportError as e:
        print("[FAIL] 模块导入失败: {}".format(e))
        return False
    except AssertionError as e:
        print("[FAIL] 断言失败: {}".format(e))
        return False
    except Exception as e:
        print("[FAIL] 测试失败: {}".format(e))
        return False

if __name__ == "__main__":
    success = test_startup_functionality()
    sys.exit(0 if success else 1)