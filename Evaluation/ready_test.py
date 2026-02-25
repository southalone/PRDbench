import requests
import json
import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
# for each prompt, I should first create a session, then send the query
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--local_port", type=str, default="8010")
parser.add_argument("--model_name", type=str, default="claude_3_7_sonnet")
parser.add_argument("--root_path", type=str, default='workspace/gemini_test')
parser.add_argument("--round", type=int, default=1)
parser.add_argument("--retry_count", type=int, default=2)
parser.add_argument("--max_workers", type=int, default=8, help="并行worker数量，建议4-8")


args = parser.parse_args()
code_path = args.root_path

local_port = args.local_port
model_name = args.model_name

def move_to_backup(file_path, backup_dir):
    if os.path.exists(file_path):
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        base_name = os.path.basename(file_path)
        backup_file = os.path.join(backup_dir, base_name)
        shutil.move(file_path, backup_file)
        print(f"Moved {file_path} to {backup_file}")

def construct_session(session_id):
    session_query = {
        "url": f"http://localhost:{local_port}/apps/code_eval_agent_workspace_dir/users/{model_name}/sessions/s_{session_id}",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        }
    }
    # delete session if it exists via curl -X DELETE
    delete_query = {
        "url": f"http://localhost:{local_port}/apps/code_eval_agent_workspace_dir/users/{model_name}/sessions/s_{session_id}",
        "method": "DELETE",
        "headers": {
            "Content-Type": "application/json"
        }
    }
    
    try:
        # Delete existing session
        delete_response = requests.delete(delete_query["url"], headers=delete_query["headers"])
        print(f"Delete session response status code: {delete_response.status_code}")
        
        # Create new session
        response = requests.post(session_query["url"], headers=session_query["headers"])
        print(f"Create session response status code: {response.status_code}")
        print(f"Create session response content: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Create session failed, status code: {response.status_code}")
            return response.json()
            
    except requests.exceptions.RequestException as e:
        print(f"Network request error: {e}")
        return {"error": "network_error", "message": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response content: {response.text}")
        return {"error": "json_decode_error", "text": response.text}

def make_query(prompt_data, session_id):
    query_query = {
        "url": f"http://localhost:{local_port}/run",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "data": {
            "appName": f"code_eval_agent_workspace_dir",
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
    
    try:
        response = requests.post(query_query["url"], headers=query_query["headers"], json=query_query["data"])
        print(f"Query response status code: {response.status_code}")
        print(f"Query response content: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Query failed, status code: {response.status_code}")
            return response.json()
            
    except requests.exceptions.RequestException as e:
        print(f"Network request error: {e}")
        return {"error": "network_error", "message": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response content: {str(response)}")
        return {"error": "json_decode_error", "text": str(response)}
    # todo if token limit occurs retry up to 5 times

def check_report_format(report_file):
    """
    Check if evaluation report round.jsonl conforms to standard format
    Returns True if compliant, False if non-compliant
    """
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return False
            # Standard array
            if content.startswith('[') and content.endswith(']'):
                items = json.loads(content)
                valid_count = sum(1 for item in items if isinstance(item, dict) and 'score' in item)
                return valid_count > 0
            else:
                lines = [line for line in content.splitlines() if line.strip()]
                # JSONL check
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
                    # Multi-line objects
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
                    if len(objects) < 3:
                        return False
                    valid_count = sum(1 for obj_str in objects
                                      if isinstance(json.loads(obj_str), dict)
                                      and 'score' in json.loads(obj_str))
                    return valid_count > 0
    except Exception:
        return False

def transfer_metric_abs_path(metric_data, project_dir):
    testcases = metric_data.get('testcases', [])
    for testcase in testcases:
        print(testcase)
        test_input = testcase.get('test_input', '')
        if test_input:
            test_input_path = os.path.join(project_dir, test_input)
            if os.path.exists(test_input_path):
                testcase['test_input'] = test_input_path
        test_command = testcase.get('test_command', '')
        if test_command:
            test_command = f'cd {project_dir} && ' + test_command
            testcase['test_command'] = test_command
    input_files = metric_data.get('input_files', [])
    new_input_files = []
    if input_files:
        for input_file in input_files:
            input_file_path = os.path.join(project_dir, input_file)
            if os.path.exists(input_file_path):
                new_input_files.append(input_file_path)
            else:
                new_input_files.append(input_file)
        metric_data['input_files'] = new_input_files
    return metric_data

# Loop evaluation of projects 1 to 50
def load_test_plan(test_plan_path):
    """加载detailed_test_plan.json文件"""
    try:
        with open(test_plan_path, 'r', encoding='utf-8') as f:
            test_plan = json.load(f)
        return test_plan
    except Exception as e:
        print(f"Error loading test plan from {test_plan_path}: {e}")
        return None

def get_completed_metrics(report_dir):
    """
    获取已经完成的评分项（检查reports目录下的非空且有效的JSON文件，且有score字段）。
    返回：
      - completed_metrics: set，已完成的评分项名
    """
    completed_metrics = set()
    reasons = {
        'file_empty': [],
        'invalid_json': [],
        'no_score_field': [],
        'other_error': []
    }

    if os.path.exists(report_dir):
        try:
            # 扫描reports目录下的所有.json文件
            for filename in os.listdir(report_dir):
                if not filename.endswith('.json'):
                    continue
                file_path = os.path.join(report_dir, filename)
                metric_name = filename[:-5]  # 去掉.json后缀

                # 1. 判断文件是否为空
                if os.path.getsize(file_path) == 0:
                    reasons['file_empty'].append({'metric': metric_name, 'file': file_path})
                    continue

                # 2. 读取并解析JSON
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if not content:
                        reasons['file_empty'].append({'metric': metric_name, 'file': file_path})
                        continue
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        reasons['invalid_json'].append({
                            'metric': metric_name,
                            'file': file_path,
                            'error': str(e),
                            'content_preview': content[:200]
                        })
                        # 检测到无效JSON，尝试删除该文件
                        try:
                            os.remove(file_path)
                        except Exception as del_e:
                            reasons['other_error'].append({
                                'metric': metric_name,
                                'file': file_path,
                                'error': f"Failed to delete invalid JSON file: {del_e}"
                            })
                        continue

                    # 3. 判断内容是否为空
                    if data == {} or data == []:
                        reasons['file_empty'].append({'metric': metric_name, 'file': file_path})
                        continue

                    # 4. 检查是否有score字段（假设评分项都要求有score）
                    if not isinstance(data, dict) or 'score' not in data:
                        reasons['no_score_field'].append({
                            'metric': metric_name,
                            'file': file_path,
                            'data_type': type(data).__name__,
                            'keys': list(data.keys()) if isinstance(data, dict) else None
                        })
                        continue

                    # 5. 到这里说明是有效的评分项
                    completed_metrics.add(metric_name)

                except Exception as e:
                    reasons['other_error'].append({
                        'metric': metric_name,
                        'file': file_path,
                        'error': str(e)
                    })

        except Exception as e:
            reasons['other_error'].append({
                'dir': report_dir,
                'error': str(e)
            })

    return completed_metrics

def evaluate_single_metric(metric_data, project_dir, session_id, retry_round, make_query, report_dir):
    """对单个测试项进行评分"""
    metric_name = metric_data.get('metric', 'Unknown Metric')
    description = metric_data.get('description', '')
    
    metric_report_file = os.path.join(report_dir, f"{metric_name}.json")
    
    abs_metric_data = transfer_metric_abs_path(metric_data, project_dir)
    
    prompt_data = f"""[Round {retry_round}] ### Task
Please evaluate the implementation of {project_dir} based on the evaluation metric: {metric_name}. The project code is located in the src/ directory and the evaluation auxiliary files are located in the evaluation/ directory.
The code should be completed strictly in accordance with the evaluation criteria to be considered qualified. If the code fails to run or adapt to the interface, please directly give the current test point a score of 0.

### Evaluation Metric Details
{json.dumps(abs_metric_data, ensure_ascii=False, indent=2)}

- 'metric': the metric name
- 'description'(Important): Arrange-Act-Assert description of the test metric
- 'type': the type of the test metric, can be 'unit_test', 'shell_interaction' and 'file_comparison'
- 'testcases': reference execution commands and input files
- 'expected_output' / 'expected_output_files': expected output after executing the testcases
- 'input_files': input files for the testcases

### Path Instructions
The project code is located in the {project_dir}/src/ directory. DO NOT MODIFY THE PROJECT CODE.
DO NOT MODIFY THE EVALUATION CRITERIA. DO NOT MODIFY ANY FILES UNDER THE {project_dir}/evaluation DIRECTORY.
The evaluation report must be saved to {metric_report_file} in JSON format.
If you encounter a "No such file or directory" error, please check whether you are in the correct problem path and whether the path has omitted the problem number.

### Tips
If the code is unable to run, please give the score of 0 and report it in the report.
If the detailed_test_plan mentions that image analysis is required, use the "deal_graph" tool to analyze the images.
Use the write_file tool to write the report content into a file, passing it to the content variable as a string type when writing.
If the metric has more than one testcase, you should use "start_interative_shell" tool to start a new shell session for each testcase. And if you need to input content to the shell, use the "run_interactive_shell" tool.

### *Important* File Output Requirement
After completing your evaluation, you MUST write the evaluation result to a JSON file at the following path:
{metric_report_file}

The JSON file should contain the evaluation result in the following format:
{{"metric": "{metric_name}",
"description": "{description}",
"score": <0-2>,
"explanation": "Detailed explanation of the evaluation result"
}}

The score should be 0, 1, or 2.
0 means the test metric is completely not passed.
1 means the test metric is partially passed. For shell_interaction and file_comparison types, this indicates that all steps except the final verification step are correct; for unit_test type, this means that pytest runs without any module import errors.
2 means the test metric is completely passed.

#### Detailed Example
{{
"metric": "1.3 Menu Navigation - Export Results Submenu",
"description": "1. **Arrange:** Read the main menu and understand the options. \\n2. **Act:** Start the program and select main menu '3' to enter the export results submenu.\\n3. **Assert:** Check whether the submenu displays 'Export Huffman codes to CSV', 'Export Huffman tree to JSON', and 'Return to main menu'.",
"score": 0,
"explanation": "When attempting to export results without having generated Huffman codes, the program does not enter the export submenu but instead prompts 'No available Huffman codes, please generate them first.' and returns to the main menu, which does not meet the expected behavior."
}}

### Final Reminder
The interface of the code must be completed strictly in accordance with the evaluation criteria to be considered qualified. 
If the code fails to run or fails to adapt to the interface, please directly give the current test point a score of 0. There is no need to examine the code correctness, just use evaluation metric to give the score.
DO NOT modify the project code. DO NOT MODIFY the evaluation criteria. 
""".strip()

    print(f"Evaluating metric: {metric_name}")
    query_response = make_query(prompt_data, session_id)
    
    # 保存query_response到log文件
    log_file = os.path.join(report_dir, f"{metric_name}.log")
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(query_response, f, ensure_ascii=False, indent=2)
        print(f"Query response saved to log file: {log_file}")
    except Exception as e:
        print(f"Warning: Failed to save log file for metric {metric_name}: {e}")
    
    return query_response

def run_evaluation(test_dir, args, code_path, construct_session, make_query, retry_round=0):
    print(f"\n=== Starting evaluation of project {test_dir} ===")
    dir_path = os.path.join(code_path, test_dir)
    project_dir = dir_path

    # Check if project directory exists
    if not os.path.exists(project_dir):
        print(f"Warning: Project directory {project_dir} does not exist, skipping...")
        return False

    report_file = os.path.join(dir_path, "reports", f"round{args.round}.jsonl")

    # if os.path.exists(report_file):
    #     print(f"Warning: Report file {report_file} already exists, skipping...")
    #     return False

    report_dir = os.path.join(dir_path, "reports")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # Load test plan
    test_plan_path = os.path.join(project_dir, "evaluation", "detailed_test_plan.json")
    if not os.path.exists(test_plan_path):
        print(f"Warning: Test plan not found at {test_plan_path}, skipping...")
        return False
    
    test_plan = load_test_plan(test_plan_path)
    if not test_plan:
        print(f"Warning: Failed to load test plan from {test_plan_path}, skipping...")
        return False

    # Get completed metrics
    completed_metrics = get_completed_metrics(report_dir)
    print(f"Already completed metrics: {len(completed_metrics)}")
   
    # Evaluate each metric
    for metric_data in test_plan:
        metric_name = metric_data.get('metric', 'Unknown Metric')
         # Add retry round to session_id to ensure uniqueness
        if retry_round == 0:
            session_id = f"{test_dir}_{metric_name}"
        else:
            session_id = f"{test_dir}_{metric_name}_{retry_round}"

        print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        print(f"Starting to create session, session_id: {session_id} ...")
        
        
        # Skip if already completed
        if metric_name in completed_metrics:
            print(f"Skipping already completed metric: {metric_name}")
            continue
        
        session_response = construct_session(session_id)    
        # 调用evaluate_single_metric，agent会自己写入JSON文件
        result = evaluate_single_metric(metric_data, project_dir, session_id, retry_round, make_query, report_dir)
        
        # 检查agent是否成功生成了JSON文件并验证内容
        metric_report_file = os.path.join(report_dir, f"{metric_name}.json")
        if os.path.exists(metric_report_file):
            # 验证JSON文件内容
            try:
                with open(metric_report_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # 检查是否包含必需的字段
                required_fields = ['metric', 'description', 'score', 'explanation']
                if all(field in json_data for field in required_fields):
                    # 检查score是否为有效数字
                    if isinstance(json_data['score'], (int, float)) and 0 <= json_data['score'] <= 2:
                        print(f"Successfully evaluated metric {metric_name} - valid JSON file generated")
                    else:
                        print(f"Warning: Metric {metric_name} JSON file exists but score is invalid: {json_data.get('score')}")
                else:
                    missing_fields = [field for field in required_fields if field not in json_data]
                    print(f"Warning: Metric {metric_name} JSON file exists but missing required fields: {missing_fields}")
            except json.JSONDecodeError as e:
                print(f"Warning: Metric {metric_name} JSON file exists but is not valid JSON: {e}")
            except Exception as e:
                print(f"Warning: Error reading metric {metric_name} JSON file: {e}")
        else:
            print(f"Warning: Metric {metric_name} evaluation completed but no JSON file was generated")

    print(f"dir_path: {dir_path}")
    print(f"=== Project {test_dir} evaluation completed ===\n")
    return True

def get_test_directories(root_path):
    """获取root_path下所有子文件夹作为测试目录"""
    test_dirs = []
    if not os.path.exists(root_path):
        print(f"Warning: Root path {root_path} does not exist")
        return test_dirs
    
    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        if os.path.isdir(item_path):
            test_dirs.append(item)
    
    test_dirs.sort()  # 按名称排序，确保处理顺序一致
    print(f"Found {len(test_dirs)} test directories: {test_dirs}")
    return test_dirs

def check_all_reports_generated(code_path, test_dirs, args):
    """Check if all projects have generated metric json files"""
    for test_dir in test_dirs:
        dir_path = os.path.join(code_path, test_dir)
        report_dir = os.path.join(dir_path, "reports")
        
        # 检查reports目录是否存在
        if not os.path.exists(report_dir):
            return False
            
        # 检查是否有任何.json文件
        json_files = [f for f in os.listdir(report_dir) if f.endswith('.json')]
        if not json_files:
            return False
    return True

def evaluate_single_repo_wrapper(test_dir, args_dict, code_path):
    """
    评估单个repo的所有metrics（含重试逻辑）
    这个函数会在独立进程中运行，需要重新创建必要的函数
    
    Args:
        test_dir: 测试目录名
        args_dict: 参数字典（因为跨进程传递）
        code_path: 代码根路径
    
    Returns:
        dict: 包含评估结果的字典
    """
    local_port = args_dict['local_port']
    model_name = args_dict['model_name']
    retry_count = args_dict['retry_count']
    round_num = args_dict['round']
    
    worker_name = multiprocessing.current_process().name
    
    # 在子进程中重新定义 construct_session 函数
    def construct_session_local(session_id):
        session_query = {
            "url": f"http://localhost:{local_port}/apps/code_eval_agent_workspace_dir/users/{model_name}/sessions/s_{session_id}",
            "method": "POST",
            "headers": {"Content-Type": "application/json"}
        }
        delete_query = {
            "url": f"http://localhost:{local_port}/apps/code_eval_agent_workspace_dir/users/{model_name}/sessions/s_{session_id}",
            "method": "DELETE",
            "headers": {"Content-Type": "application/json"}
        }
        
        try:
            delete_response = requests.delete(delete_query["url"], headers=delete_query["headers"])
            print(f"[{worker_name}][{test_dir}] Delete session response status code: {delete_response.status_code}")
            
            response = requests.post(session_query["url"], headers=session_query["headers"])
            print(f"[{worker_name}][{test_dir}] Create session response status code: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[{worker_name}][{test_dir}] Create session failed, status code: {response.status_code}")
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"[{worker_name}][{test_dir}] Network request error: {e}")
            return {"error": "network_error", "message": str(e)}
        except json.JSONDecodeError as e:
            print(f"[{worker_name}][{test_dir}] JSON parsing error: {e}")
            return {"error": "json_decode_error", "text": response.text if 'response' in locals() else ""}
    
    # 在子进程中重新定义 make_query 函数
    def make_query_local(prompt_data, session_id):
        query_query = {
            "url": f"http://localhost:{local_port}/run",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": {
                "appName": "code_eval_agent_workspace_dir",
                "userId": model_name,
                "sessionId": f"s_{session_id}",
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": prompt_data}]
                }
            }
        }
        
        try:
            response = requests.post(query_query["url"], headers=query_query["headers"], json=query_query["data"])
            print(f"[{worker_name}][{test_dir}] Query response status code: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[{worker_name}][{test_dir}] Query failed, status code: {response.status_code}")
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"[{worker_name}][{test_dir}] Network request error: {e}")
            return {"error": "network_error", "message": str(e)}
        except json.JSONDecodeError as e:
            print(f"[{worker_name}][{test_dir}] JSON parsing error: {e}")
            return {"error": "json_decode_error", "text": str(response) if 'response' in locals() else ""}
    
    # 重建 args 对象
    class Args:
        pass
    args = Args()
    args.round = round_num
    args.retry_count = retry_count
    
    print(f"\n[{worker_name}] === 开始评估项目 {test_dir} ===")
    start_time = time.time()
    
    try:
        # 先做一轮初始评估
        run_evaluation(test_dir, args, code_path, construct_session_local, make_query_local, retry_round=0)

        # 最多补漏重试指定次数
        for retry in range(1, retry_count + 1):
            dir_path = os.path.join(code_path, test_dir)
            report_dir = os.path.join(dir_path, "reports")
            test_plan_path = os.path.join(dir_path, "evaluation", "detailed_test_plan.json")
            
            if not os.path.exists(test_plan_path):
                print(f"[{worker_name}][{test_dir}] 补漏检查: Test plan不存在，跳过该项目")
                break
            
            test_plan = load_test_plan(test_plan_path)
            if not test_plan:
                print(f"[{worker_name}][{test_dir}] 补漏检查: 加载test plan失败，跳过该项目")
                break
            
            if not os.path.exists(report_dir):
                print(f"[{worker_name}][{test_dir}] 补漏检查: reports目录不存在，准备重试...({retry}/{retry_count})")
                need_retry = True
            else:
                completed_metrics = get_completed_metrics(report_dir)
                all_metrics = {metric['metric'] for metric in test_plan if 'metric' in metric}
                need_retry = not all_metrics.issubset(completed_metrics)
                if need_retry:
                    lack_metrics = all_metrics - completed_metrics
                    print(f"[{worker_name}][{test_dir}] 补漏检查: 缺少{len(lack_metrics)}个metrics，重试中...({retry}/{retry_count})")
                    if len(lack_metrics) <= 5:  # 只在数量少时打印详情
                        print(f"[{worker_name}][{test_dir}] 缺少的metrics: {lack_metrics}")
            
            if not need_retry:
                print(f"[{worker_name}][{test_dir}] ✓ 所有metric打分结果已生成，补漏完成！")
                break
            
            # 下一轮重试
            run_evaluation(test_dir, args, code_path, construct_session_local, make_query_local, retry_round=retry)
            
            if retry == retry_count:
                print(f"[{worker_name}][{test_dir}] ✗ 达到最大重试次数({retry_count})，部分metric结果可能缺失")
        
        elapsed_time = time.time() - start_time
        print(f"[{worker_name}] === 项目 {test_dir} 评估完成，耗时: {elapsed_time:.2f}秒 ===\n")
        
        return {
            "test_dir": test_dir,
            "success": True,
            "elapsed_time": elapsed_time
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"[{worker_name}][{test_dir}] ✗ 评估过程发生异常: {e}")
        import traceback
        traceback.print_exc()
        return {
            "test_dir": test_dir,
            "success": False,
            "error": str(e),
            "elapsed_time": elapsed_time
        }

def main(args, code_path, construct_session, make_query):
    """串行版本的main函数（保留用于兼容）"""
    # Get all test directories dynamically
    test_dirs = get_test_directories(code_path)
    if not test_dirs:
        print("No test directories found, exiting...")
        return
    
    print(f"Found {len(test_dirs)} test directories to evaluate")

    for test_dir in test_dirs:
        print(f"\n=== 开始评估项目 {test_dir} ===")
        # 先做一轮初始评估
        run_evaluation(test_dir, args, code_path, construct_session, make_query, retry_round=0)

        # 最多补漏重试指定次数
        for retry in range(1, args.retry_count + 1):
            dir_path = os.path.join(code_path, test_dir)
            report_dir = os.path.join(dir_path, "reports")
            # 依赖 get_completed_metrics 和 test_plan
            test_plan_path = os.path.join(dir_path, "evaluation", "detailed_test_plan.json")
            if not os.path.exists(test_plan_path):
                print(f"补漏检查: Test plan {test_plan_path} 不存在，跳过该项目！")
                break
            test_plan = load_test_plan(test_plan_path)
            if not test_plan:
                print(f"补漏检查: 加载 test plan 失败，跳过该项目！")
                break
            if not os.path.exists(report_dir):
                print(f"补漏检查: 项目 {test_dir} reports 目录不存在，准备重试...({retry})")
                need_retry = True
            else:
                completed_metrics = get_completed_metrics(report_dir)
                all_metrics = {metric['metric'] for metric in test_plan if 'metric' in metric}
                need_retry = not all_metrics.issubset(completed_metrics)
                if need_retry:
                    lack_metrics = all_metrics - completed_metrics
                    print(f"补漏检查: 项目 {test_dir} 缺少 metric 报告: {lack_metrics}, 准备重试...({retry})")
            if not need_retry:
                print(f"项目 {test_dir} 所有 metric 打分结果已生成，补漏完成！")
                break
            # 下一轮重试
            run_evaluation(test_dir, args, code_path, construct_session, make_query, retry_round=retry)
            if retry == args.retry_count:
                print(f"项目 {test_dir} 达到最大重试次数({args.retry_count})，部分 metric 结果可能缺失！")
    print("所有项目评测并补漏流程已完成！")

def main_parallel(args, code_path):
    """并行版本的main函数（推荐使用）"""
    # 获取所有测试目录
    test_dirs = get_test_directories(code_path)
    if not test_dirs:
        print("No test directories found, exiting...")
        return
    
    print(f"Found {len(test_dirs)} test directories to evaluate")
    
    # 设置并发数
    max_workers = min(args.max_workers, len(test_dirs))
    print(f"使用 {max_workers} 个并行workers进行评估")
    print(f"预计总任务数: {len(test_dirs)} 个repos")
    print("=" * 80)
    
    # 准备参数字典（用于跨进程传递）
    args_dict = {
        'local_port': local_port,
        'model_name': model_name,
        'retry_count': args.retry_count,
        'round': args.round
    }
    
    # 记录开始时间
    overall_start_time = time.time()
    results = []
    
    # 使用进程池并行执行
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_repo = {
            executor.submit(evaluate_single_repo_wrapper, test_dir, args_dict, code_path): test_dir 
            for test_dir in test_dirs
        }
        
        # 处理完成的任务
        completed_count = 0
        for future in as_completed(future_to_repo):
            test_dir = future_to_repo[future]
            completed_count += 1
            
            try:
                result = future.result()
                results.append(result)
                
                if result['success']:
                    print(f"[主进程] ✓ [{completed_count}/{len(test_dirs)}] Repository {test_dir} 评估成功 (耗时: {result['elapsed_time']:.2f}秒)")
                else:
                    print(f"[主进程] ✗ [{completed_count}/{len(test_dirs)}] Repository {test_dir} 评估失败: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"[主进程] ✗ [{completed_count}/{len(test_dirs)}] Repository {test_dir} 抛出异常: {e}")
                results.append({
                    "test_dir": test_dir,
                    "success": False,
                    "error": str(e)
                })
    
    # 统计结果
    overall_elapsed_time = time.time() - overall_start_time
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    print("=" * 80)
    print("所有项目评测并补漏流程已完成！")
    print(f"总耗时: {overall_elapsed_time:.2f}秒 ({overall_elapsed_time/60:.2f}分钟)")
    print(f"成功: {success_count}/{len(test_dirs)}")
    print(f"失败: {failed_count}/{len(test_dirs)}")
    
    if failed_count > 0:
        print("\n失败的项目:")
        for r in results:
            if not r['success']:
                print(f"  - {r['test_dir']}: {r.get('error', 'Unknown error')}")
    
    print("=" * 80)

if __name__ == '__main__':
    # 使用并行版本
    main_parallel(args, code_path)
