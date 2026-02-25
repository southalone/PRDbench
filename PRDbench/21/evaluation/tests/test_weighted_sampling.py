# -*- coding: utf-8 -*-
"""
加权随机抽样测试
"""

import sys
import os
import pytest
import numpy as np
from collections import Counter

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.lottery_engine import LotteryEngine

class TestWeightedSampling:
    """加权随机抽样测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = LotteryEngine()
        
    def test_score_weighted_lottery(self):
        """测试积分加权抽奖"""
        # 准备测试数据：明显的高积分和低积分员工
        employees = [
            {'name': '高积分员工1', 'employee_id': '0101001', 'score': 200, 'tenure': 24},
            {'name': '高积分员工2', 'employee_id': '0101002', 'score': 190, 'tenure': 18},
            {'name': '高积分员工3', 'employee_id': '0101003', 'score': 180, 'tenure': 36},
            {'name': '低积分员工1', 'employee_id': '0102001', 'score': 50, 'tenure': 12},
            {'name': '低积分员工2', 'employee_id': '0102002', 'score': 60, 'tenure': 30},
            {'name': '低积分员工3', 'employee_id': '0102003', 'score': 55, 'tenure': 15}
        ]
        
        # 配置积分加权奖项
        prizes = [
            {
                'name': '测试奖项',
                'quantity': 1,
                'weight_rule': 'score',
                'allow_duplicate': True
            }
        ]
        
        # 执行多次抽奖统计
        high_score_wins = 0
        low_score_wins = 0
        total_tests = 100
        
        # 临时禁用打印输出
        import io
        import contextlib
        
        for _ in range(total_tests):
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)
            if '测试奖项' in results and results['测试奖项']:
                winner = results['测试奖项'][0]
                if winner['score'] >= 180:
                    high_score_wins += 1
                elif winner['score'] <= 60:
                    low_score_wins += 1
                    
        # 验证高积分员工中奖频率明显高于低积分员工
        high_score_rate = high_score_wins / total_tests
        low_score_rate = low_score_wins / total_tests
        
        print(f"高积分员工中奖率: {high_score_rate:.2%}")
        print(f"低积分员工中奖率: {low_score_rate:.2%}")
        
        # 断言：高积分员工中奖率应该明显高于低积分员工
        # 考虑到随机性，要求高积分中奖率至少是低积分的1.5倍
        assert high_score_rate > low_score_rate * 1.5, f"加权效果不明显：高积分{high_score_rate:.2%} vs 低积分{low_score_rate:.2%}"
        
    def test_equal_weight_lottery(self):
        """测试平均权重抽奖"""
        employees = [
            {'name': '员工1', 'employee_id': '0101001', 'score': 100, 'tenure': 24},
            {'name': '员工2', 'employee_id': '0101002', 'score': 200, 'tenure': 18},
            {'name': '员工3', 'employee_id': '0101003', 'score': 50, 'tenure': 36}
        ]
        
        prizes = [
            {
                'name': '平均权重奖项',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': True
            }
        ]
        
        # 执行多次抽奖，验证每个员工中奖概率大致相等
        win_counts = Counter()
        total_tests = 300
        
        import io
        import contextlib
        
        for _ in range(total_tests):
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)
            if '平均权重奖项' in results and results['平均权重奖项']:
                winner_id = results['平均权重奖项'][0]['employee_id']
                win_counts[winner_id] += 1
                
        # 验证每个员工的中奖次数大致相等（允许35%的偏差）
        expected_wins = total_tests / len(employees)
        for emp_id, wins in win_counts.items():
            deviation = abs(wins - expected_wins) / expected_wins
            print(f"员工{emp_id}: {wins}次 (期望{expected_wins:.1f}次, 偏差{deviation:.1%})")
            assert deviation < 0.35, f"员工{emp_id}中奖次数偏差过大：{wins} vs 期望{expected_wins:.1f}"
            
    def test_tenure_weighted_lottery(self):
        """测试入职时长加权抽奖"""
        employees = [
            {'name': '老员工1', 'employee_id': '0101001', 'score': 100, 'tenure': 60},
            {'name': '老员工2', 'employee_id': '0101002', 'score': 100, 'tenure': 48},
            {'name': '新员工1', 'employee_id': '0102001', 'score': 100, 'tenure': 6},
            {'name': '新员工2', 'employee_id': '0102002', 'score': 100, 'tenure': 12}
        ]
        
        prizes = [
            {
                'name': '入职时长奖项',
                'quantity': 1,
                'weight_rule': 'tenure',
                'allow_duplicate': True
            }
        ]
        
        # 执行多次抽奖统计
        old_employee_wins = 0
        new_employee_wins = 0
        total_tests = 100
        
        import io
        import contextlib
        
        for _ in range(total_tests):
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)
            if '入职时长奖项' in results and results['入职时长奖项']:
                winner = results['入职时长奖项'][0]
                if winner['tenure'] >= 48:
                    old_employee_wins += 1
                elif winner['tenure'] <= 12:
                    new_employee_wins += 1
                    
        # 验证老员工中奖频率高于新员工
        old_rate = old_employee_wins / total_tests
        new_rate = new_employee_wins / total_tests
        
        print(f"老员工中奖率: {old_rate:.2%}")
        print(f"新员工中奖率: {new_rate:.2%}")
        
        assert old_rate > new_rate * 1.2, f"入职时长加权效果不明显：老员工{old_rate:.2%} vs 新员工{new_rate:.2%}"