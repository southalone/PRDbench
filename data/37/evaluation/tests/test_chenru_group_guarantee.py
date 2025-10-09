import sys
import os
# 添加src目录到Python路径，以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from lottery_system.models import User, Prize
from lottery_system.services.lottery_manager import LotteryManager


def test_chenru_group_guarantee_mechanism():
    """
    测试程茹分组保障兜底机制：
    当马家旗抽奖且前两轮都没有程茹分组成员中奖时，
    应强制限定奖池为程茹分组成员，即使奖品设置了避让程茹分组。
    """
    # 准备测试数据：创建包含程茹分组和其他分组的用户
    users = [
        User("张三", "技术部"),
        User("李四", "产品部"), 
        User("王五", "市场部"),
        User("程茹", "程茹分组"),
        User("陈启显", "程茹分组"),
        User("金舵", "程茹分组")
    ]
    
    # 创建抽奖管理器实例
    lottery_manager = LotteryManager(users)
    
    # 模拟前两次抽奖都没有程茹分组成员中奖的情况
    lottery_manager.last_two_draw_results = [False, False]
    
    # 创建一个由"马家旗"抽奖且避让"程茹分组"的奖品
    prize_majiaqi = Prize(
        name="测试奖品C", 
        quantity=1,
        avoid_groups=["程茹分组"],  # 设置避让程茹分组
        associated_drawer="马家旗"
    )
    
    # 获取符合条件的奖池
    eligible_pool = lottery_manager._get_eligible_pool(prize_majiaqi)
    
    # 断言：尽管奖品设置了避让程茹分组，但由于兜底机制，
    # 奖池应该只包含程茹分组成员
    assert len(eligible_pool) == 3  # 应该有3个程茹分组成员
    assert all(user.department == "程茹分组" for user in eligible_pool)
    
    # 验证返回的用户名单
    expected_names = {"程茹", "陈启显", "金舵"}
    actual_names = {user.name for user in eligible_pool}
    assert actual_names == expected_names


def test_chenru_group_guarantee_not_triggered():
    """
    测试程茹分组保障机制不被触发的情况：
    当前面的抽奖有程茹分组成员中奖时，兜底机制不应被触发。
    """
    users = [
        User("张三", "技术部"),
        User("程茹", "程茹分组")
    ]
    
    lottery_manager = LotteryManager(users)
    
    # 模拟前两次抽奖中有程茹分组成员中奖的情况
    lottery_manager.last_two_draw_results = [False, True]  # 第二次有程茹分组中奖
    
    # 创建由"马家旗"抽奖且避让"程茹分组"的奖品
    prize_majiaqi = Prize(
        name="测试奖品", 
        quantity=1,
        avoid_groups=["程茹分组"],
        associated_drawer="马家旗"
    )
    
    # 获取符合条件的奖池
    eligible_pool = lottery_manager._get_eligible_pool(prize_majiaqi)
    
    # 断言：兜底机制不被触发，避让规则正常生效
    # 应该只有技术部的张三符合条件
    assert len(eligible_pool) == 1
    assert eligible_pool[0].name == "张三"
    assert eligible_pool[0].department == "技术部"


def test_chenru_group_guarantee_no_chenru_members():
    """
    测试当没有程茹分组成员时，兜底机制的行为。
    """
    users = [
        User("张三", "技术部"),
        User("李四", "产品部")
    ]
    
    lottery_manager = LotteryManager(users)
    lottery_manager.last_two_draw_results = [False, False]
    
    prize_majiaqi = Prize(
        name="测试奖品", 
        quantity=1,
        avoid_groups=[],
        associated_drawer="马家旗"
    )
    
    eligible_pool = lottery_manager._get_eligible_pool(prize_majiaqi)
    
    # 断言：由于没有程茹分组成员，兜底机制不生效，
    # 返回正常的奖池
    assert len(eligible_pool) == 2
    expected_names = {"张三", "李四"}
    actual_names = {user.name for user in eligible_pool}
    assert actual_names == expected_names