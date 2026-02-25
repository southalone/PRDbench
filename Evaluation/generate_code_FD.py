import requests
import json
import os
import shutil
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("--local_port", type=str, default="5678")
parser.add_argument("--model_name", type=str, default="claude_3_7_sonnet")
parser.add_argument("--root_path", type=str, default='work/codex_dev_test')
parser.add_argument("--round", type=int, default=1)
parser.add_argument("--type", type=str, default="free")
parser.add_argument("--source_dir", type=str, default="PRD_bench/")
parser.add_argument("--i", type=int, default=1)
args = parser.parse_args()

code_path = args.root_path
source_dir = args.source_dir
local_port = args.local_port
model_name = args.model_name

def construct_session(session_id):
    session_query = {
        "url": f"http://localhost:{local_port}/apps/code_eval_agent/users/{model_name}/sessions/s_{session_id}",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        }
    }
    delete_query = {
        "url": f"http://localhost:{local_port}/apps/code_eval_agent/users/{model_name}/sessions/s_{session_id}",
        "method": "DELETE",
        "headers": {
            "Content-Type": "application/json"
        }
    }
    try:
        delete_response = requests.delete(delete_query["url"], headers=delete_query["headers"])
        print(f"删除会话响应状态码: {delete_response.status_code}")
        response = requests.post(session_query["url"], headers=session_query["headers"])
        print(f"创建会话响应状态码: {response.status_code}")
        print(f"创建会话响应内容: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"创建会话失败，状态码: {response.status_code}")
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return {"error": "network_error", "message": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应内容: {response.text}")
        return {"error": "json_decode_error", "text": response.text}

def make_query(prompt_data, session_id, max_retry=5):
    query_query = {
        "url": f"http://localhost:{local_port}/run",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "data": {
            "appName": f"code_eval_agent",
            "userId": model_name,
            "sessionId": f"s_{session_id}",
            "newMessage": {
                "role": "user",
                "parts": [{
                    "text": prompt_data
                }]
            }
        }
    }
    for attempt in range(max_retry):
        try:
            response = requests.post(query_query["url"], headers=query_query["headers"], json=query_query["data"])
            print(f"查询响应状态码: {response.status_code}")
            print(f"查询响应内容: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"查询失败，状态码: {response.status_code}")
                # 检查 token 上限相关错误并重试
                if "token" in response.text or "limit" in response.text:
                    print(f"检测到token相关错误，第{attempt+1}次重试")
                    time.sleep(3)
                    continue
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            time.sleep(2)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"响应内容: {str(response)}")
            time.sleep(2)
    return {"error": "max_retry_exceeded"}

def check_report_format(report_file):
    """
    检查评测报告 round.jsonl 是否符合标准格式
    返回 True 表示合规，False 表示不合规
    """
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return False
            # 标准数组
            if content.startswith('[') and content.endswith(']'):
                items = json.loads(content)
                valid_count = sum(1 for item in items if isinstance(item, dict) and 'score' in item)
                return valid_count > 0
            else:
                lines = [line for line in content.splitlines() if line.strip()]
                # JSONL 检查
                is_jsonl = True
                for line in lines:
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        is_jsonl = False
                        break
                if is_jsonl:
                    valid_count = sum(1 for line in lines
                                      if isinstance(json.loads(line), dict)
                                      and 'score' in json.loads(line))
                    return valid_count > 0
                else:
                    # 多行对象
                    objects = []
                    brace_depth = 0
                    obj_start = None
                    for i, c in enumerate(content):
                        if c == '{':
                            if brace_depth == 0:
                                obj_start = i
                            brace_depth += 1
                        elif c == '}':
                            brace_depth -= 1
                            if brace_depth == 0 and obj_start is not None:
                                obj_str = content[obj_start:i+1]
                                objects.append(obj_str)
                                obj_start = None
                    if len(objects) < 5:
                        return False
                    valid_count = sum(1 for obj_str in objects
                                      if isinstance(json.loads(obj_str), dict)
                                      and 'score' in json.loads(obj_str))
                    return valid_count > 0
    except Exception:
        return False


def run_evaluation(i, retry_round=0):
    print(f"\n=== 开始评测第 {i} 个项目 ===")
    path_suffix = i
    dir_path = os.path.join(code_path, str(path_suffix))
    project_dir = dir_path
    report_file = os.path.join(dir_path, "reports", f"round{args.round}.jsonl")
    log_file = os.path.join(dir_path, "reports", f"round{args.round}.log")

    # 检查项目目录是否存在
    if not os.path.exists(project_dir):
        print(f"警告: 项目目录 {project_dir} 不存在，跳过...")
        return False

    # 检查项目是否已经评测过
    if os.path.exists(report_file):
        print(f"项目 {i} 已经评测过，跳过...")
        return True

    report_dir = os.path.join(dir_path, "reports")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    eva_path = os.path.join(source_dir, str(i), "evaluation")
    eval_dir_source = eva_path
    eval_dir_target = os.path.join(dir_path, "evaluation")

    if os.path.exists(eval_dir_source):
        shutil.copytree(eval_dir_source, eval_dir_target, dirs_exist_ok=True)
        print(f"已复制 {i}/evaluation 目录")
    else:
        print(f"警告: {i} 中不存在 evaluation 目录")

    prompt_data = f"""### Task
Please evaluate the implementation of {project_dir} by running code-level tests and generating an evaluation report according to the evaluation criteria. The evaluation criteria are provided in evaluation/metric_en.json, and the project code is located in the src/ directory.

You should independently design and execute tests for each test point described in evaluation/metric_en.json. You may freely create auxiliary files, test scripts (such as pytest files), and input data as needed to thoroughly test the code against each metric. However, you must not modify the content of the metrics in evaluation/metric_en.json, nor alter any code in the {project_dir}/src/ directory.

### Path Instructions
- The project code is located in the {project_dir}/src/ directory. **DO NOT MODIFY THE PROJECT CODE.**
- The evaluation criteria are located in the {project_dir}/evaluation/metric_en.json file. **DO NOT MODIFY THE METRIC FILE.**
- You are allowed and encouraged to create or modify auxiliary files, test scripts, and input data under the {project_dir}/evaluation directory (excluding metric_en.json), to help you test the code against the evaluation criteria.
- The evaluation report must be saved to {project_dir}/reports/round{args.round}.jsonl in JSON format.

### Tips
- If the code is unable to run after reasonable testing efforts, please document this in the report.
- You may write and execute your own pytest scripts or other testing scripts to comprehensively evaluate the code according to each metric.
- You may prepare or generate any necessary input files or data for your tests, as long as you do not modify the metric_en.json or src code.

### Example
The detailed evaluation report must be saved to reports/round{args.round}.jsonl in JSON format. Entries in the report should follow this structure:
{{
"metric": "1.3 Menu Navigation - Export Results Submenu",
"description": "Test whether the export submenu displays the correct options when accessed.",
"score": 0,
"explanation": "No export submenu is present in the actual implementation. The code does not provide menu navigation functionality, so this feature could not be tested."
}},
{{
"metric": "3.2 Unit Test - Generate Huffman Codes",
"description": "Verify that the generate_huffman_codes function produces the expected encoding dictionary.",
"score": 2,
"explanation": "A custom pytest file was written to test generate_huffman_codes. The test passed and produced the expected results."
}}

For each metric in evaluation/metric_en.json, you must attempt to design and execute a test (using auxiliary scripts, pytest, or other methods as appropriate). Document your testing process, results, and any issues encountered in the evaluation report. Assign a score for each metric according to your findings.

### Final Reminder
You are free to create or modify any auxiliary files, input data, or test scripts within the evaluation directory (except metric_en.json) to facilitate comprehensive testing. **Do NOT modify the project code in src or the metrics in metric_en.json.**
For every metric, design and execute a test. If a feature is missing or incompatible, document this in the report and score accordingly. **Do not skip any metrics.**
The output report should be saved to {project_dir}/reports/round{args.round}.jsonl in JSON format.
""".strip()

    # session_id 唯一化
    session_id = f"{path_suffix}" if retry_round == 0 else f"{path_suffix}_{retry_round}"
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print(f"开始创建会话 session_id={session_id} ...")
    session_response = construct_session(session_id)

    print(f"开始发送查询...")
    query_response = make_query(prompt_data, session_id)

    # 保存日志
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(query_response, f, indent=2, ensure_ascii=False)

    print(f"dir_path: {dir_path}")
    print(f"=== 第 {i} 个项目评测完成 ===\n")
    return True

def check_all_reports_generated():
    for i in range(1, 51):
        dir_path = os.path.join(code_path, str(i))
        report_file = os.path.join(dir_path, "reports", f"round{args.round}.jsonl")
        if not os.path.exists(report_file):
            return False
    return True

# 记录每个项目的重试次数
retry_dict = {i: 0 for i in range(1, 51)}

def check_all_reports_generated_and_valid():
    for i in range(1, 51):
        dir_path = os.path.join(code_path, str(i))
        report_file = os.path.join(dir_path, "reports", f"round{args.round}.jsonl")
        if not os.path.exists(report_file) or not check_report_format(report_file):
            return False
    return True

# 首次评测
for i in range(1, 51):
    dir_path = os.path.join(code_path, str(i))
    report_file = os.path.join(dir_path, "reports", f"round{args.round}.jsonl")
    if os.path.exists(report_file) and check_report_format(report_file):
        print(f"项目 {i} 已有合规评测报告，跳过...")
        continue
    run_evaluation(i, retry_round=0)
print("所有50个项目初次评测完成！")

# 持续补漏重试，直到全部 jsonl 生成且合规，或重试次数达到3次
while not check_all_reports_generated_and_valid():
    print("\n=== 补漏重试轮次 ===")
    for i in range(1, 51):
        dir_path = os.path.join(code_path, str(i))
        report_file = os.path.join(dir_path, "reports", f"round{args.round}.jsonl")
        log_file = os.path.join(dir_path, "reports", f"round{args.round}.log")
        if not os.path.exists(dir_path):
            print(f"补漏检测: 项目目录 {dir_path} 不存在，跳过...")
            continue
        # 检查合规性
        need_retry = False
        if not os.path.exists(report_file):
            need_retry = True
            print(f"补漏检测: 项目 {i} 缺少评测报告，准备重试...")
        elif not check_report_format(report_file):
            need_retry = True
            print(f"补漏检测: 项目 {i} 评测报告格式不合规，准备重试...")
            os.remove(report_file)
            print(f"已删除不合规报告 {report_file}")
        if need_retry:
            if retry_dict[i] >= 3:
                print(f"项目 {i} 已重试3次，跳过后续重试！")
                continue
            retry_dict[i] += 1
            if os.path.exists(log_file):
                os.remove(log_file)
                print(f"已删除 {log_file}")
            run_evaluation(i, retry_round=retry_dict[i])
        else:
            print(f"补漏检测: 项目 {i} 评测报告已存在且合规，跳过...")
print("所有项目的 jsonl 文件都已生成且合规，补漏重试结束！")
