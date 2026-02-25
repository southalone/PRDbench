#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import json

def copy_project_files(source_dir, target_dir, aux_data_path=None):
    """
    复制项目文件夹中的特定文件和目录到目标路径

    Args:
        source_dir: 原文件路径
        target_dir: 目标路径
        aux_data_path: aux_data.json 文件路径，用于复制额外文件
    """
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 读取 aux_data.json 文件
    aux_data = {}
    if aux_data_path and os.path.exists(aux_data_path):
        try:
            with open(aux_data_path, 'r', encoding='utf-8') as f:
                aux_data = json.load(f)
            print(f"已加载额外数据文件: {aux_data_path}")
        except Exception as e:
            print(f"警告: 无法读取 aux_data.json 文件: {e}")
    elif aux_data_path:
        print(f"警告: aux_data.json 文件不存在: {aux_data_path}")

    # 获取源目录下的所有项目文件夹
    projects = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]

    print(f"找到 {len(projects)} 个项目文件夹")

    for project in projects:
        project_source_path = os.path.join(source_dir, project)
        project_target_path = os.path.join(target_dir, project)

        # 创建项目目标目录
        if not os.path.exists(project_target_path):
            os.makedirs(project_target_path)

        # 复制 src/PRD.md 或 src/prd.md 文件
        src_dir_source = os.path.join(project_source_path, "src")
        src_dir_target = os.path.join(project_target_path, "src")

        if os.path.exists(src_dir_source):
            # 检查 PRD.md 或 prd.md 是否存在
            prd_file = None
            if os.path.exists(os.path.join(src_dir_source, "PRD.md")):
                prd_file = "PRD.md"
            elif os.path.exists(os.path.join(src_dir_source, "prd.md")):
                prd_file = "prd.md"

            if prd_file:
                # 创建目标 src 目录
                if not os.path.exists(src_dir_target):
                    os.makedirs(src_dir_target)

                # 复制 PRD.md 文件
                shutil.copy2(
                    os.path.join(src_dir_source, prd_file),
                    os.path.join(src_dir_target, prd_file)
                )
                print(f"已复制 {project}/src/{prd_file}")
            else:
                print(f"警告: 在 {project}/src 中未找到 PRD.md 或 prd.md")
        else:
            print(f"警告: {project} 中不存在 src 目录")

        # 复制 evaluation 目录
        eval_dir_source = os.path.join(project_source_path, "evaluation")
        eval_dir_target = os.path.join(project_target_path, "evaluation")

        if os.path.exists(eval_dir_source):
            # 复制整个 evaluation 目录
            shutil.copytree(eval_dir_source, eval_dir_target)
            print(f"已复制 {project}/evaluation 目录")
        else:
            print(f"警告: {project} 中不存在 evaluation 目录")

        # 根据 aux_data.json 复制额外文件
        if aux_data and project in aux_data:
            extra_files = aux_data[project]
            if extra_files:
                for file_path in extra_files:
                    source_file = os.path.join(project_source_path, file_path)
                    target_file = os.path.join(project_target_path, file_path)
                    
                    if os.path.exists(source_file):
                        # 创建目标文件的目录
                        target_file_dir = os.path.dirname(target_file)
                        if target_file_dir and not os.path.exists(target_file_dir):
                            os.makedirs(target_file_dir)
                        
                        # 如果是目录，使用 copytree；如果是文件，使用 copy2
                        if os.path.isdir(source_file):
                            if os.path.exists(target_file):
                                shutil.rmtree(target_file)
                            shutil.copytree(source_file, target_file)
                            print(f"已复制 {project}/{file_path} (目录)")
                        else:
                            shutil.copy2(source_file, target_file)
                            print(f"已复制 {project}/{file_path}")
                    else:
                        print(f"警告: 额外文件不存在: {project}/{file_path}")

def main():
    parser = argparse.ArgumentParser(description='复制项目文件夹中的特定文件和目录')
    parser.add_argument('source_dir', help='原文件路径')
    parser.add_argument('target_dir', help='目标路径')
    parser.add_argument('--aux_data', 
                       default='/work/Generation/aux_data.json',
                       help='aux_data.json 文件路径')

    args = parser.parse_args()

    if not os.path.exists(args.source_dir):
        print(f"错误: 源目录 '{args.source_dir}' 不存在")
        sys.exit(1)

    copy_project_files(args.source_dir, args.target_dir, args.aux_data)
    print("复制完成!")

if __name__ == "__main__":
    main()
