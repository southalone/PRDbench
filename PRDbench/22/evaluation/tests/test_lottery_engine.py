import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from lottery_engine import LotteryEngine
from participant_manager import ParticipantManager
from lottery_config import LotteryConfigManager
from result_manager import ResultManager
from models import Participant, LotteryRoundConfig
import tempfile

class TestLotteryEngine:
    def setup_method(self):
        """在每个测试方法运行前执行的设置"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, "data")
        
        # 初始化各个模块
        self.participant_manager = ParticipantManager(data_dir=self.data_dir)
        self.config_manager = LotteryConfigManager(self.participant_manager, data_dir=self.data_dir)
        self.result_manager = ResultManager(data_dir=self.data_dir)
        self.lottery_engine = LotteryEngine(self.participant_manager, self.config_manager, self.result_manager)
        
        # 添加测试人员
        self.participant_manager.participants = [
            Participant(name="张三", department="技术部", weight=1.0),
            Participant(name="李四", department="技术部", weight=1.0),
            Participant(name="王五", department="市场部", weight=2.0),  # 高权重
            Participant(name="赵六", department="市场部", weight=1.0),
        ]
        
        # 添加测试轮次配置
        self.config_manager.rounds = [
            LotteryRoundConfig(
                round_id="round_1",
                name="测试轮次1",
                draw_count=1,
                scope_type="all",
                scope_value="",
                allow_repeat=False,
                participant_weights={}
            ),
            LotteryRoundConfig(
                round_id="round_2",
                name="测试轮次2",
                draw_count=2,
                scope_type="all",
                scope_value="",
                allow_repeat=True,
                participant_weights={}
            )
        ]

    def teardown_method(self):
        """在每个测试方法运行后执行的清理"""
        # 清理临时目录
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_weighted_probability(self):
        """测试权重应用准确性"""
        # 准备一个高权重人员
        round_config = LotteryRoundConfig(
            round_id="test_round",
            name="权重测试",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )
        
        # 多次执行抽奖
        high_weight_wins = 0
        total_runs = 1000
        
        for _ in range(total_runs):
            result = self.lottery_engine.execute_single_round(round_config)
            if result.winners[0]['name'] == "王五":  # 王五权重为2.0，其他人1.0
                high_weight_wins += 1
        
        # 断言高权重人员中奖频率显著更高
        # 理论上王五中奖概率约为2/(1+1+2+1) = 2/5 = 0.4
        # 其他人中奖概率约为1/5 = 0.2
        # 我们期望王五中奖次数显著高于其他人
        expected_high_weight_win_rate = 0.4
        actual_high_weight_win_rate = high_weight_wins / total_runs
        
        # 允许一定误差范围
        assert actual_high_weight_win_rate > expected_high_weight_win_rate * 0.8, \
            f"高权重人员中奖率未达到预期: 期望 > {expected_high_weight_win_rate * 0.8}, 实际 {actual_high_weight_win_rate}"
        
        print(f"高权重人员中奖率: {actual_high_weight_win_rate}")

    def test_no_repeat_logic(self):
        """测试禁止重复中奖逻辑"""
        # 配置一个两轮抽奖，第一轮抽取1人且模式为'禁止重复中奖'
        round1_config = LotteryRoundConfig(
            round_id="round_1",
            name="第一轮",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )
        
        # 第二轮抽取剩余人员
        round2_config = LotteryRoundConfig(
            round_id="round_2",
            name="第二轮",
            draw_count=3,  # 抽取剩余的3个人
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )
        
        # 执行第一轮抽奖
        result1 = self.lottery_engine.execute_single_round(round1_config)
        first_winner = result1.winners[0]['name']
        
        # 执行第二轮抽奖，传入第一轮中奖者名单
        result2 = self.lottery_engine.execute_single_round(round2_config, previous_winners=[first_winner])
        
        # 断言第二轮的中奖者列表中不包含第一轮的中奖者
        second_winners = [winner['name'] for winner in result2.winners]
        assert first_winner not in second_winners, \
            f"禁止重复中奖模式失效: 第一轮中奖者 {first_winner} 出现在第二轮中奖者列表中"
        
        print(f"第一轮中奖者: {first_winner}")
        print(f"第二轮中奖者: {second_winners}")
def test_weighted_probability():
    """测试权重应用准确性 - 独立函数版本"""
    import tempfile
    import shutil
    
    # 创建临时目录用于测试
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, "data")
    
    try:
        # 初始化各个模块
        participant_manager = ParticipantManager(data_dir=data_dir)
        config_manager = LotteryConfigManager(participant_manager, data_dir=data_dir)
        result_manager = ResultManager(data_dir=data_dir)
        lottery_engine = LotteryEngine(participant_manager, config_manager, result_manager)
        
        # 添加测试人员
        participant_manager.participants = [
            Participant(name="张三", department="技术部", weight=1.0),
            Participant(name="李四", department="技术部", weight=1.0),
            Participant(name="王五", department="市场部", weight=2.0),  # 高权重
            Participant(name="赵六", department="市场部", weight=1.0),
        ]
        
        # 准备一个高权重人员
        round_config = LotteryRoundConfig(
            round_id="test_round",
            name="权重测试",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )
        
        # 多次执行抽奖
        high_weight_wins = 0
        total_runs = 1000
        
        for _ in range(total_runs):
            result = lottery_engine.execute_single_round(round_config)
            if result.winners[0]['name'] == "王五":  # 王五权重为2.0，其他人1.0
                high_weight_wins += 1
        
        # 断言高权重人员中奖频率显著更高
        # 理论上王五中奖概率约为2/(1+1+2+1) = 2/5 = 0.4
        # 其他人中奖概率约为1/5 = 0.2
        # 我们期望王五中奖次数显著高于其他人
        expected_high_weight_win_rate = 0.4
        actual_high_weight_win_rate = high_weight_wins / total_runs
        
        # 允许一定误差范围
        assert actual_high_weight_win_rate > expected_high_weight_win_rate * 0.8, \
            f"高权重人员中奖率未达到预期: 期望 > {expected_high_weight_win_rate * 0.8}, 实际 {actual_high_weight_win_rate}"
        
        print(f"高权重人员中奖率: {actual_high_weight_win_rate}")
        
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir, ignore_errors=True)
def test_no_repeat_logic():
    """测试禁止重复中奖逻辑 - 独立函数版本"""
    import tempfile
    import shutil
    
    # 创建临时目录用于测试
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, "data")
    
    try:
        # 初始化各个模块
        participant_manager = ParticipantManager(data_dir=data_dir)
        config_manager = LotteryConfigManager(participant_manager, data_dir=data_dir)
        result_manager = ResultManager(data_dir=data_dir)
        lottery_engine = LotteryEngine(participant_manager, config_manager, result_manager)
        
        # 添加测试人员
        participant_manager.participants = [
            Participant(name="张三", department="技术部", weight=1.0),
            Participant(name="李四", department="技术部", weight=1.0),
            Participant(name="王五", department="市场部", weight=2.0),
            Participant(name="赵六", department="市场部", weight=1.0),
        ]
        
        # 配置一个两轮抽奖，第一轮抽取1人且模式为'禁止重复中奖'
        round1_config = LotteryRoundConfig(
            round_id="round_1",
            name="第一轮",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )
        
        # 第二轮抽取剩余人员
        round2_config = LotteryRoundConfig(
            round_id="round_2",
            name="第二轮",
            draw_count=3,  # 抽取剩余的3个人
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )
        
        # 执行第一轮抽奖
        result1 = lottery_engine.execute_single_round(round1_config)
        first_winner = result1.winners[0]['name']
        
        # 执行第二轮抽奖，传入第一轮中奖者名单
        result2 = lottery_engine.execute_single_round(round2_config, previous_winners=[first_winner])
        
        # 断言第二轮的中奖者列表中不包含第一轮的中奖者
        second_winners = [winner['name'] for winner in result2.winners]
        assert first_winner not in second_winners, \
            f"禁止重复中奖模式失效: 第一轮中奖者 {first_winner} 出现在第二轮中奖者列表中"
        
        print(f"第一轮中奖者: {first_winner}")
        print(f"第二轮中奖者: {second_winners}")
        
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir, ignore_errors=True)