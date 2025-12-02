#!/bin/bash

# 本地测试启动脚本
# 自动设置工作目录为当前目录，便于测试

echo "🔧 设置本地测试环境..."

# 设置工作目录为当前目录
export CODE_AGENT_WORKSPACE_DIR=$(pwd)

echo "📁 工作目录已设置为: $CODE_AGENT_WORKSPACE_DIR"

# 激活环境并运行测试
echo "🚀 启动测试..."

if [ "$1" = "judge" ]; then
    echo "运行Judge工具测试..."
    conda activate /mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/EVA/kuangjun/.conda/.envs/googleADK && python test_judge.py
elif [ "$1" = "interactive" ]; then
    echo "运行交互式shell测试..."
    conda activate /mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/EVA/kuangjun/.conda/.envs/googleADK && python test_interactive_shell.py
else
    echo "运行完整测试套件..."
    conda activate /mnt/dolphinfs/hdd_pool/docker/user/hadoop-aipnlp/EVA/kuangjun/.conda/.envs/googleADK && python test_agent.py
fi

echo "✅ 测试完成" 