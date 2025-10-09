# 期望的推荐算法库使用示例
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from surprise import Dataset, Reader, SVD, KNNBasic

# 1. TF-IDF特征提取
tfidf = TfidfVectorizer(max_features=5000)
tfidf_matrix = tfidf.fit_transform(documents)

# 2. 相似度计算
similarity_matrix = cosine_similarity(tfidf_matrix)

# 3. 矩阵分解
svd = TruncatedSVD(n_components=50)
reduced_matrix = svd.fit_transform(user_item_matrix)

# 4. Surprise库协同过滤
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df, reader)
algo = SVD(n_factors=50, n_epochs=20)
algo.fit(trainset)

# 5. KNN算法
knn_algo = KNNBasic(sim_options={'name': 'cosine', 'user_based': True})
knn_algo.fit(trainset)