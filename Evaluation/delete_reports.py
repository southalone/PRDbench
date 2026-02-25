#!/usr/bin/env python3
import os
import shutil
import argparse
import sys

def delete_reports_folders(base_dir, folder_ids=None):
    """
    删除指定ID的子文件夹中的reports文件夹

    Args:
        base_dir: 基础目录路径
        folder_ids: 要处理的文件夹ID列表，如果为None则处理所有ID

    Returns:
        deleted_count: 删除的文件夹数量
    """
    # 检查基础目录是否存在
    if not os.path.exists(base_dir):
        print(f"错误: 基础目录 '{base_dir}' 不存在")
        return 0

    # 计数器
    deleted_count = 0

    print(f"开始在 '{base_dir}' 中查找并删除reports文件夹...")

    # 如果没有指定ID，则获取所有数字命名的子文件夹
    if folder_ids is None:
        folder_ids = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item.isdigit():
                folder_ids.append(item)

    # 处理每个指定的文件夹ID
    for folder_id in folder_ids:
        folder_path = os.path.join(base_dir, str(folder_id))

        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            print(f"警告: ID为 {folder_id} 的文件夹不存在，跳过")
            continue

        # 检查reports文件夹是否存在
        reports_path = os.path.join(folder_path, "reports")
        if os.path.exists(reports_path):
            try:
                # 删除reports文件夹
                shutil.rmtree(reports_path)
                print(f"已删除: {reports_path}")
                deleted_count += 1
            except Exception as e:
                print(f"删除 '{reports_path}' 时出错: {e}")
        else:
            print(f"ID {folder_id} 的文件夹中没有reports文件夹，跳过")

    print(f"\n操作完成! 共删除了 {deleted_count} 个reports文件夹")
    return deleted_count

def parse_folder_ids(ids_str):
    """
    解析文件夹ID字符串，支持范围表示法
    例如: "1,3-5,7,10-12" 将被解析为 [1,3,4,5,7,10,11,12]

    Args:
        ids_str: ID字符串，如 "1,3-5,7,10-12"

    Returns:
        folder_ids: 解析后的ID列表
    """
    folder_ids = []

    # 分割逗号分隔的部分
    parts = ids_str.split(',')

    for part in parts:
        part = part.strip()

        # 处理范围 (例如 "3-5")
        if '-' in part:
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                folder_ids.extend(range(start, end + 1))
            except ValueError:
                print(f"警告: 无法解析ID范围 '{part}'，跳过")

        # 处理单个ID
        else:
            try:
                folder_ids.append(int(part))
            except ValueError:
                print(f"警告: 无法解析ID '{part}'，跳过")

    return sorted(folder_ids)

def main():
    parser = argparse.ArgumentParser(description='删除指定ID的子文件夹中的reports文件夹')
    parser.add_argument('-d', '--directory', required=True,
                        help='基础目录路径')
    parser.add_argument('-i', '--ids',
                        help='要处理的文件夹ID，可以是单个ID、逗号分隔的ID列表或范围 (例如: "1,3-5,7,10-12")，如果不指定则处理所有ID')

    args = parser.parse_args()

    # 解析文件夹ID
    folder_ids = None
    if args.ids:
        folder_ids = [str(id) for id in parse_folder_ids(args.ids)]
        print(f"将处理以下ID的文件夹: {folder_ids}")
    else:
        print("将处理所有ID的文件夹")

    delete_reports_folders(args.directory, folder_ids)

if __name__ == "__main__":
    main()
