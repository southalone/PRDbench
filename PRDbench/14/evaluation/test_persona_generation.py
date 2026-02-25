#!/usr/bin/env python3
"""
用户画像生成测试脚本
测试 [2.2.5 用户画像生成] 功能
"""

import subprocess
import json
import os
import sys
from pathlib import Path

def test_persona_generation():
    """测试用户画像生成功能"""
    print("🧪 开始测试用户画像生成功能...")
    
    # 1. 执行用户画像生成命令
    cmd = [
        "python", "-m", "src.main", "persona", "generate",
        "--from-cluster-results", "evaluation/reports/cluster/results.json",
        "--output-dir", "evaluation/reports/personas"
    ]
    
    print(f"📋 执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return False
        
        print("✅ 命令执行成功")
        print(f"输出: {result.stdout}")
        
        # 2. 检查期望的输出文件是否存在
        expected_files = [
            "evaluation/reports/personas/cluster_0.json",
            "evaluation/reports/personas/cluster_1.json", 
            "evaluation/reports/personas/cluster_2.json"
        ]
        
        for file_path in expected_files:
            if not os.path.exists(file_path):
                print(f"❌ 期望的输出文件不存在: {file_path}")
                return False
            print(f"✅ 文件存在: {file_path}")
        
        # 3. 验证文件内容结构
        for file_path in expected_files:
            if not validate_persona_file_structure(file_path):
                return False
        
        print("🎉 所有测试通过！用户画像生成功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False

def validate_persona_file_structure(file_path):
    """验证用户画像文件的结构"""
    print(f"🔍 验证文件结构: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查必需的字段
        required_fields = [
            'cluster_id',
            'cluster_name', 
            'sample_count',
            'demographics',
            'motivations',
            'consumption_patterns',
            'venue_preferences',
            'persona_summary'
        ]
        
        for field in required_fields:
            if field not in data:
                print(f"❌ 缺少必需字段: {field}")
                return False
        
        # 检查demographics子字段
        demographics_fields = ['gender_distribution', 'age_group_distribution']
        for field in demographics_fields:
            if field not in data['demographics']:
                print(f"❌ demographics中缺少字段: {field}")
                return False
        
        # 检查motivations子字段
        motivations_fields = ['price_sensitivity', 'satisfaction_level', 'amenities_importance']
        for field in motivations_fields:
            if field not in data['motivations']:
                print(f"❌ motivations中缺少字段: {field}")
                return False
        
        # 检查consumption_patterns子字段
        consumption_fields = ['frequency_distribution', 'dominant_frequency', 'spending_behavior']
        for field in consumption_fields:
            if field not in data['consumption_patterns']:
                print(f"❌ consumption_patterns中缺少字段: {field}")
                return False
        
        # 检查venue_preferences子字段
        venue_fields = ['preferred_venue_distribution', 'dominant_preference', 'preference_description']
        for field in venue_fields:
            if field not in data['venue_preferences']:
                print(f"❌ venue_preferences中缺少字段: {field}")
                return False
        
        print(f"✅ 文件结构验证通过: {file_path}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 文件验证失败: {e}")
        return False

if __name__ == "__main__":
    success = test_persona_generation()
    sys.exit(0 if success else 1)