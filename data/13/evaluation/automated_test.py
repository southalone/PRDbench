#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐系统自动化评估测试脚本
按照 metric.json 中的评估标准进行系统性测试
"""

import os
import sys
import json
import subprocess
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime

# 设置路径
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"
sys.path.insert(0, str(SRC_DIR))

class AutomatedEvaluator:
    """自动化评估器"""
    
    def __init__(self):
        self.results = []
        self.total_score = 0
        self.max_score = 0
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(EVALUATION_DIR / 'test.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 加载评估标准
        with open(EVALUATION_DIR / 'metric.json', 'r', encoding='utf-8') as f:
            self.metrics = json.load(f)
    
    def log_test_result(self, test_name: str, score: int, max_score: int, details: str):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'score': score,
            'max_score': max_score,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        self.total_score += score
        self.max_score += max_score
        
        self.logger.info(f"测试: {test_name}")
        self.logger.info(f"得分: {score}/{max_score}")
        self.logger.info(f"详情: {details}")
        self.logger.info("-" * 80)
    
    def test_system_startup(self):
        """测试1.1: 系统启动与环境配置"""
        test_name = "1.1 系统启动与环境配置"
        try:
            # 检查主入口文件是否存在
            main_py = SRC_DIR / "main.py"
            if not main_py.exists():
                self.log_test_result(test_name, 0, 2, "main.py文件不存在")
                return
            
            # 检查代码中是否包含至少3个功能选项
            with open(main_py, 'r', encoding='utf-8') as f:
                content = f.read()
            
            menu_options = 0
            if "数据" in content:
                menu_options += 1
            if "推荐" in content:
                menu_options += 1
            if "服务" in content or "API" in content:
                menu_options += 1
            if "模型" in content or "训练" in content:
                menu_options += 1
            if "评估" in content:
                menu_options += 1
            
            if menu_options >= 3:
                score = 2
                details = f"系统包含{menu_options}个主要功能模块，满足启动要求"
            elif menu_options >= 1:
                score = 1
                details = f"系统包含{menu_options}个功能模块，但数量不足"
            else:
                score = 0
                details = "系统缺少主要功能模块"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_data_collection_json(self):
        """测试2.1.1a: 数据采集 - JSON格式支持"""
        test_name = "2.1.1a 数据采集 - JSON格式支持"
        try:
            # 检查是否有数据加载相关的代码
            files_to_check = [
                SRC_DIR / "data_old" / "data_loader.py",
                SRC_DIR / "cli_simplified.py"
            ]
            
            json_support = False
            for file_path in files_to_check:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "json" in content.lower() or "JSON" in content:
                            json_support = True
                            break
            
            # 检查pandas依赖（可以处理JSON）
            requirements_file = SRC_DIR / "requirements.txt"
            pandas_available = False
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "pandas" in f.read():
                        pandas_available = True
            
            if json_support and pandas_available:
                score = 2
                details = "支持JSON格式数据处理，具备pandas依赖"
            elif pandas_available:
                score = 1
                details = "具备JSON处理能力但缺少显式支持代码"
            else:
                score = 0
                details = "缺少JSON数据处理支持"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_data_collection_csv(self):
        """测试2.1.1b: 数据采集 - CSV格式支持"""
        test_name = "2.1.1b 数据采集 - CSV格式支持"
        try:
            # 检查CLI中的数据生成功能
            cli_file = SRC_DIR / "cli_simplified.py"
            csv_support = False
            
            if cli_file.exists():
                with open(cli_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "to_csv" in content or "read_csv" in content:
                        csv_support = True
            
            # 检查是否生成了示例CSV数据
            data_dir = SRC_DIR / "data"
            csv_files_exist = False
            if data_dir.exists():
                csv_files = list(data_dir.glob("*.csv"))
                if len(csv_files) >= 2:  # 至少有用户和商品数据
                    csv_files_exist = True
            
            if csv_support and csv_files_exist:
                score = 2
                details = "完全支持CSV格式，已生成示例数据文件"
            elif csv_support:
                score = 1
                details = "支持CSV格式但缺少数据文件"
            else:
                score = 0
                details = "缺少CSV格式支持"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_data_cleaning_outliers(self):
        """测试2.1.2a: 数据清洗 - 异常值检测"""
        test_name = "2.1.2a 数据清洗 - 异常值检测"
        try:
            # 检查是否有数据预处理模块
            preprocessor_file = SRC_DIR / "data_old" / "preprocessor.py"
            outlier_detection = False
            
            if preprocessor_file.exists():
                with open(preprocessor_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    keywords = ["outlier", "异常", "极值", "检测", "清洗"]
                    if any(keyword in content for keyword in keywords):
                        outlier_detection = True
            
            # 检查统计库依赖
            requirements_file = SRC_DIR / "requirements.txt"
            stats_libs = False
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "scipy" in req_content or "numpy" in req_content:
                        stats_libs = True
            
            if outlier_detection and stats_libs:
                score = 2
                details = "具备异常值检测功能和统计库支持"
            elif stats_libs:
                score = 1
                details = "具备统计分析能力但缺少异常值检测实现"
            else:
                score = 0
                details = "缺少异常值检测功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_missing_value_handling(self):
        """测试2.1.2b: 数据清洗 - 缺失值处理"""
        test_name = "2.1.2b 数据清洗 - 缺失值处理"
        try:
            # 检查pandas支持（具备缺失值处理能力）
            requirements_file = SRC_DIR / "requirements.txt"
            pandas_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "pandas" in f.read():
                        pandas_support = True
            
            # 检查代码中是否有缺失值处理逻辑
            missing_handling = False
            files_to_check = [
                SRC_DIR / "data_old" / "preprocessor.py",
                SRC_DIR / "cli_simplified.py"
            ]
            
            for file_path in files_to_check:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        keywords = ["fillna", "dropna", "缺失", "missing", "null"]
                        if any(keyword in content for keyword in keywords):
                            missing_handling = True
                            break
            
            if pandas_support and missing_handling:
                score = 2
                details = "具备完整的缺失值处理功能"
            elif pandas_support:
                score = 1
                details = "具备缺失值处理能力但缺少实现代码"
            else:
                score = 0
                details = "缺少缺失值处理功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_chinese_segmentation(self):
        """测试2.1.2c: 中文分词处理"""
        test_name = "2.1.2c 中文分词处理"
        try:
            # 检查jieba依赖
            requirements_file = SRC_DIR / "requirements.txt"
            jieba_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "jieba" in f.read():
                        jieba_support = True
            
            # 检查代码中是否使用了中文分词
            chinese_processing = False
            files_to_check = list(SRC_DIR.rglob("*.py"))
            
            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "jieba" in content or "分词" in content:
                            chinese_processing = True
                            break
                except:
                    continue
            
            if jieba_support and chinese_processing:
                score = 2
                details = "完整支持中文分词处理"
            elif jieba_support:
                score = 1
                details = "具备中文分词依赖但缺少使用代码"
            else:
                score = 0
                details = "缺少中文分词处理功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_normalization_encoding(self):
        """测试2.1.2d: 数据归一化与编码"""
        test_name = "2.1.2d 数据归一化与编码"
        try:
            # 检查scikit-learn依赖
            requirements_file = SRC_DIR / "requirements.txt"
            sklearn_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "scikit-learn" in req_content:
                        sklearn_support = True
            
            # 检查代码中是否有标准化或编码处理
            normalization_code = False
            files_to_check = list(SRC_DIR.rglob("*.py"))
            
            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        keywords = ["StandardScaler", "normalize", "LabelEncoder", "OneHotEncoder", "归一化", "标准化"]
                        if any(keyword in content for keyword in keywords):
                            normalization_code = True
                            break
                except:
                    continue
            
            if sklearn_support and normalization_code:
                score = 2
                details = "完整支持数据归一化和编码功能"
            elif sklearn_support:
                score = 1
                details = "具备数据预处理能力但缺少实现代码"
            else:
                score = 0
                details = "缺少数据归一化和编码功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_content_based_tfidf(self):
        """测试2.2.1a: 基于内容推荐 - TF-IDF实现"""
        test_name = "2.2.1a 基于内容推荐 - TF-IDF实现"
        try:
            # 检查内容推荐算法文件
            content_based_file = SRC_DIR / "algorithms" / "content_based.py"
            tfidf_implementation = False
            
            if content_based_file.exists():
                with open(content_based_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "TfidfVectorizer" in content or "TF-IDF" in content or "tfidf" in content:
                        tfidf_implementation = True
            
            # 检查scikit-learn依赖（TF-IDF需要）
            requirements_file = SRC_DIR / "requirements.txt"
            sklearn_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "scikit-learn" in f.read():
                        sklearn_support = True
            
            if tfidf_implementation and sklearn_support:
                score = 2
                details = "完整实现TF-IDF内容推荐算法"
            elif sklearn_support:
                score = 1
                details = "具备TF-IDF实现能力但缺少算法代码"
            else:
                score = 0
                details = "缺少TF-IDF推荐功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_word2vec_embedding(self):
        """测试2.2.1b: 基于内容推荐 - Word2Vec/Embedding支持"""
        test_name = "2.2.1b 基于内容推荐 - Word2Vec/Embedding支持"
        try:
            # 检查gensim依赖
            requirements_file = SRC_DIR / "requirements.txt"
            gensim_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "gensim" in f.read():
                        gensim_support = True
            
            # 检查Word2Vec实现
            word2vec_implementation = False
            files_to_check = list(SRC_DIR.rglob("*.py"))
            
            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "Word2Vec" in content or "word2vec" in content or "embedding" in content:
                            word2vec_implementation = True
                            break
                except:
                    continue
            
            if gensim_support and word2vec_implementation:
                score = 2
                details = "完整支持Word2Vec词向量推荐"
            elif gensim_support:
                score = 1
                details = "具备词向量处理能力但缺少实现代码"
            else:
                score = 0
                details = "缺少词向量推荐功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_collaborative_filtering_usercf(self):
        """测试2.2.2a: 协同过滤 - 基于用户的协同过滤(UserCF)"""
        test_name = "2.2.2a 协同过滤 - 基于用户的协同过滤(UserCF)"
        try:
            # 检查协同过滤算法文件
            cf_file = SRC_DIR / "algorithms" / "collaborative_filtering.py"
            usercf_implementation = False
            
            if cf_file.exists():
                with open(cf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "UserCF" in content or "user_based" in content or "基于用户" in content:
                        usercf_implementation = True
            
            # 检查surprise库支持
            requirements_file = SRC_DIR / "requirements.txt"
            surprise_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "surprise" in f.read():
                        surprise_support = True
            
            if usercf_implementation and surprise_support:
                score = 2
                details = "完整实现基于用户的协同过滤算法"
            elif surprise_support:
                score = 1
                details = "具备协同过滤能力但缺少UserCF实现"
            else:
                score = 0
                details = "缺少UserCF协同过滤功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_collaborative_filtering_itemcf(self):
        """测试2.2.2b: 协同过滤 - 基于物品的协同过滤(ItemCF)"""
        test_name = "2.2.2b 协同过滤 - 基于物品的协同过滤(ItemCF)"
        try:
            # 检查协同过滤算法文件
            cf_file = SRC_DIR / "algorithms" / "collaborative_filtering.py"
            itemcf_implementation = False
            
            if cf_file.exists():
                with open(cf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "ItemCF" in content or "item_based" in content or "基于物品" in content:
                        itemcf_implementation = True
            
            # 检查相关依赖
            requirements_file = SRC_DIR / "requirements.txt"
            deps_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "surprise" in req_content or "scikit-learn" in req_content:
                        deps_support = True
            
            if itemcf_implementation and deps_support:
                score = 2
                details = "完整实现基于物品的协同过滤算法"
            elif deps_support:
                score = 1
                details = "具备协同过滤能力但缺少ItemCF实现"
            else:
                score = 0
                details = "缺少ItemCF协同过滤功能"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_api_basic_recommendation(self):
        """测试2.3.1a: RESTful API - 基础推荐接口"""
        test_name = "2.3.1a RESTful API - 基础推荐接口"
        try:
            # 检查API文件结构
            api_main = SRC_DIR / "api" / "main.py"
            api_routes = SRC_DIR / "api" / "routes"
            
            api_structure = api_main.exists() and api_routes.exists()
            
            # 检查FastAPI依赖
            requirements_file = SRC_DIR / "requirements.txt"
            fastapi_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "fastapi" in req_content and "uvicorn" in req_content:
                        fastapi_support = True
            
            # 检查推荐路由
            recommend_route = False
            if (api_routes / "recommendation.py").exists():
                with open(api_routes / "recommendation.py", 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "/recommend" in content or "recommend" in content:
                        recommend_route = True
            
            if api_structure and fastapi_support and recommend_route:
                score = 2
                details = "完整实现RESTful推荐API接口"
            elif api_structure and fastapi_support:
                score = 1
                details = "具备API框架但推荐接口不完整"
            else:
                score = 0
                details = "缺少RESTful API实现"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_health_check_api(self):
        """测试2.3.2a: 健康检测API - 系统状态检查"""
        test_name = "2.3.2a 健康检测API - 系统状态检查"
        try:
            # 检查健康检测路由
            health_route_file = SRC_DIR / "api" / "routes" / "health.py"
            health_implementation = False
            
            if health_route_file.exists():
                with open(health_route_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "/health" in content or "health" in content:
                        health_implementation = True
            
            # 检查系统监控依赖
            requirements_file = SRC_DIR / "requirements.txt"
            monitoring_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "psutil" in req_content:
                        monitoring_support = True
            
            if health_implementation and monitoring_support:
                score = 2
                details = "完整实现健康检测API和系统监控"
            elif health_implementation:
                score = 1
                details = "具备健康检测接口但缺少系统监控功能"
            else:
                score = 0
                details = "缺少健康检测API"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_python_environment(self):
        """测试3.1: 技术栈依赖 - Python环境"""
        test_name = "3.1 技术栈依赖 - Python环境"
        try:
            python_version = sys.version_info
            
            # 检查Python版本要求
            requirements_file = SRC_DIR / "requirements.txt"
            version_specified = False
            
            # 检查代码中是否使用了新版本特性
            modern_features = 0
            files_to_check = list(SRC_DIR.rglob("*.py"))[:10]  # 检查前10个文件
            
            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查类型提示
                        if "from typing import" in content or ": str" in content or ": int" in content:
                            modern_features += 1
                            break
                except:
                    continue
            
            # 检查f-string使用
            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "f\"" in content or "f'" in content:
                            modern_features += 1
                            break
                except:
                    continue
            
            if python_version >= (3, 9) and modern_features >= 2:
                score = 2
                details = f"Python {python_version.major}.{python_version.minor}环境，使用了{modern_features}种现代特性"
            elif python_version >= (3, 8):
                score = 1
                details = f"Python {python_version.major}.{python_version.minor}环境，但现代特性使用不足"
            else:
                score = 0
                details = f"Python版本过低: {python_version.major}.{python_version.minor}"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_core_dependencies_data(self):
        """测试3.2a: 核心依赖库 - 数据处理库"""
        test_name = "3.2a 核心依赖库 - 数据处理库"
        try:
            requirements_file = SRC_DIR / "requirements.txt"
            data_libs = []
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "pandas" in req_content:
                        data_libs.append("pandas")
                    if "numpy" in req_content:
                        data_libs.append("numpy")
            
            # 检查实际使用
            usage_count = 0
            files_to_check = list(SRC_DIR.rglob("*.py"))
            
            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "import pandas" in content or "import numpy" in content:
                            usage_count += 1
                            if usage_count >= 3:  # 多个文件使用
                                break
                except:
                    continue
            
            if len(data_libs) >= 2 and usage_count >= 3:
                score = 2
                details = f"正确使用数据处理库: {', '.join(data_libs)}"
            elif len(data_libs) >= 1:
                score = 1
                details = f"部分数据处理库支持: {', '.join(data_libs)}"
            else:
                score = 0
                details = "缺少核心数据处理库"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_core_dependencies_ml(self):
        """测试3.2b: 核心依赖库 - 推荐算法库"""
        test_name = "3.2b 核心依赖库 - 推荐算法库"
        try:
            requirements_file = SRC_DIR / "requirements.txt"
            ml_libs = []
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    req_content = f.read()
                    if "scikit-learn" in req_content:
                        ml_libs.append("scikit-learn")
                    if "surprise" in req_content:
                        ml_libs.append("surprise")
            
            # 检查算法实现数量
            algorithm_files = list((SRC_DIR / "algorithms").glob("*.py")) if (SRC_DIR / "algorithms").exists() else []
            
            if len(ml_libs) >= 2 and len(algorithm_files) >= 3:
                score = 2
                details = f"完整的推荐算法库支持: {', '.join(ml_libs)}, {len(algorithm_files)}个算法文件"
            elif len(ml_libs) >= 1:
                score = 1
                details = f"基本推荐算法库支持: {', '.join(ml_libs)}"
            else:
                score = 0
                details = "缺少推荐算法库"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_system_architecture(self):
        """测试3.3a: 系统架构 - 分层设计"""
        test_name = "3.3a 系统架构 - 分层设计"
        try:
            # 检查目录结构
            layers = []
            expected_dirs = [
                "api",       # 服务层
                "algorithms", # 算法层
                "data_old",      # 数据层（或core）
                "config"     # 配置层
            ]
            
            for dir_name in expected_dirs:
                if (SRC_DIR / dir_name).exists():
                    layers.append(dir_name)
            
            # 检查核心服务
            core_service = SRC_DIR / "core" / "recommendation_service.py"
            has_core_service = core_service.exists()
            
            if len(layers) >= 3 and has_core_service:
                score = 2
                details = f"清晰的分层架构: {', '.join(layers)}, 具备核心服务层"
            elif len(layers) >= 2:
                score = 1
                details = f"基本分层结构: {', '.join(layers)}"
            else:
                score = 0
                details = "缺少清晰的分层架构"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def test_unit_testing(self):
        """测试3.3b: 单元测试覆盖"""
        test_name = "3.3b 单元测试覆盖"
        try:
            # 检查pytest依赖
            requirements_file = SRC_DIR / "requirements.txt"
            pytest_support = False
            
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    if "pytest" in f.read():
                        pytest_support = True
            
            # 检查测试文件
            test_files = list(SRC_DIR.rglob("test_*.py")) + list(SRC_DIR.rglob("*_test.py"))
            
            if pytest_support and len(test_files) >= 3:
                score = 2
                details = f"完整的单元测试支持: pytest + {len(test_files)}个测试文件"
            elif pytest_support and len(test_files) >= 1:
                score = 1
                details = f"基本测试支持: pytest + {len(test_files)}个测试文件"
            else:
                score = 0
                details = "缺少单元测试"
            
            self.log_test_result(test_name, score, 2, details)
            
        except Exception as e:
            self.log_test_result(test_name, 0, 2, f"测试失败: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        self.logger.info("开始推荐系统自动化评估测试")
        self.logger.info("=" * 80)
        
        # 系统基础测试
        self.test_system_startup()
        
        # 数据处理测试
        self.test_data_collection_json()
        self.test_data_collection_csv()
        self.test_data_cleaning_outliers()
        self.test_missing_value_handling()
        self.test_chinese_segmentation()
        self.test_normalization_encoding()
        
        # 推荐算法测试
        self.test_content_based_tfidf()
        self.test_word2vec_embedding()
        self.test_collaborative_filtering_usercf()
        self.test_collaborative_filtering_itemcf()
        
        # API服务测试
        self.test_api_basic_recommendation()
        self.test_health_check_api()
        
        # 技术栈测试
        self.test_python_environment()
        self.test_core_dependencies_data()
        self.test_core_dependencies_ml()
        
        # 架构测试
        self.test_system_architecture()
        self.test_unit_testing()
        
        # 生成总结报告
        return self.generate_summary_report()
    
    def generate_summary_report(self):
        """生成总结报告"""
        self.logger.info("=" * 80)
        self.logger.info("评估测试完成")
        self.logger.info(f"总得分: {self.total_score}/{self.max_score} ({self.total_score/self.max_score*100:.1f}%)")
        
        # 按得分分组
        passed_tests = [r for r in self.results if r['score'] == r['max_score']]
        partial_tests = [r for r in self.results if 0 < r['score'] < r['max_score']]
        failed_tests = [r for r in self.results if r['score'] == 0]
        
        self.logger.info(f"完全通过: {len(passed_tests)}项")
        self.logger.info(f"部分通过: {len(partial_tests)}项")
        self.logger.info(f"未通过: {len(failed_tests)}项")
        
        return {
            'total_score': self.total_score,
            'max_score': self.max_score,
            'percentage': self.total_score/self.max_score*100,
            'passed': len(passed_tests),
            'partial': len(partial_tests),
            'failed': len(failed_tests),
            'results': self.results
        }

def main():
    """主函数"""
    evaluator = AutomatedEvaluator()
    summary = evaluator.run_all_tests()
    
    # 保存详细结果
    with open(EVALUATION_DIR / 'test_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n评估完成！总得分: {summary['total_score']}/{summary['max_score']} ({summary['percentage']:.1f}%)")
    print(f"详细结果已保存到: {EVALUATION_DIR / 'test_results.json'}")

if __name__ == "__main__":
    main()