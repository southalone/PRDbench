#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件导出功能测试
File Export Function Tests
"""

import pytest
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.export_service import export_service
from services.trip_service import trip_service
from models.trip import TripPlan, TripStatus

class TestFileExport:
    """文件导出测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 创建测试行程
        self.test_trip = trip_service.create_new_trip("测试导出行程")
        trip_service.add_trip_segment("北京", "上海", 24.0)
        trip_service.add_trip_segment("上海", "广州", 12.0)
    
    def test_file_save_verification(self):
        """测试文件保存验证"""
        # 导出Markdown文件
        try:
            filepath = export_service.export_to_markdown(
                trip_service.current_trip, 
                "test_export"
            )
            
            # 验证文件是否存在
            assert os.path.exists(filepath), f"导出文件不存在: {filepath}"
            
            # 验证文件大小（调整为更合理的期望值）
            file_size = os.path.getsize(filepath)
            assert file_size > 500, f"文件大小过小: {file_size} bytes"
            
            # 验证文件可读性
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, "文件内容为空"
                assert "行程报告" in content or "测试导出行程" in content, "文件内容不正确"
            
            # 清理测试文件
            if os.path.exists(filepath):
                os.remove(filepath)
                
        except Exception as e:
            pytest.fail(f"文件导出测试失败: {e}")
    
    def test_markdown_export_content(self):
        """测试Markdown导出内容"""
        try:
            filepath = export_service.export_to_markdown(
                trip_service.current_trip,
                "content_test"
            )
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 验证必要内容
            assert "# " in content, "缺少Markdown标题"
            assert "北京" in content, "缺少出发城市信息"
            assert "上海" in content, "缺少目的地城市信息"
            assert "广州" in content, "缺少第二段目的地信息"
            
            # 清理测试文件
            if os.path.exists(filepath):
                os.remove(filepath)
                
        except Exception as e:
            pytest.fail(f"Markdown内容测试失败: {e}")
    
    def test_export_directory_creation(self):
        """测试导出目录创建"""
        # 测试导出到不存在的目录
        test_dir = "test_exports"
        full_test_dir = os.path.join("exports", test_dir)
        if os.path.exists(full_test_dir):
            import shutil
            shutil.rmtree(full_test_dir)
        
        try:
            filepath = export_service.export_to_markdown(
                trip_service.current_trip,
                f"{test_dir}/test_file"
            )
            
            # 验证目录和文件都被创建
            assert os.path.exists(full_test_dir), "导出目录未创建"
            assert os.path.exists(filepath), "导出文件未创建"
            
            # 清理测试目录
            if os.path.exists(full_test_dir):
                import shutil
                shutil.rmtree(full_test_dir)
                
        except Exception as e:
            pytest.fail(f"目录创建测试失败: {e}")

if __name__ == "__main__":
    pytest.main([__file__])