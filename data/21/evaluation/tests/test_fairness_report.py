# -*- coding: utf-8 -*-
"""
公平性报告测试
"""

import sys
import os
import pytest
import numpy as np
from io import StringIO
from contextlib import redirect_stdout

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.result_display import ResultDisplay
from modules.lottery_engine import LotteryEngine

class TestFairnessReport:
    """公平性报告测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.display = ResultDisplay()
        self.engine = LotteryEngine()
        
    def test_statistical_tests(self):
        """测试Z检验和卡方检验实现"""
        # 准备多部门员工数据
        employees = [
            {'name': '部门01员工1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': '部门01员工2', 'employee_id': '0101002', 'score': 92, 'tenure': 18},
            {'name': '部门01员工3', 'employee_id': '0101003', 'score': 88, 'tenure': 30},
            {'name': '部门02员工1', 'employee_id': '0201001', 'score': 78, 'tenure': 36},
            {'name': '部门02员工2', 'employee_id': '0201002', 'score': 90, 'tenure': 12},
            {'name': '部门03员工1', 'employee_id': '0301001', 'score': 95, 'tenure': 48}
        ]
        
        # 模拟抽奖结果
        mock_results = {
            '测试奖项': [
                {'name': '部门01员工1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
                {'name': '部门02员工1', 'employee_id': '0201001', 'score': 78, 'tenure': 36}
            ]
        }
        
        self.display.set_results(mock_results)
        
        # 捕获输出
        output = StringIO()
        with redirect_stdout(output):
            self.display.display_fairness_report(employees)
            
        output_text = output.getvalue()
        
        # 验证Z检验相关输出
        assert "积分分布Z检验" in output_text, "缺少Z检验标题"
        assert "总体积分均值" in output_text, "缺少总体积分均值"
        assert "Z统计量" in output_text, "缺少Z统计量"
        assert "p值" in output_text, "缺少p值"
        assert ("统计结果符合随机性要求" in output_text or "统计结果显示可能存在偏差" in output_text), "缺少统计结论"
        
        # 验证卡方检验相关输出
        assert "部门分布卡方检验" in output_text, "缺少卡方检验标题"
        assert "总体占比" in output_text, "缺少总体占比信息"
        assert "中奖占比" in output_text, "缺少中奖占比信息"
        assert ("卡方统计量" in output_text or "χ²" in output_text), "缺少卡方统计量"
        
        print("Z检验和卡方检验实现测试通过")
        
    def test_randomness_marking(self):
        """测试随机性自动标记功能"""
        # 使用不同积分的员工，确保能进行Z检验
        employees = [
            {'name': f'员工{i}', 'employee_id': f'010100{i}', 'score': 80 + i*2, 'tenure': 24}
            for i in range(1, 21)  # 20个员工，积分不同
        ]
        
        # 模拟抽奖结果
        mock_results = {
            '随机奖项': [
                {'name': '员工1', 'employee_id': '0101001', 'score': 82, 'tenure': 24},
                {'name': '员工2', 'employee_id': '0101002', 'score': 84, 'tenure': 24},
                {'name': '员工3', 'employee_id': '0101003', 'score': 86, 'tenure': 24}
            ]
        }
        
        self.display.set_results(mock_results)
        
        # 生成报告内容
        report_content = self.display.generate_report_content(employees)
        
        # 验证随机性标记存在（由于有Z检验结果）
        has_z_test = "Z统计量：" in report_content
        if has_z_test:
            assert "统计结果符合随机性要求" in report_content or "统计结果显示可能存在偏差" in report_content, "缺少随机性判断标记"
            
            # 验证p值判断逻辑
            lines = report_content.split('\n')
            p_value_lines = [line for line in lines if 'p值：' in line]
            
            if len(p_value_lines) > 0:
                # 检查是否有对应的随机性标记
                for p_line in p_value_lines:
                    # 提取p值
                    try:
                        p_value_str = p_line.split('p值：')[1].strip()
                        p_value = float(p_value_str)
                        
                        # 根据p值检查是否有对应的标记
                        if p_value > 0.05:
                            assert "统计结果符合随机性要求" in report_content, f"p值{p_value}大于0.05但缺少随机性标记"
                        else:
                            assert "统计结果显示可能存在偏差" in report_content, f"p值{p_value}小于等于0.05但缺少偏差标记"
                            
                    except (ValueError, IndexError):
                        continue  # 跳过无法解析的行
        else:
            # 如果没有Z检验，至少应该有报告结构
            assert "【公平性统计报告】" in report_content, "缺少公平性报告部分"
                
        print("随机性自动标记功能测试通过")
        
    def test_report_content_completeness(self):
        """测试报告内容完整性"""
        employees = [
            {'name': '张三', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': '李四', 'employee_id': '0201002', 'score': 92, 'tenure': 18}
        ]
        
        mock_results = {
            '一等奖': [{'name': '张三', 'employee_id': '0101001', 'score': 85, 'tenure': 24}],
            '二等奖': [{'name': '李四', 'employee_id': '0201002', 'score': 92, 'tenure': 18}]
        }
        
        self.display.set_results(mock_results)
        
        # 生成完整报告
        report_content = self.display.generate_report_content(employees)
        
        # 验证报告结构完整性
        required_sections = [
            "程青岛一区抽奖系统 - 抽奖结果报告",
            "生成时间：",
            "【抽奖结果】",
            "一等奖",
            "二等奖", 
            "【公平性统计报告】",
            "积分分布Z检验：",
            "部门分布卡方检验：",
            "报告结束"
        ]
        
        for section in required_sections:
            assert section in report_content, f"报告缺少必需部分：{section}"
            
        print("报告内容完整性测试通过")