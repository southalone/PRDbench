#!/usr/bin/env python3
import os
import sys
import shutil
import argparse


def copy_project_files(source_dir, target_dir):
    """
    复制项目文件夹中的特定文件和目录到目标路径

    Args:
        source_dir: 原文件路径
        target_dir: 目标路径
    """
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

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
        # eval_dir_source = os.path.join(project_source_path, "evaluation")
        # eval_dir_target = os.path.join(project_target_path, "evaluation")

        # if os.path.exists(eval_dir_source):
        #     # 复制整个 evaluation 目录
        #     shutil.copytree(eval_dir_source, eval_dir_target)
        #     print(f"已复制 {project}/evaluation 目录")
        # else:
        #     print(f"警告: {project} 中不存在 evaluation 目录")

def main():
    parser = argparse.ArgumentParser(description='复制项目文件夹中的特定文件和目录')
    parser.add_argument('source_dir', help='原文件路径')
    parser.add_argument('target_dir', help='目标路径')

    args = parser.parse_args()

    if not os.path.exists(args.source_dir):
        print(f"错误: 源目录 '{args.source_dir}' 不存在")
        sys.exit(1)

    copy_project_files(args.source_dir, args.target_dir)
    print("复制完成!")

if __name__ == "__main__":
    main()
