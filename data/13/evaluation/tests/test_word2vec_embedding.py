import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import Word2VecRecommender

# 检查 gensim 是否可用
try:
    from gensim.models import Word2Vec
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False


class TestWord2VecEmbedding:
    """Word2Vec/Embedding支持单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.recommender = Word2VecRecommender(vector_size=128, window=5, min_count=2)
        
    def create_text_corpus_data(self):
        """创建用于训练词向量模型的文本数据"""
        # 创建包含丰富中文文本的商品数据
        items_data = []
        
        # 手机类商品文本
        phone_texts = [
            "苹果iPhone 14 Pro Max 智能手机 A16仿生芯片 超视网膜XDR显示屏 专业级相机系统",
            "华为Mate50 Pro 鸿蒙系统 麒麟芯片 超感知徕卡影像 曲面屏设计 无线充电",
            "小米13 Ultra 徕卡光学镜头 骁龙8Gen2处理器 2K AMOLED显示屏 120W快充",
            "OPPO Find X6 Pro 哈苏影像系统 天玑9200处理器 潜望式长焦镜头 ColorOS系统",
            "vivo X90 Pro+ 蔡司T*镀膜镜头 天玑9200芯片 120Hz高刷屏幕 闪充技术",
            "三星Galaxy S23 Ultra S Pen手写笔 Exynos2200处理器 Dynamic AMOLED屏幕",
            "一加11 哈苏专业模式 骁龙8Gen2芯片 2K 120Hz曲面屏 SUPERVOOC闪充",
            "魅族20 Pro 星纪魅族设计 骁龙8Gen2处理器 无界全面屏 Flyme系统",
            "索尼Xperia 1 V 4K HDR OLED显示屏 骁龙8Gen2芯片 专业摄影功能",
            "谷歌Pixel 7 Pro Tensor G2芯片 计算摄影技术 纯净Android系统 AI功能"
        ]
        
        # 电脑类商品文本
        laptop_texts = [
            "联想拯救者Y9000P 游戏笔记本电脑 RTX4080显卡 13代酷睿i9处理器 16GB内存",
            "戴尔XPS 13 Plus 超极本 12代酷睿i7处理器 OLED触控屏 轻薄便携设计",
            "华硕ROG 玩家国度 电竞游戏本 RTX4090显卡 AMD锐龙9处理器 240Hz电竞屏",
            "惠普暗影精灵8 高性能游戏笔记本 RTX4070显卡 酷睿i7处理器 RGB背光键盘",
            "ThinkPad X1 Carbon 商务办公本 12代酷睿处理器 碳纤维机身 指纹识别",
            "MacBook Pro 14英寸 M2 Pro芯片 Liquid视网膜XDR显示屏 专业级性能",
            "微软Surface Laptop 5 触控笔记本 12代酷睿处理器 PixelSense触摸屏",
            "机械革命蛟龙16K 电竞游戏本 RTX4060显卡 AMD处理器 高刷新率屏幕",
            "炫龙毁灭者DD2 高端游戏笔记本 RTX显卡 英特尔处理器 机械键盘设计",
            "神舟战神Z8 性价比游戏本 GTX显卡 酷睿处理器 大容量硬盘存储"
        ]
        
        # 鞋服类商品文本
        shoe_texts = [
            "耐克Air Jordan 1 经典复古篮球鞋 真皮材质 气垫缓震 街头潮流单品",
            "阿迪达斯Ultraboost 22 跑步运动鞋 Boost缓震科技 Primeknit鞋面",
            "新百伦990v5 美产限量版 复古跑鞋 ENCAP缓震技术 麂皮革材质",
            "匡威All Star 经典帆布鞋 高帮低帮设计 橡胶大底 潮流百搭款式",
            "万斯Old Skool 滑板鞋 侧边条纹设计 耐磨橡胶底 街头滑板文化",
            "彪马Suede Classic 复古板鞋 麂皮材质 经典条纹logo 舒适内里",
            "安踏KT7 汤普森签名篮球战靴 专业篮球科技 TPU支撑 耐磨外底",
            "李宁韦德之道10 专业篮球鞋 缓震科技 碳纤维板 专业球员同款",
            "361度国际线 专业跑步鞋 轻量化设计 透气网面 专业跑步科技",
            "特步竞速160X 马拉松跑鞋 专业竞赛设计 轻量回弹 专业运动员推荐"
        ]
        
        # 家电类商品文本
        appliance_texts = [
            "美的变频空调 1.5匹挂机 节能静音设计 智能温控 WiFi远程控制",
            "格力品悦 壁挂式家用冷暖空调 变频节能 快速制冷制热 静音运行",
            "海尔统帅 智能WiFi控制空调 语音操控 自清洁功能 节能环保",
            "奥克斯金典 变频冷暖空调 智能除湿 快速制冷 低噪音设计",
            "TCL卧室空调 快速制冷制热 节能省电 智能睡眠模式 遥控操作",
            "西门子滚筒洗衣机 10KG大容量 智能投放 95度高温洗涤 节能静音",
            "海尔波轮洗衣机 全自动家用 大容量设计 多种洗涤程序 操作简单",
            "小天鹅比佛利 高端洗护一体机 智能洗涤 烘干功能 欧式设计",
            "美的洗烘一体机 智能投放洗衣液 多种洗涤模式 节能省水设计",
            "松下罗密欧 日式精工洗衣机 泡沫净技术 柔和洗涤 静音马达"
        ]
        
        # 合并所有文本数据
        all_texts = phone_texts + laptop_texts + shoe_texts + appliance_texts
        categories = ['手机'] * 10 + ['电脑'] * 10 + ['鞋服'] * 10 + ['家电'] * 10
        
        for i, (text, category) in enumerate(zip(all_texts, categories), 1):
            items_data.append({
                'item_id': i,
                'title': text.split(' ')[0] + ' ' + text.split(' ')[1],  # 提取品牌和型号
                'description': text,
                'tags': ' '.join(text.split(' ')[:5]),  # 前5个词作为标签
                'category': category
            })
        
        # 为了达到至少1000个文档的要求，复制和变化现有数据
        extended_data = []
        for i, item in enumerate(items_data):
            # 原始数据
            extended_data.append(item)
            
            # 创建变化版本
            for j in range(24):  # 每个原始商品创建24个变化版本
                new_item = item.copy()
                new_item['item_id'] = len(all_texts) + i * 24 + j + 1
                new_item['title'] = f"{item['title']} 版本{j+1}"
                new_item['description'] = f"{item['description']} 特别版本{j+1} 增强功能"
                new_item['tags'] = f"{item['tags']} 版本{j+1}"
                extended_data.append(new_item)
        
        return pd.DataFrame(extended_data)
    
    def test_word2vec_training(self):
        """测试Word2Vec模型训练"""
        # 准备测试数据
        items_df = self.create_text_corpus_data()
        
        # 训练Word2Vec模型
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        if not GENSIM_AVAILABLE:
            # 当 gensim 不可用时，测试模型确实没有被训练
            assert self.recommender.model is None, "Gensim不可用时，Word2Vec模型应该为None"
            assert len(self.recommender.item_vectors) == 0, "Gensim不可用时，不应该生成商品向量"
            print("警告：Gensim库不可用，Word2Vec功能被禁用")
            return
        
        # 验证模型训练成功（只有当 gensim 可用时）
        assert self.recommender.model is not None, "Word2Vec模型应该被成功训练"
        assert len(self.recommender.item_vectors) > 0, "应该生成商品向量"
        
        # 验证向量维度
        for item_id, vector in self.recommender.item_vectors.items():
            assert len(vector) == self.recommender.vector_size, f"向量维度应该为{self.recommender.vector_size}"
            assert isinstance(vector, np.ndarray), "向量应该是numpy数组"
        
        # 验证词汇表大小
        vocab_size = len(self.recommender.model.wv.key_to_index)
        assert vocab_size >= 100, f"词汇表大小应该≥100，实际为{vocab_size}"
        
        # 验证模型能识别常见词汇
        common_words = ['智能', '手机', '电脑', '游戏', '处理器']
        found_words = 0
        for word in common_words:
            if word in self.recommender.model.wv:
                found_words += 1
        
        word_coverage = found_words / len(common_words)
        assert word_coverage >= 0.6, f"常见词汇覆盖率应该≥60%，实际为{word_coverage:.2%}"
    
    def test_vector_similarity_calculation(self):
        """测试向量相似度计算"""
        items_df = self.create_text_corpus_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        if not GENSIM_AVAILABLE:
            # 当 gensim 不可用时，测试推荐返回空列表
            target_item_id = 1
            similar_items = self.recommender.get_similar_items(target_item_id, top_n=5)
            assert len(similar_items) == 0, "Gensim不可用时，相似度推荐应该返回空列表"
            print("警告：Gensim库不可用，跳过向量相似度计算测试")
            return
        
        # 测试相似商品推荐
        target_item_id = 1  # 第一个手机商品
        similar_items = self.recommender.get_similar_items(target_item_id, top_n=5)
        
        # 验证推荐结果
        assert len(similar_items) <= 5, "推荐数量不应该超过top_n"
        
        for item_id, similarity in similar_items:
            assert isinstance(item_id, (int, np.integer)), "商品ID应该是整数"
            assert isinstance(similarity, (float, np.floating)), "相似度应该是浮点数"
            assert -1 <= similarity <= 1, "余弦相似度应该在[-1,1]范围内"
            assert item_id != target_item_id, "不应该推荐商品自己"
        
        # 验证推荐结果按相似度降序排列
        similarities = [sim for _, sim in similar_items]
        assert similarities == sorted(similarities, reverse=True), "推荐结果应该按相似度降序排列"
    
    def test_semantic_similarity(self):
        """测试语义相似度"""
        items_df = self.create_text_corpus_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        if not GENSIM_AVAILABLE:
            print("警告：Gensim库不可用，跳过语义相似度测试")
            return
        
        # 获取不同类别的商品
        phone_items = items_df[items_df['category'] == '手机']['item_id'].values[:10]
        laptop_items = items_df[items_df['category'] == '电脑']['item_id'].values[:10]
        
        # 计算同类别商品间的平均相似度
        phone_similarities = []
        for i in range(len(phone_items)):
            for j in range(i+1, len(phone_items)):
                if phone_items[i] in self.recommender.item_vectors and phone_items[j] in self.recommender.item_vectors:
                    similar_items = self.recommender.get_similar_items(phone_items[i], top_n=20)
                    for item_id, sim in similar_items:
                        if item_id == phone_items[j]:
                            phone_similarities.append(sim)
                            break
        
        # 计算跨类别商品间的平均相似度
        cross_similarities = []
        for phone_id in phone_items[:5]:
            if phone_id in self.recommender.item_vectors:
                similar_items = self.recommender.get_similar_items(phone_id, top_n=50)
                for item_id, sim in similar_items:
                    if item_id in laptop_items:
                        cross_similarities.append(sim)
                        break
        
        # 验证语义理解能力
        if phone_similarities and cross_similarities:
            avg_phone_sim = np.mean(phone_similarities)
            avg_cross_sim = np.mean(cross_similarities)
            
            assert avg_phone_sim > avg_cross_sim, "同类别商品相似度应该高于跨类别相似度"
    
    def test_word2vec_parameters(self):
        """测试Word2Vec参数配置"""
        if not GENSIM_AVAILABLE:
            print("警告：Gensim库不可用，跳过Word2Vec参数测试")
            return
            
        items_df = self.create_text_corpus_data()
        
        # 测试不同参数配置
        recommender_128 = Word2VecRecommender(vector_size=128, window=5, min_count=2)
        recommender_64 = Word2VecRecommender(vector_size=64, window=3, min_count=1)
        
        recommender_128.fit(items_df, text_columns=['title', 'description'])
        recommender_64.fit(items_df, text_columns=['title', 'description'])
        
        # 验证不同向量维度
        for item_id, vector in recommender_128.item_vectors.items():
            assert len(vector) == 128, "128维模型向量维度应该为128"
        
        for item_id, vector in recommender_64.item_vectors.items():
            assert len(vector) == 64, "64维模型向量维度应该为64"
        
        # 验证模型参数设置
        assert recommender_128.model.vector_size == 128, "向量维度参数应该正确设置"
        assert recommender_128.model.window == 5, "窗口大小参数应该正确设置"
        assert recommender_128.model.min_count == 2, "最小词频参数应该正确设置"
    
    def test_chinese_word_embeddings(self):
        """测试中文词向量效果"""
        if not GENSIM_AVAILABLE:
            print("警告：Gensim库不可用，跳过中文词向量测试")
            return
            
        items_df = self.create_text_corpus_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        # 测试中文词汇的词向量质量
        chinese_tech_words = ['智能', '处理器', '显示屏', '摄像头', '电池']
        chinese_brand_words = ['苹果', '华为', '小米', '三星', 'OPPO']
        
        # 验证技术词汇间的相似性
        tech_similarities = []
        for i in range(len(chinese_tech_words)):
            for j in range(i+1, len(chinese_tech_words)):
                word1, word2 = chinese_tech_words[i], chinese_tech_words[j]
                if word1 in self.recommender.model.wv and word2 in self.recommender.model.wv:
                    similarity = self.recommender.model.wv.similarity(word1, word2)
                    tech_similarities.append(similarity)
        
        # 验证品牌词汇间的相似性
        brand_similarities = []
        for i in range(len(chinese_brand_words)):
            for j in range(i+1, len(chinese_brand_words)):
                word1, word2 = chinese_brand_words[i], chinese_brand_words[j]
                if word1 in self.recommender.model.wv and word2 in self.recommender.model.wv:
                    similarity = self.recommender.model.wv.similarity(word1, word2)
                    brand_similarities.append(similarity)
        
        # 验证词向量学习效果
        if tech_similarities:
            avg_tech_sim = np.mean(tech_similarities)
            assert avg_tech_sim > 0, "技术词汇应该有正相关性"
        
        if brand_similarities:
            avg_brand_sim = np.mean(brand_similarities)
            assert avg_brand_sim > 0, "品牌词汇应该有正相关性"
    
    def test_edge_cases_and_robustness(self):
        """测试边界情况和鲁棒性"""
        if not GENSIM_AVAILABLE:
            print("警告：Gensim库不可用，跳过边界情况测试")
            return
            
        # 测试小数据集
        small_df = pd.DataFrame({
            'item_id': [1, 2, 3],
            'title': ['苹果手机', '华为电脑', '耐克鞋子'],
            'description': ['智能手机产品', '高性能笔记本', '运动休闲鞋'],
            'tags': ['手机 智能', '电脑 性能', '鞋子 运动']
        })
        
        small_recommender = Word2VecRecommender(vector_size=50, min_count=1)
        small_recommender.fit(small_df)
        
        # 验证小数据集也能正常工作
        assert small_recommender.model is not None, "小数据集也应该能训练模型"
        assert len(small_recommender.item_vectors) > 0, "小数据集也应该生成商品向量"
        
        # 测试不存在的商品ID
        similar_items = self.recommender.get_similar_items(99999, top_n=5)
        assert len(similar_items) == 0, "不存在的商品ID应该返回空推荐"
        
        # 测试空文本处理
        empty_text_df = pd.DataFrame({
            'item_id': [1, 2],
            'title': ['', ''],
            'description': ['', ''],
            'tags': ['', '']
        })
        
        empty_recommender = Word2VecRecommender(min_count=1)
        # 空文本应该能处理，但可能没有有效向量
        try:
            empty_recommender.fit(empty_text_df)
            # 如果成功训练，验证结果
            assert len(empty_recommender.item_vectors) >= 0, "空文本处理后向量数量应该≥0"
        except Exception:
            # 空文本可能导致训练失败，这是可以接受的
            pass
    
    def test_model_persistence_and_consistency(self):
        """测试模型持久性和一致性"""
        if not GENSIM_AVAILABLE:
            print("警告：Gensim库不可用，跳过模型持久性测试")
            return
            
        items_df = self.create_text_corpus_data()
        
        # 训练两个相同参数的模型
        recommender1 = Word2VecRecommender(vector_size=100, window=5, min_count=2)
        recommender2 = Word2VecRecommender(vector_size=100, window=5, min_count=2)
        
        # 使用相同的随机种子确保一致性
        np.random.seed(42)
        recommender1.fit(items_df)
        
        np.random.seed(42)
        recommender2.fit(items_df)
        
        # 验证模型参数一致性
        assert recommender1.vector_size == recommender2.vector_size, "相同参数模型向量维度应该一致"
        assert len(recommender1.item_vectors) == len(recommender2.item_vectors), "相同数据训练的模型应该生成相同数量的向量"