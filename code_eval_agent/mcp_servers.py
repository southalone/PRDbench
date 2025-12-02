#!/usr/bin/env python3
"""
本地 MCP 服务器实现
提供 Python 解释器、文件操作和系统操作服务
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import aiohttp
from aiohttp import web
import pexpect

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from mcp_config import (
    PYTHON_INTERPRETER_MCP_URL, 
    FILE_OPERATIONS_PORT,
    PYTHON_INTERPRETER_PORT,
    SYSTEM_OPERATIONS_PORT,
    FILE_OPERATIONS_MCP_URL, 
    SYSTEM_OPERATIONS_MCP_URL,
    WORKSPACE_DIR,
)

class PythonInterpreterMCP:
    """Python 解释器 MCP 服务器"""
    TIMEOUT = 10
    
    def __init__(self, port: int = None):
        self.port = port or int(PYTHON_INTERPRETER_PORT)
        print(self.port)
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        self.app.router.add_post('/python-interpreter/execute', self.execute_code)
        self.app.router.add_get('/python-interpreter/health', self.health_check)
        self.app.router.add_get('/python-interpreter/interactive', self.interactive_execute_code)
    
    async def execute_code(self, request):
        """执行 Python 代码"""
        try:
            data = await request.json()
            code = data.get('code', '')
            timeout = data.get('timeout', self.TIMEOUT)
            
            logger.info(f"执行 Python 代码: {code[:100]}...")
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # 执行代码
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd='/tmp'
                )
                
                response_data = {
                    'status': 'success',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode,
                    'execution_time': datetime.now().isoformat()
                }
                
            finally:
                # 清理临时文件
                os.unlink(temp_file)
            
            return web.json_response(response_data)
            
        except subprocess.TimeoutExpired:
            return web.json_response({
                'status': 'error',
                'error': '代码执行超时'
            }, status=408)
        except Exception as e:
            logger.error(f"代码执行错误: {e}")
            return web.json_response({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    async def health_check(self, request):
        """健康检查"""
        return web.json_response({
            'status': 'healthy',
            'service': 'python-interpreter',
            'timestamp': datetime.now().isoformat()
        })
    
    async def interactive_execute_code(self, request):
        """交互式执行 Python 代码（WebSocket）"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # 启动交互式Python进程
        child = pexpect.spawn(sys.executable, ['-i'], encoding='utf-8', timeout=None)

        async def read_from_python():
            """后台任务：不断读取Python输出并推送到前端"""
            try:
                while True:
                    output = child.read_nonblocking(size=1024, timeout=1)
                    if output:
                        await ws.send_str(output)
            except pexpect.exceptions.TIMEOUT:
                pass
            except pexpect.exceptions.EOF:
                await ws.send_str('[Python进程已结束]')
                await ws.close()

        reader_task = asyncio.create_task(read_from_python())

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    # 用户输入，写入Python进程
                    child.sendline(msg.data)
                elif msg.type == web.WSMsgType.ERROR:
                    break
        finally:
            reader_task.cancel()
            child.terminate(force=True)
            await ws.close()
        return ws
    
    async def start(self):
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        logger.info(f"Python 解释器 MCP 服务器启动在端口 {self.port}")
        return runner

class FileOperationsMCP:
    """文件操作 MCP 服务器"""
    
    def __init__(self, port: int = None, workspace_dir: str = None):
        self.port = port or int(FILE_OPERATIONS_PORT)
        self.workspace_dir = Path(workspace_dir or WORKSPACE_DIR)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        self.app.router.add_post('/file-operations/read', self.read_file)
        self.app.router.add_post('/file-operations/write', self.write_file)
        self.app.router.add_post('/file-operations/list', self.list_files)
        self.app.router.add_get('/file-operations/health', self.health_check)
    
    def validate_path(self, file_path: str) -> bool:
        """验证文件路径是否安全"""
        try:
            file_path = Path(file_path).resolve()
            workspace_path = self.workspace_dir.resolve()
            return str(file_path).startswith(str(workspace_path))
        except:
            return False
    
    async def read_file(self, request):
        """读取文件"""
        try:
            data = await request.json()
            file_path = data.get('path', '')
            
            if not self.validate_path(file_path):
                return web.json_response({
                    'status': 'error',
                    'error': '文件路径不安全'
                }, status=403)
            
            file_path = Path(file_path)
            if not file_path.exists():
                return web.json_response({
                    'status': 'error',
                    'error': '文件不存在'
                }, status=404)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return web.json_response({
                'status': 'success',
                'content': content,
                'size': len(content),
                'path': str(file_path)
            })
            
        except Exception as e:
            logger.error(f"读取文件错误: {e}")
            return web.json_response({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    async def write_file(self, request):
        """写入文件"""
        try:
            data = await request.json()
            file_path = data.get('path', '')
            content = data.get('content', '')
            
            if not self.validate_path(file_path):
                return web.json_response({
                    'status': 'error',
                    'error': '文件路径不安全'
                }, status=403)
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return web.json_response({
                'status': 'success',
                'path': str(file_path),
                'size': len(content)
            })
            
        except Exception as e:
            logger.error(f"写入文件错误: {e}")
            return web.json_response({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    async def list_files(self, request):
        """列出文件"""
        try:
            data = await request.json()
            directory = data.get('directory', str(self.workspace_dir))
            
            if not self.validate_path(directory):
                return web.json_response({
                    'status': 'error',
                    'error': '目录路径不安全'
                }, status=403)
            
            directory = Path(directory)
            if not directory.exists():
                return web.json_response({
                    'status': 'error',
                    'error': '目录不存在'
                }, status=404)
            
            files = []
            for item in directory.iterdir():
                file_info = {
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else None
                }
                files.append(file_info)
            
            return web.json_response({
                'status': 'success',
                'files': files,
                'directory': str(directory)
            })
            
        except Exception as e:
            logger.error(f"列出文件错误: {e}")
            return web.json_response({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    async def health_check(self, request):
        """健康检查"""
        return web.json_response({
            'status': 'healthy',
            'service': 'file-operations',
            'workspace': str(self.workspace_dir),
            'timestamp': datetime.now().isoformat()
        })
    
    async def start(self):
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        logger.info(f"文件操作 MCP 服务器启动在端口 {self.port}")
        return runner

async def start_all_servers():
    """启动所有 MCP 服务器"""
    servers = [
        PythonInterpreterMCP(),
        FileOperationsMCP(),
    ]
    
    runners = []
    for server in servers:
        runner = await server.start()
        runners.append(runner)
    
    logger.info("所有 MCP 服务器已启动")
    
    try:
        # 保持服务器运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("正在关闭服务器...")
        for runner in runners:
            await runner.cleanup()
        logger.info("所有服务器已关闭")

if __name__ == "__main__":
    asyncio.run(start_all_servers()) 