curl -v -X POST \
https://api.toiotech.com/v1/ \
-H 'Authorization: Be****qP' \
-d '{
  "model": "qwen3-coder-480b-a35b-instruct",
  "messages": [
    {
      "role": "user",
      "content": "\n    把{\n  \"metric\": \"0.1 Program Launch and Main Menu Display\",\n  \"description\": \"1. **Execute (Act):** Run `python src/main.py` on the command line.\n2. **Assert:** Check if the program successfully launches and displays a full interface with the title \\\"Intelligent Business Travel Planning System\\\" and at least 6 main menu options (Create New Journey, Load Saved Journey, Use Travel Template, View Current Journey, System Settings, Exit System).\",\n  \"score\": 0,\n  \"explanation\": \"The program failed to launch due to a file path error. The error message indicates that the system cannot find the main.py file in the expected location. This prevents the program from displaying the main menu, resulting in a score of 0.\"\n}写进/mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/EVA/zhangbolun06/PRD_bench/workspace/codex_2_Dev_inference_eval/9/reports/0.1 Program Launch and Main Menu Display.json\n"
    }
  ],
  "temperature": 0.1,
  "presence_penalty": 1.2,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "exit_loop",
        "description": "当任务完成时退出循环",
        "parameters": {
          "type": "object",
          "properties": {}
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_workspace",
        "description": "List the files and directories in the workspace.",
        "parameters": {
          "type": "object",
          "properties": {
            "workspace_name": {
              "nullable": true,
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "read_file",
        "description": "Read the content of the file.",
        "parameters": {
          "type": "object",
          "properties": {
            "file_path": {
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "write_file",
        "description": "Write the content to the file.",
        "parameters": {
          "type": "object",
          "properties": {
            "file_path": {
              "type": "string"
            },
            "content": {
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "delete_file",
        "description": "Delete the file.",
        "parameters": {
          "type": "object",
          "properties": {
            "file_path": {
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "run_system_command",
        "description": "Run the system command.",
        "parameters": {
          "type": "object",
          "properties": {
            "command": {
              "type": "string"
            },
            "timeout": {
              "type": "integer"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "start_interative_shell",
        "description": "Start a interactive shell session.",
        "parameters": {
          "type": "object",
          "properties": {
            "cmd": {
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "run_interactive_shell",
        "description": "Run a interactive shell session.",
        "parameters": {
          "type": "object",
          "properties": {
            "session_id": {
              "nullable": true,
              "type": "string"
            },
            "user_input": {
              "nullable": true,
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "kill_shell_session",
        "description": "Terminate a shell session.",
        "parameters": {
          "type": "object",
          "properties": {
            "session_id": {
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "judge",
        "description": "Run the program and simulate the user interaction, record the interaction process and output result.",
        "parameters": {
          "type": "object",
          "properties": {
            "context": {
              "type": "string"
            },
            "entry_command": {
              "type": "string"
            },
            "input_file": {
              "nullable": true,
              "type": "string"
            }
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "deal_graph",
        "description": "Interact with the multi-modal LLM and get the reply.",
        "parameters": {
          "type": "object",
          "properties": {
            "graph_path_list": {
              "type": "array"
            },
            "prompt": {
              "type": "string"
            }
          }
        }
      }
    }
  ],
  "extra_body": {
    "max_tokens_threshold": 224000,
    "enable_compression": true
  },
  "extra_headers": {
    "uid": "Yi4TygCohR3TpCx7/PRhCQ=="
  }
}
'