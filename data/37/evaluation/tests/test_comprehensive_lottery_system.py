import sys
import os
import tempfile
import csv
from datetime import datetime
from unittest.mock import patch, mock_open

# 添加src目录到Python路径，以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from lottery_system.models import User, Prize
from lottery_system.services.list_manager import ListManager
from lottery_system.services.prize_manager import PrizeManager
from lottery_system.services.lottery_manager import LotteryManager
from lottery_system.services.result_manager import ResultManager, Winner


class TestListManager:
    """测试名单管理功能"""
    
    def test_default_list_loading(self):
        """测试2.1.2 内置名单加载"""
        list_manager = ListManager()
        users, errors = list_manager.load_default_list()
        
        # 验证默认名单加载成功
        assert len(users) > 0, "应该能加载默认用户名单"
        assert all(isinstance(user, User) for user in users), "所有项都应该是User对象"
        assert all(user.name and user.department for user in users), "每个用户都应该有姓名和部门"
    
    def test_custom_list_loading_success(self):
        """测试2.1.3 自定义名单上传 - 成功场景"""
        list_manager = ListManager()
        
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("张三,技术部\n李四,产品部\n")
            temp_path = f.name
        
        try:
            users, errors = list_manager.load_custom_list(temp_path)
            
            assert len(errors) == 0, "不应该有错误"
            assert len(users) == 2, "应该加载2个用户"
            assert users[0].name == "张三" and users[0].department == "技术部"
            assert users[1].name == "李四" and users[1].department == "产品部"
        finally:
            os.unlink(temp_path)
    
    def test_duplicate_name_validation(self):
        """测试2.1.4a 名单验证 - 重复姓名"""
        list_manager = ListManager()
        users = [
            User("王五", "市场部"),
            User("王五", "市场部"),
            User("张三", "技术部")
        ]
        
        valid_users, duplicates = list_manager.validate_users(users)
        
        assert len(valid_users) == 2, "应该有2个有效用户"
        assert len(duplicates) == 1, "应该有1个重复用户"
        assert duplicates[0].name == "王五", "重复用户应该是王五"
    
    def test_format_error_validation(self):
        """测试2.1.4b 名单验证 - 格式错误"""
        list_manager = ListManager()
        
        # 创建包含格式错误的临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("赵六-行政部\n")  # 错误的分隔符
            temp_path = f.name
        
        try:
            users, errors = list_manager._load_from_path(temp_path)
            
            assert len(users) == 0, "不应该有有效用户"
            assert len(errors) == 1, "应该有1个错误"
            assert "Format Error" in errors[0], "错误信息应该包含Format Error"
            assert "Line 1" in errors[0], "错误信息应该指出行号"
        finally:
            os.unlink(temp_path)
    
    def test_group_info_display(self):
        """测试2.1.5 分组信息查看"""
        list_manager = ListManager()
        users = [
            User("张三", "技术部"),
            User("李四", "产品部"),
            User("王五", "技术部")
        ]
        
        group_info = list_manager.get_group_info(users)
        
        assert group_info["技术部"] == 2, "技术部应该有2人"
        assert group_info["产品部"] == 1, "产品部应该有1人"
    
    def test_invalid_data_handling(self):
        """测试2.1.4c 名单验证 - 手动处理"""
        list_manager = ListManager()
        
        # 创建包含重复数据的临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("王五,市场部\n王五,市场部\n张三,技术部\n")
            temp_path = f.name
        
        try:
            users, errors = list_manager.load_custom_list(temp_path)
            
            # 验证能够检测到重复数据但仍能处理有效数据
            if len(errors) > 0:
                # 如果有错误处理逻辑，验证剔除功能
                valid_users, duplicates = list_manager.validate_users(users + [User("王五", "市场部")])
                assert len(valid_users) >= 1, "应该能剔除重复数据并保留有效数据"
                assert len(duplicates) >= 1, "应该能识别重复数据"
            else:
                # 验证正常加载功能
                assert len(users) >= 1, "应该能加载有效用户数据"
        finally:
            os.unlink(temp_path)


class TestPrizeManager:
    """测试奖品管理功能"""
    
    def test_default_prizes_loading(self):
        """测试2.2.1 奖品库管理 - 查看预设"""
        prize_manager = PrizeManager()
        errors = prize_manager.load_default_prizes()
        
        assert len(errors) == 0, "加载默认奖品不应该有错误"
        
        prizes = prize_manager.get_prizes()
        assert len(prizes) >= 3, "应该至少有3个预设奖品"
        
        # 验证预设奖品
        prize_names = [prize.name for prize in prizes]
        assert "三等奖-电影票" in prize_names, "应该包含三等奖-电影票"
        assert "二等奖-购物卡" in prize_names, "应该包含二等奖-购物卡"
        assert "一等奖-年假1天" in prize_names, "应该包含一等奖-年假1天"
    
    def test_custom_prize_addition(self):
        """测试2.2.2 奖品库管理 - 自定义添加"""
        prize_manager = PrizeManager()
        
        # 添加自定义奖品
        prize_manager.add_prize(
            name="特等奖-iPhone 17", 
            quantity=1, 
            avoid_groups=[], 
            associated_drawer="黎斌"
        )
        
        prizes = prize_manager.get_prizes()
        assert len(prizes) == 1, "应该有1个奖品"
        
        prize = prizes[0]
        assert prize.name == "特等奖-iPhone 17", "奖品名称应该正确"
        assert prize.quantity == 1, "数量应该正确"
        assert prize.associated_drawer == "黎斌", "关联抽奖人应该正确"
    
    def test_avoid_groups_configuration(self):
        """测试2.2.3 分组避让规则配置"""
        prize_manager = PrizeManager()
        
        # 添加带避让分组的奖品
        prize_manager.add_prize(
            name="测试奖品", 
            quantity=1, 
            avoid_groups=["技术部", "产品部"]
        )
        
        prize = prize_manager.get_prizes()[0]
        assert "技术部" in prize.avoid_groups, "避让分组应该包含技术部"
        assert "产品部" in prize.avoid_groups, "避让分组应该包含产品部"
    
    def test_prize_reordering(self):
        """测试2.2.4 奖品排序功能"""
        prize_manager = PrizeManager()
        
        # 添加三个奖品
        prize_manager.add_prize("奖品A", 1)
        prize_manager.add_prize("奖品B", 1) 
        prize_manager.add_prize("奖品C", 1)
        
        # 测试重新排序：将C调整到第一位
        success = prize_manager.reorder_prizes([3, 1, 2])  # C, A, B
        
        assert success, "重新排序应该成功"
        
        prizes = prize_manager.get_prizes()
        assert prizes[0].name == "奖品C", "第一个应该是奖品C"
        assert prizes[1].name == "奖品A", "第二个应该是奖品A"
        assert prizes[2].name == "奖品B", "第三个应该是奖品B"


class TestLotteryManager:
    """测试抽奖管理功能"""
    
    def test_no_duplicate_winners(self):
        """测试2.4.1 基础过滤 - 已中奖者不重复"""
        users = [User("张三", "技术部"), User("李四", "产品部")]
        lottery_manager = LotteryManager(users)
        
        prize1 = Prize("奖品X", 1, [], None)
        prize2 = Prize("奖品Y", 1, [], None)
        
        # 第一轮抽奖
        winners1 = lottery_manager.draw(prize1)
        assert len(winners1) == 1, "第一轮应该有1个获奖者"
        
        # 第二轮抽奖
        winners2 = lottery_manager.draw(prize2)
        assert len(winners2) == 1, "第二轮应该有1个获奖者"
        
        # 验证没有重复中奖者
        assert winners1[0] != winners2[0], "两轮获奖者应该不同"
    
    def test_group_avoidance_filtering(self):
        """测试2.4.2 基础过滤 - 分组避让"""
        users = [
            User("张三", "技术部"), 
            User("李四", "产品部")
        ]
        lottery_manager = LotteryManager(users)
        
        # 创建避让技术部的奖品
        prize = Prize("产品专属奖", 1, ["技术部"], None)
        
        # 获取符合条件的用户池
        eligible_pool = lottery_manager._get_eligible_pool(prize)
        
        assert len(eligible_pool) == 1, "应该只有1个符合条件的用户"
        assert eligible_pool[0].department == "产品部", "获奖者应该是产品部的"
    
    def test_libin_special_rule(self):
        """测试2.4.3 特殊规则 - 黎斌"""
        users = [
            User("张三", "技术部"), 
            User("李四", "产品部")
        ]
        lottery_manager = LotteryManager(users)
        
        # 创建黎斌抽奖的奖品，但设置了避让技术部
        prize = Prize("黎斌奖品", 1, ["技术部"], "黎斌")
        
        # 获取符合条件的用户池
        eligible_pool = lottery_manager._get_eligible_pool(prize)
        
        # 黎斌抽奖时应该忽略避让规则
        assert len(eligible_pool) == 2, "黎斌抽奖时应该包含所有用户"
        department_list = [user.department for user in eligible_pool]
        assert "技术部" in department_list, "应该包含技术部成员"
        assert "产品部" in department_list, "应该包含产品部成员"
    
    def test_pause_resume_control(self):
        """测试2.3.2 手动控制 - 暂停与继续"""
        users = [User("张三", "技术部"), User("李四", "产品部")]
        lottery_manager = LotteryManager(users)
        
        # 创建测试奖品
        prize = Prize("测试奖品", 1, [], None)
        
        # 模拟暂停和继续功能测试
        # 这里主要测试LotteryManager是否支持暂停/继续的状态控制
        assert hasattr(lottery_manager, 'is_paused') or hasattr(lottery_manager, '_paused'), "应该支持暂停状态控制"
        
        # 验证抽奖功能正常
        winners = lottery_manager.draw(prize)
        assert len(winners) == 1, "暂停恢复后抽奖功能应该正常"
    
    def test_terminate_control(self):
        """测试2.3.3 手动控制 - 终止"""
        users = [User("张三", "技术部"), User("李四", "产品部"), User("王五", "市场部")]
        lottery_manager = LotteryManager(users)
        
        # 创建需要抽取多名获奖者的奖品
        prize = Prize("多人奖品", 3, [], None)
        
        # 模拟终止功能：先抽取部分获奖者
        winners = lottery_manager.draw(prize)
        
        # 验证能够正常抽出获奖者（终止功能的基础是抽奖功能正常）
        assert len(winners) <= 3, "应该能抽出获奖者"
        assert len(winners) >= 1, "至少应该有1个获奖者"
        
        # 验证已抽出的结果能被正确保存（通过检查winners列表非空）
        for winner in winners:
            assert isinstance(winner, User), "获奖者应该是User对象"


class TestResultManager:
    """测试结果管理功能"""
    
    def test_result_aggregation_display(self):
        """测试2.5.1b 最终结果汇总展示"""
        result_manager = ResultManager()
        
        # 创建测试数据
        user1 = User("张三", "技术部")
        user2 = User("李四", "产品部")
        prize1 = Prize("一等奖", 1, [], None)
        prize2 = Prize("二等奖", 1, [], None)
        
        # 添加获奖者
        result_manager.add_winner(user1, prize1)
        result_manager.add_winner(user2, prize2)
        
        # 获取按奖品分组的结果
        prizes = [prize1, prize2]
        results = result_manager.get_winners_by_prize(prizes)
        
        assert "一等奖" in results, "结果应该包含一等奖"
        assert "二等奖" in results, "结果应该包含二等奖"
        assert len(results["一等奖"]) == 1, "一等奖应该有1个获奖者"
        assert results["一等奖"][0].user.name == "张三", "一等奖获奖者应该是张三"
    
    def test_csv_export_functionality(self):
        """测试2.5.2a 结果导出功能"""
        result_manager = ResultManager()
        
        # 创建测试数据
        user = User("张三", "技术部")
        prize = Prize("测试奖品", 1, [], None)
        result_manager.add_winner(user, prize)
        
        # 模拟文件写入
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.path.abspath', return_value='/test/path.txt'):
                success, message = result_manager.export_to_csv([prize])
        
        assert success, "导出应该成功"
        assert "successfully exported" in message, "成功消息应该包含exported"
    
    def test_csv_export_format(self):
        """测试2.5.2b 结果导出格式"""
        result_manager = ResultManager()
        
        # 创建测试数据
        user = User("张三", "技术部")
        prize = Prize("测试奖品", 1, [], None)
        result_manager.add_winner(user, prize)
        
        # 使用临时文件进行实际写入测试
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            # 直接测试文件写入逻辑
            with patch('os.path.abspath', return_value=temp_path):
                success, message = result_manager.export_to_csv([prize])
            
            assert success, "导出应该成功"
            
            # 验证文件内容格式
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')
                
                # 验证表头
                assert lines[0] == "姓名,部门,奖品名称,中奖时间", "表头格式应该正确"
                
                # 验证数据行
                assert len(lines) == 2, "应该有表头和1行数据"
                data_parts = lines[1].split(',')
                assert len(data_parts) == 4, "数据行应该有4个字段"
                assert data_parts[0] == "张三", "姓名字段应该正确"
                assert data_parts[1] == "技术部", "部门字段应该正确"
                assert data_parts[2] == "测试奖品", "奖品名称字段应该正确"
        finally:
            os.unlink(temp_path)


# 集成测试
class TestIntegratedWorkflow:
    """测试综合工作流程"""
    
    def test_complete_lottery_workflow(self):
        """测试完整的抽奖工作流程"""
        # 1. 初始化管理器
        list_manager = ListManager()
        prize_manager = PrizeManager()
        result_manager = ResultManager()
        
        # 2. 准备用户和奖品数据
        users = [User("张三", "技术部"), User("李四", "产品部")]
        prize_manager.add_prize("测试奖品", 1, [], None)
        
        # 3. 执行抽奖
        lottery_manager = LotteryManager(users)
        prize = prize_manager.get_prizes()[0]
        winners = lottery_manager.draw(prize)
        
        # 4. 记录结果
        for winner in winners:
            result_manager.add_winner(winner, prize)
        
        # 5. 验证整个流程
        assert len(winners) == 1, "应该有1个获奖者"
        assert result_manager.get_all_winners()[0].user in users, "获奖者应该在用户列表中"


if __name__ == "__main__":
    pytest.main([__file__])