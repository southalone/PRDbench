# 期望的中文处理和向量化使用示例
import jieba
import gensim
from gensim.models import Word2Vec
from gensim.models.keyedvectors import KeyedVectors

# 1. jieba中文分词
text = "这是一个中文商品标题和描述"
words = jieba.cut(text)
word_list = list(words)

# 2. 去除停用词
stopwords = set(['的', '是', '在', '了', '和'])
filtered_words = [word for word in word_list if word not in stopwords]

# 3. Word2Vec词向量训练
sentences = [['商品', '标题'], ['用户', '推荐'], ['协同', '过滤']]
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1)

# 4. 词向量操作
vector = model.wv['商品']  # 获取词向量
similarity = model.wv.similarity('商品', '标题')  # 计算相似度

# 5. 保存和加载模型
model.save('models/word2vec.model')
loaded_model = Word2Vec.load('models/word2vec.model')

# 6. 文档向量化
def vectorize_document(doc_words, model):
    vectors = [model.wv[word] for word in doc_words if word in model.wv]
    if vectors:
        return sum(vectors) / len(vectors)
    return None