import os
import shutil
import argparse

def check_query_response(query_response_path):
    """
    检查 query_response.json 文件内容：
    - 如果文件不存在，返回 False（不处理）
    - 如果文件包含 'network_error' 或 '已重试 4 次'，返回 True（需要清理）
    - 如果文件存在但不含 'exit_loop'，返回 True（需要清理）
    - 如果文件存在且包含 'exit_loop'，返回 False（保留）
    """
    if not os.path.exists(query_response_path):
        print(f"文件不存在: {query_response_path}")
        return False  # 不处理，跳过

    try:
        with open(query_response_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # 情况1：有错误标记，需要清理
            if 'network_error' in content or '已重试 4 次' in content or "会话时间已达到上限" in content:
                print(f"检测到错误内容，删除: {query_response_path}")
                return True

            # 情况2：没有 exit_loop，也需要清理
            if 'exit_loop' not in content:
                print(f"未找到 'exit_loop'，删除: {query_response_path}")
                return True

            # 情况3：包含 exit_loop，保留
            #print(f"包含 'exit_loop'，保留: {query_response_path}")
            return False

    except Exception as e:
        print(f"读取 {query_response_path} 时出错: {e}")
        return True  # 读取失败也视为需要清理（可选策略）


def clean_folder_except_evaluation(folder_path, keep_prd=False):
    """
    清理文件夹，保留 evaluation 文件夹；
    如果 keep_prd=True，则 src/PRD.md 也保留。
    """
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # 保留 evaluation 文件夹
        if item == 'evaluation' and os.path.isdir(item_path):
            continue

        # 如果需要保留 src/PRD.md
        if keep_prd and item == 'src' and os.path.isdir(item_path):
            for sub_item in os.listdir(item_path):
                sub_item_path = os.path.join(item_path, sub_item)
                if sub_item != 'PRD.md':
                    if os.path.isfile(sub_item_path) or os.path.islink(sub_item_path):
                        os.remove(sub_item_path)
                    elif os.path.isdir(sub_item_path):
                        shutil.rmtree(sub_item_path)
            continue

        # 删除其他所有文件和文件夹
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def copy_template_except_evaluation(template_path, target_folder_path):
    """
    从模板复制内容到目标文件夹，跳过 evaluation 文件夹。
    """
    print(template_path)
    for item in os.listdir(template_path):
        if item == 'evaluation':
            continue
        src_item = os.path.join(template_path, item)
        dst_item = os.path.join(target_folder_path, item)
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dst_item)
        else:
            shutil.copy2(src_item, dst_item)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量检测并清理 1-50 号文件夹')
    parser.add_argument('--base_dir', type=str, required=True, help='工作目录的路径')
    parser.add_argument('--template_dir', type=str, default=None, help='模板目录（可选）')
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    template_path = os.path.abspath(args.template_dir) if args.template_dir else None

    for i in range(1, 51):
        folder_path = os.path.join(base_dir, str(i))
        query_response_path = os.path.join(folder_path, 'query_response.json')

        # 检查是否需要清理
        if check_query_response(query_response_path) or not os.path.exists(folder_path):
            print(f"开始清理文件夹: {folder_path}")
            if template_path:
                # 使用模板恢复（保留 evaluation）
                clean_folder_except_evaluation(folder_path)
                copy_template_except_evaluation(os.path.join(template_path, str(i)), folder_path)
                print(f"已从模板恢复: {folder_path}")
            else:
                # 仅保留 evaluation 和 src/PRD.md
                clean_folder_except_evaluation(folder_path, keep_prd=True)
                print(f"已清理（保留 evaluation 和 PRD.md）: {folder_path}")
        else:
            print(f"跳过（保留）: {folder_path}")
