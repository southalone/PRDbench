#!/usr/bin/env python3
import re
import sys
import os
import json
import ast
import shutil

# 推荐：安装 json5 和 yaml 库
try:
    import json5
except ImportError:
    json5 = None
    print("⚠️  未安装 json5 库，运行 'pip install json5' 安装。")

try:
    import yaml
except ImportError:
    yaml = None
    print("⚠️  未安装 yaml 库，运行 'pip install pyyaml' 安装。")

def convert_to_standard_json(text):
    """
    修复 JSON 引号 + 用 json5/yaml 预处理
    """
    # 只匹配 {} 或 [] 包裹的单引号内容
    pattern = r"'(\{.*?\}|\[.*?\])'"
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        # 1. 替换内部单引号为双引号
        fixed_inner = re.sub(r"(?<!\\)'", '"', match)
        # 2. 修复无效转义字符
        fixed_inner = re.sub(r"\\(?![\\\"ntrbf/])", r"\\\\", fixed_inner)
        # 3. 尝试用 ast.literal_eval 预处理
        try:
            parsed = ast.literal_eval(f"'{fixed_inner}'")
            fixed_inner = json.dumps(parsed, ensure_ascii=False, indent=2)
        except:
            pass
        # 4. 尝试用 json5 解析
        if json5:
            try:
                parsed = json5.loads(fixed_inner)
                fixed_inner = json.dumps(parsed, ensure_ascii=False, indent=2)
            except:
                pass
        # 5. 尝试用 yaml 解析
        if yaml:
            try:
                parsed = yaml.safe_load(fixed_inner)
                fixed_inner = json.dumps(parsed, ensure_ascii=False, indent=2)
            except:
                pass
        # 6. 用 json.loads 验证并格式化
        try:
            parsed = json.loads(fixed_inner)
            standard_json = json.dumps(parsed, ensure_ascii=False, indent=2)
            text = text.replace(f"'{match}'", standard_json)
        except json.JSONDecodeError as e:
            error_pos = e.pos
            context = fixed_inner[max(0, error_pos-100):error_pos+100]
            print(f"❌ JSON 解析失败：{e}")
            print(f"错误位置附近：{context}")
            sys.exit(1)
    
    return text

def fix_file_inplace(input_path, backup=True):
    """
    直接修改原文件
    - input_path: 输入文件路径
    - backup: 是否备份原文件
    """
    if not os.path.exists(input_path):
        print(f"错误：文件 '{input_path}' 不存在！")
        sys.exit(1)
    
    # 1. 备份原文件
    if backup:
        backup_path = f"{input_path}.bak"
        shutil.copy2(input_path, backup_path)
        print(f"✅ 已备份原文件：{backup_path}")
    
    # 2. 读取并修复
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = convert_to_standard_json(content)
    
    # 3. 直接覆盖原文件
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 已直接修改原文件：{input_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python fix_json_inplace.py <输入文件> [是否备份]")
        print("示例：")
        print("  python fix_json_inplace.py example.sh")
        print("  python fix_json_inplace.py example.sh no_backup")
        sys.exit(1)
    
    input_file = sys.argv[1]
    backup = True
    if len(sys.argv) > 2 and sys.argv[2] == "no_backup":
        backup = False
    
    fix_file_inplace(input_file, backup)
