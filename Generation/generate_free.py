import requests
import requests
import json
import argparse
import os

def construct_session(local_port, model_name, session_id):
    delete_url = f"http://localhost:{local_port}/apps/code_agent_local/users/{model_name}/sessions/s_{session_id}"
    try:
        delete_response = requests.delete(delete_url, headers={"Content-Type": "application/json"})
        print(f"删除会话响应状态码: {delete_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"删除会话时网络请求错误: {e}")

    create_url = f"http://localhost:{local_port}/apps/code_agent_local/users/{model_name}/sessions/s_{session_id}"
    try:
        response = requests.post(create_url, headers={"Content-Type": "application/json"})
        print(f"创建会话响应状态码: {response.status_code}")
        print(f"创建会话响应内容: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return {"error": "network_error", "message": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应内容: {response.text}")
        return {"error": "json_decode_error", "text": response.text}

def make_query(local_port, model_name, session_id, prompt_data):
    url = f"http://localhost:{local_port}/run"
    data = {
        "appName": "code_agent_local",
        "userId": model_name,
        "sessionId": f"s_{session_id}",
        "newMessage": {
            "role": "user",
            "parts": [{
                "text": prompt_data
            }]
        }
    }
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=data)
        print(f"查询响应状态码: {response.status_code}")
        print(f"查询响应内容: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return {"error": "network_error", "message": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应内容: {str(response)}")
        return {"error": "json_decode_error", "text": str(response)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Interact with code agent via HTTP API.")
    parser.add_argument("--local_port", type=str, default="9090", help="Local server port")
    parser.add_argument("--model_name", type=str, default="gpt_5", help="Model name")
    parser.add_argument("--session_id", type=str, default="9", help="Session ID")
    parser.add_argument("--ID", type=str, default="9", help="Project ID")
    parser.add_argument("--project_path", type=str, default="workspace/ADK_gpt_5_Dev_inference/9", help="Project path")
    parser.add_argument("--prompt", type=str, default=None, help="Prompt data to send")
    parser.add_argument("--prompt_file", type=str, default=None, help="Path to file containing prompt text")
    args = parser.parse_args()

    # 默认prompt模板，带{ID}和{project_path}变量
    default_prompt_template = '''
Please develop a complete Python project (ID:{ID}) located at {project_path} according to the requirements specified in the project documentation (src/PRD.md).

### Requirements
1. Strictly implement all functional requirements described in PRD.md, ensuring that every feature is fully realized and that no requirements are omitted.
2. Independently design the implementation details, including process flows and interfaces, based on the requirements in PRD.md, so that each function can be clearly and completely used via the CLI.
3. Submit all project code and related files completely under the src/ directory, ensuring that the project structure is clear and maintainable.
4. Do not ask any intermediate questions during the development process. Complete the entire project and submit directly.
'''

    # 优先使用 --prompt，其次使用 --prompt_file，否则用模板自动填充ID和路径
    if args.prompt is not None:
        prompt_data = args.prompt
    elif args.prompt_file is not None:
        with open(args.prompt_file, 'r', encoding='utf-8') as f:
            prompt_data = f.read()
    else:
        prompt_data = default_prompt_template.format(ID=args.ID, project_path=args.project_path)

    session_response = construct_session(args.local_port, args.model_name, args.session_id)
    query_response = make_query(args.local_port, args.model_name, args.session_id, prompt_data)
    print("Session response:", session_response)
    print("Query response:", query_response)
    output_path = os.path.join(args.project_path, "query_response.json")
    output_path2 = os.path.join(args.project_path, "session_response.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(query_response, f, ensure_ascii=False, indent=2)
        print(f"Query response has been saved to {output_path}")
        with open(output_path2, "w", encoding="utf-8") as f:
            json.dump(session_response, f, ensure_ascii=False, indent=2)
        print(f"Query response has been saved to {output_path2}")
    except Exception as e:
        print(f"Failed to save query_response: {e}")
