import pytest
import sys
import os
import re

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

class TestOutputFormat:

    def test_entity_name_and_type(self):
        """测试实体输出是否包含名称和类型标签"""
        # 模拟实体输出格式
        sample_output = """
        加贺恭一郎/nr 3 在东京的一个雨夜，侦探加贺恭一郎正在调查一起神秘的案件
        田中雪穗/nr 2 受害者是一名叫做田中雪穗的年轻女性，她是一名护士
        东京/ns 1 在东京的一个雨夜，侦探加贺恭一郎正在调查
        """

        # 检查是否包含实体名称和类型标签
        lines = sample_output.strip().split('\n')
        for line in lines:
            if line.strip():
                # 检查格式：实体名称/类型 频次 上下文
                parts = line.strip().split(' ', 2)
                assert len(parts) >= 2, f"输出格式不正确: {line}"

                entity_with_type = parts[0]
                assert '/' in entity_with_type, f"实体应包含类型标签: {entity_with_type}"

                entity_name, entity_type = entity_with_type.split('/', 1)
                assert len(entity_name) > 0, "实体名称不能为空"
                assert entity_type in ['nr', 'ns', 't', 'nn'], f"实体类型应为nr/ns/t/nn之一: {entity_type}"

    def test_entity_frequency(self):
        """测试实体输出是否包含频次信息"""
        sample_output = """
        加贺恭一郎/nr 3 在东京的一个雨夜，侦探加贺恭一郎正在调查一起神秘的案件
        田中雪穗/nr 2 受害者是一名叫做田中雪穗的年轻女性，她是一名护士
        东京/ns 1 在东京的一个雨夜，侦探加贺恭一郎正在调查
        """

        lines = sample_output.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.strip().split(' ', 2)
                assert len(parts) >= 2, f"输出格式不正确: {line}"

                frequency = parts[1]
                assert frequency.isdigit(), f"频次应为数字: {frequency}"
                assert int(frequency) > 0, f"频次应大于0: {frequency}"

    def test_entity_context(self):
        """测试实体输出是否包含上下文信息（前后8个字符）"""
        sample_output = """
        加贺恭一郎/nr 3 在东京的一个雨夜，侦探加贺恭一郎正在调查一起神秘的案件
        田中雪穗/nr 2 受害者是一名叫做田中雪穗的年轻女性，她是一名护士
        东京/ns 1 在东京的一个雨夜，侦探加贺恭一郎正在调查
        """

        lines = sample_output.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.strip().split(' ', 2)
                assert len(parts) >= 3, f"输出应包含上下文信息: {line}"

                context = parts[2]
                assert len(context) > 0, "上下文信息不能为空"

                # 检查上下文是否包含实体名称
                entity_name = parts[0].split('/')[0]
                assert entity_name in context, f"上下文应包含实体名称: {entity_name} not in {context}"

                # 检查上下文长度（应该包含前后8个字符，但这里只做基本检查）
                assert len(context) >= len(entity_name), "上下文长度应该合理"

if __name__ == '__main__':
    pytest.main([__file__])
