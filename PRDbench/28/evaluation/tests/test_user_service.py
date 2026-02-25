# -*- coding: utf-8 -*-
"""
用户服务单元测试
"""

import pytest
import sys
import os
import hashlib

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from services.user_service import UserService


class TestUserService:
    """用户服务测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.user_service = UserService()
    
    def test_hash_password_consistency(self):
        """测试密码哈希一致性"""
        password = "test123456"
        hash1 = self.user_service.hash_password(password)
        hash2 = self.user_service.hash_password(password)
        
        # 相同密码应产生相同哈希
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256产生64字符的十六进制字符串
    
    def test_hash_password_different_inputs(self):
        """测试不同密码产生不同哈希"""
        password1 = "password123"
        password2 = "password456"
        
        hash1 = self.user_service.hash_password(password1)
        hash2 = self.user_service.hash_password(password2)
        
        # 不同密码应产生不同哈希
        assert hash1 != hash2
    
    def test_hash_password_empty_string(self):
        """测试空字符串密码哈希"""
        empty_password = ""
        hash_result = self.user_service.hash_password(empty_password)
        
        # 空字符串也应该能正常哈希
        assert len(hash_result) == 64
        assert isinstance(hash_result, str)
    
    def test_hash_password_special_characters(self):
        """测试包含特殊字符的密码哈希"""
        special_password = "p@ssw0rd!@#$%^&*()"
        hash_result = self.user_service.hash_password(special_password)
        
        # 特殊字符密码应能正常哈希
        assert len(hash_result) == 64
        assert isinstance(hash_result, str)
    
    def test_hash_password_chinese_characters(self):
        """测试包含中文字符的密码哈希"""
        chinese_password = "密码123中文"
        hash_result = self.user_service.hash_password(chinese_password)
        
        # 中文密码应能正常哈希
        assert len(hash_result) == 64
        assert isinstance(hash_result, str)
    
    def test_hash_password_long_string(self):
        """测试长密码字符串哈希"""
        long_password = "a" * 1000  # 1000个字符的密码
        hash_result = self.user_service.hash_password(long_password)
        
        # 长密码应能正常哈希
        assert len(hash_result) == 64
        assert isinstance(hash_result, str)
    
    def test_hash_password_correctness(self):
        """测试密码哈希正确性"""
        password = "test123"
        expected_hash = hashlib.sha256(password.encode()).hexdigest()
        actual_hash = self.user_service.hash_password(password)
        
        # 哈希结果应与预期一致
        assert actual_hash == expected_hash
    
    def test_hash_password_case_sensitivity(self):
        """测试密码哈希大小写敏感性"""
        password_lower = "password"
        password_upper = "PASSWORD"
        password_mixed = "Password"
        
        hash_lower = self.user_service.hash_password(password_lower)
        hash_upper = self.user_service.hash_password(password_upper)
        hash_mixed = self.user_service.hash_password(password_mixed)
        
        # 不同大小写应产生不同哈希
        assert hash_lower != hash_upper
        assert hash_lower != hash_mixed
        assert hash_upper != hash_mixed
    
    def test_hash_password_numeric_strings(self):
        """测试纯数字密码哈希"""
        numeric_passwords = ["123456", "0000", "999999999"]
        
        for password in numeric_passwords:
            hash_result = self.user_service.hash_password(password)
            assert len(hash_result) == 64
            assert isinstance(hash_result, str)
            
            # 验证每个数字密码都产生不同的哈希
            for other_password in numeric_passwords:
                if password != other_password:
                    other_hash = self.user_service.hash_password(other_password)
                    assert hash_result != other_hash
    
    def test_hash_password_whitespace_handling(self):
        """测试包含空白字符的密码处理"""
        password_with_spaces = "pass word"
        password_with_tabs = "pass\tword"
        password_with_newlines = "pass\nword"
        
        hash_spaces = self.user_service.hash_password(password_with_spaces)
        hash_tabs = self.user_service.hash_password(password_with_tabs)
        hash_newlines = self.user_service.hash_password(password_with_newlines)
        
        # 不同的空白字符应产生不同的哈希
        assert hash_spaces != hash_tabs
        assert hash_spaces != hash_newlines
        assert hash_tabs != hash_newlines
        
        # 所有哈希都应该有效
        assert len(hash_spaces) == 64
        assert len(hash_tabs) == 64
        assert len(hash_newlines) == 64


if __name__ == "__main__":
    pytest.main([__file__])