#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正导入问题的辅助脚本

由于src/credit_assessment/utils/__init__.py没有导出LoggerMixin，
我们在evaluation目录创建一个修正脚本来解决导入问题
"""

import sys
import os
from pathlib import Path

# 添加src路径到系统路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 直接从logger模块导入LoggerMixin并添加到utils命名空间
try:
    from credit_assessment.utils.logger import LoggerMixin, OperationLogger
    import credit_assessment.utils as utils_module
    
    # 动态添加LoggerMixin到utils模块
    setattr(utils_module, 'LoggerMixin', LoggerMixin)
    setattr(utils_module, 'OperationLogger', OperationLogger)
    
    print("成功修正LoggerMixin导入问题")
    
except ImportError as e:
    print(f"导入修正失败: {e}")

if __name__ == "__main__":
    print("LoggerMixin修正脚本执行完成")