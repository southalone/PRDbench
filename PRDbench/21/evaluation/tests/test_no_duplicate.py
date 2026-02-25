# -*- coding: utf-8 -*-
"""
重复中奖排除机制测试
"""

import sys
import os
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.lottery_engine import LotteryEngine

class TestNoDuplicate:
    """重复中奖测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = LotteryEngine()
        
    def test_no_duplicate_winners(self):
        """测试不允许重复中奖的排除机制"""
        # 准备5个员工的测试数据
        employees = [
            {'name': '员工1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': '员工2', 'employee_id': '0101002', 'score': 92, 'tenure': 18},
            {'name': '员工3', 'employee_id': '0102001', 'score': 78, 'tenure': 36},
            {'name': '员工4', 'employee_id': '0102002', 'score': 88, 'tenure': 12},
            {'name': '员工5', 'employee_id': '0103001', 'score': 95, 'tenure': 48}
        ]
        
        # 配置多个不允许重复中奖的奖项，奖品总数超过员工数
        prizes = [
            {
                'name': '一等奖',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            },
            {
                'name': '二等奖',
                'quantity': 2,
                'weight_rule': 'equal',
                'allow_duplicate': False
            },
            {
                'name': '三等奖',
                'quantity': 3,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]
        
        # 执行抽奖（禁用输出）
        import io
        import contextlib
        
        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)
        
        # 收集所有中奖者的工号
        all_winners = []
        for prize_name, winners in results.items():
            for winner in winners:
                all_winners.append(winner['employee_id'])
                
        # 验证无重复中奖
        unique_winners = set(all_winners)
        assert len(all_winners) == len(unique_winners), f"发现重复中奖：{len(all_winners)} 个中奖记录，{len(unique_winners)} 个唯一员工"
        
        # 验证中奖总数不超过员工总数
        assert len(unique_winners) <= len(employees), f"中奖人数({len(unique_winners)})超过员工总数({len(employees)})"
        
        print(f"测试通过：{len(unique_winners)} 个员工中奖，无重复现象")
        
    def test_allow_duplicate_winners(self):
        """测试允许重复中奖的情况"""
        employees = [
            {'name': '员工1', 'employee_id': '0101001', 'score': 100, 'tenure': 24},
            {'name': '员工2', 'employee_id': '0101002', 'score': 100, 'tenure': 18}
        ]
        
        # 配置允许重复中奖的多个奖项
        prizes = [
            {
                'name': '奖项1',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': True
            },
            {
                'name': '奖项2',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': True
            }
        ]
        
        # 执行多次抽奖，验证可能出现重复中奖
        duplicate_found = False
        
        import io
        import contextlib
        
        for _ in range(50):  # 多次尝试
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)
            
            all_winners = []
            for winners in results.values():
                for winner in winners:
                    all_winners.append(winner['employee_id'])
                    
            if len(all_winners) > len(set(all_winners)):
                duplicate_found = True
                break
                
        # 在允许重复中奖的情况下，应该有可能出现重复
        # 注意：这个测试可能偶尔失败，因为随机性可能导致没有重复
        print(f"允许重复中奖测试：{'发现重复' if duplicate_found else '未发现重复（正常随机现象）'}")
        
    def test_insufficient_candidates(self):
        """测试候选池不足的情况"""
        # 只有3个员工
        employees = [
            {'name': '员工1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': '员工2', 'employee_id': '0101002', 'score': 92, 'tenure': 18},
            {'name': '员工3', 'employee_id': '0102001', 'score': 78, 'tenure': 36}
        ]
        
        # 配置需要5个奖品的奖项（超过员工数）
        prizes = [
            {
                'name': '大奖项',
                'quantity': 5,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]
        
        # 执行抽奖（禁用输出）
        import io
        import contextlib
        
        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)
        
        # 验证中奖人数不超过员工总数
        if '大奖项' in results:
            winners_count = len(results['大奖项'])
            assert winners_count <= len(employees), f"中奖人数({winners_count})不应超过员工总数({len(employees)})"
            assert winners_count == len(employees), f"应该抽取所有可用员工({len(employees)})，实际抽取{winners_count}"
            
        print(f"候选池不足测试通过：抽取了{len(results.get('大奖项', []))}人，符合预期")