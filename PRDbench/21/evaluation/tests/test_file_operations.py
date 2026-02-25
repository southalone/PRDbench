# -*- coding: utf-8 -*-
"""
文件操作测试
"""

import sys
import os
import pytest
import re
import glob
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.lottery_engine import LotteryEngine
from modules.result_display import ResultDisplay
from utils.file_utils import FileUtils

class TestFileOperations:
    """文件操作测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = LotteryEngine()
        self.display = ResultDisplay()
        self.file_utils = FileUtils()
        
        # 清理之前的测试文件
        self.cleanup_test_files()
        
    def teardown_method(self):
        """测试后清理"""
        self.cleanup_test_files()
        
    def cleanup_test_files(self):
        """清理测试生成的文件"""
        # 删除所有抽奖结果文件
        pattern = "抽奖结果_*.txt"
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
            except:
                pass
                
    def test_filename_format(self):
        """测试文件名格式规范"""
        # 准备测试数据
        employees = [
            {'name': '张三', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': '李四', 'employee_id': '0101002', 'score': 92, 'tenure': 18}
        ]
        
        # 执行抽奖
        prizes = [
            {
                'name': '测试奖项',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]
        
        # 执行抽奖（禁用输出）
        import io
        import contextlib
        
        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)
        self.display.set_results(results)
        
        # 生成文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"抽奖结果_{timestamp}.txt"
        
        content = self.display.generate_report_content(employees)
        success = self.file_utils.save_text_file(filename, content)
        
        assert success, "文件保存失败"
        assert os.path.exists(filename), f"文件 {filename} 未生成"
        
        # 验证文件名格式
        pattern = r"^抽奖结果_\d{8}_\d{6}\.txt$"
        assert re.match(pattern, filename), f"文件名格式不正确：{filename}"
        
        # 验证日期时间格式
        date_part = filename.split('_')[1]  # YYYYMMDD
        time_part = filename.split('_')[2].replace('.txt', '')  # HHMMSS
        
        assert len(date_part) == 8, f"日期部分格式错误：{date_part}"
        assert len(time_part) == 6, f"时间部分格式错误：{time_part}"
        
        # 验证日期时间的有效性
        try:
            datetime.strptime(date_part, "%Y%m%d")
            datetime.strptime(time_part, "%H%M%S")
        except ValueError as e:
            pytest.fail(f"日期时间格式无效：{e}")
            
        print(f"文件名格式测试通过：{filename}")
        
    def test_file_content_completeness(self):
        """测试文件内容完整性"""
        # 准备测试数据
        employees = [
            {'name': '张三', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': '李四', 'employee_id': '0201002', 'score': 92, 'tenure': 18},
            {'name': '王五', 'employee_id': '0301003', 'score': 78, 'tenure': 36}
        ]
        
        # 执行抽奖
        prizes = [
            {
                'name': '一等奖',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            },
            {
                'name': '二等奖',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]
        
        # 执行抽奖（禁用输出）
        import io
        import contextlib
        
        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)
        self.display.set_results(results)
        
        # 生成报告内容
        content = self.display.generate_report_content(employees)
        
        # 验证报告内容完整性
        required_content = [
            "程青岛一区抽奖系统 - 抽奖结果报告",
            "生成时间：",
            "【抽奖结果】",
            "【公平性统计报告】",
            "积分分布Z检验：",
            "总体积分均值：",
            "部门分布卡方检验：",
            "报告结束"
        ]
        
        for item in required_content:
            assert item in content, f"报告内容缺少：{item}"
            
        # 验证中奖结果部分
        for prize_name in results.keys():
            assert prize_name in content, f"报告中缺少奖项：{prize_name}"
            
        # 验证统计数据
        assert "总体积分标准差：" in content, "缺少标准差信息"
        assert "Z统计量：" in content, "缺少Z统计量"
        assert "p值：" in content, "缺少p值"
        
        print("文件内容完整性测试通过")
        
    def test_file_save_functionality(self):
        """测试文件保存功能"""
        test_content = "这是一个测试文件内容\n包含中文字符\n测试UTF-8编码"
        test_filename = "test_save_功能测试.txt"
        
        # 测试保存功能
        success = self.file_utils.save_text_file(test_filename, test_content)
        assert success, "文件保存功能失败"
        assert os.path.exists(test_filename), "保存的文件不存在"
        
        # 验证文件内容
        with open(test_filename, 'r', encoding='utf-8') as f:
            saved_content = f.read()
            
        assert saved_content == test_content, "保存的文件内容不正确"
        
        # 清理测试文件
        os.remove(test_filename)
        
        print("文件保存功能测试通过")