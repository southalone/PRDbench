import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_old.preprocessor import DataPreprocessor


class TestDataNormalizationEncoding:
    """数据归一化与编码单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.preprocessor = DataPreprocessor()
        
    def create_raw_features_data(self):
        """创建包含不同类型特征的原始数据"""
        np.random.seed(42)
        
        data = {
            # 数值型特征 (5个字段)
            'age': np.random.randint(18, 80, 100),
            'income': np.random.normal(50000, 20000, 100),
            'price': np.random.uniform(10, 1000, 100),
            'rating': np.random.uniform(1, 5, 100),
            'quantity': np.random.poisson(5, 100),
            
            # 类别型特征 (3个字段)
            'gender': np.random.choice(['男', '女', '其他'], 100),
            'category': np.random.choice(['电子产品', '服装', '食品', '图书', '家居'], 100),
            'brand': np.random.choice(['华为', '苹果', '小米', '三星', 'OPPO'], 100),
            
            # 文本型特征 (2个字段)
            'title': [f"商品标题{i}" for i in range(100)],
            'description': [f"这是商品{i}的详细描述信息" for i in range(100)]
        }
        
        return pd.DataFrame(data)
    
    def test_data_normalization_encoding(self):
        """测试数据归一化和编码功能"""
        # 准备测试数据
        df = self.create_raw_features_data()
        
        # 定义特征类型
        numerical_columns = ['age', 'income', 'price', 'rating', 'quantity']
        categorical_columns = ['gender', 'category', 'brand']
        text_columns = ['title', 'description']
        
        # 执行归一化
        normalized_df = self.preprocessor.normalize_numerical_features(df.copy(), numerical_columns)
        
        # 验证归一化结果
        for col in numerical_columns:
            normalized_col = f'{col}_normalized'
            assert normalized_col in normalized_df.columns, f"应该创建{normalized_col}列"
            
            # 验证归一化后的值域（StandardScaler：均值约为0，标准差约为1）
            normalized_values = normalized_df[normalized_col]
            assert abs(normalized_values.mean()) < 0.1, f"{normalized_col}的均值应该接近0"
            assert abs(normalized_values.std() - 1.0) < 0.1, f"{normalized_col}的标准差应该接近1"
        
        # 执行分类编码
        encoded_df = self.preprocessor.encode_categorical_features(normalized_df, categorical_columns)
        
        # 验证编码结果
        for col in categorical_columns:
            encoded_col = f'{col}_encoded'
            assert encoded_col in encoded_df.columns, f"应该创建{encoded_col}列"
            
            # 验证编码值为整数
            assert encoded_df[encoded_col].dtype in [np.int32, np.int64], f"{encoded_col}应该是整数类型"
            
            # 验证编码值范围合理
            unique_original = df[col].nunique()
            unique_encoded = encoded_df[encoded_col].nunique()
            assert unique_encoded == unique_original, f"{encoded_col}的唯一值数量应该与原始列相同"
        
        # 执行文本特征处理
        text_processed_df = self.preprocessor.process_text_features(encoded_df, text_columns)
        
        # 验证文本处理结果
        for col in text_columns:
            segmented_col = f'{col}_segmented'
            cleaned_col = f'{col}_cleaned'
            assert segmented_col in text_processed_df.columns, f"应该创建{segmented_col}列"
            assert cleaned_col in text_processed_df.columns, f"应该创建{cleaned_col}列"
    
    def test_feature_type_recognition(self):
        """测试特征类型自动识别"""
        df = self.create_raw_features_data()
        
        # 识别数值型特征
        numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
        expected_numeric = ['age', 'income', 'price', 'rating', 'quantity']
        
        for feature in expected_numeric:
            assert feature in numeric_features, f"{feature}应该被识别为数值型特征"
        
        # 识别分类型特征
        categorical_features = df.select_dtypes(include=['object']).columns.tolist()
        expected_categorical = ['gender', 'category', 'brand', 'title', 'description']
        
        for feature in expected_categorical:
            assert feature in categorical_features, f"{feature}应该被识别为分类型特征"
        
        # 验证特征类型识别准确率
        total_features = len(df.columns)
        correctly_identified = len(numeric_features) + len(categorical_features)
        accuracy = correctly_identified / total_features
        
        assert accuracy >= 0.9, f"特征类型识别准确率应该≥90%，实际为{accuracy:.2%}"
    
    def test_normalization_methods(self):
        """测试不同的归一化方法"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5, 100],  # 包含极值
            'feature2': [10, 20, 30, 40, 50, 60],  # 正常分布
            'feature3': [-10, -5, 0, 5, 10, 15]  # 包含负值
        })
        
        # 测试StandardScaler归一化
        normalized_df = self.preprocessor.normalize_numerical_features(
            test_data.copy(), ['feature1', 'feature2', 'feature3']
        )
        
        for col in ['feature1', 'feature2', 'feature3']:
            normalized_col = f'{col}_normalized'
            values = normalized_df[normalized_col]
            
            # 验证标准化后的统计特性
            assert abs(values.mean()) < 0.1, f"{normalized_col}均值应该接近0"
            assert abs(values.std() - 1.0) < 0.1, f"{normalized_col}标准差应该接近1"
    
    def test_encoding_methods(self):
        """测试不同的编码方法"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'low_cardinality': ['A', 'B', 'C', 'A', 'B', 'C'],  # 低基数
            'high_cardinality': [f'cat_{i}' for i in range(6)],  # 高基数
            'ordinal_feature': ['低', '中', '高', '低', '中', '高']  # 有序特征
        })
        
        # 测试标签编码
        encoded_df = self.preprocessor.encode_categorical_features(
            test_data.copy(), ['low_cardinality', 'high_cardinality', 'ordinal_feature']
        )
        
        # 验证编码结果
        for col in ['low_cardinality', 'high_cardinality', 'ordinal_feature']:
            encoded_col = f'{col}_encoded'
            
            # 验证编码值类型和范围
            assert encoded_df[encoded_col].dtype in [np.int32, np.int64], f"{encoded_col}应该是整数类型"
            assert encoded_df[encoded_col].min() >= 0, f"{encoded_col}最小值应该≥0"
            
            # 验证编码的一致性
            original_unique = test_data[col].nunique()
            encoded_unique = encoded_df[encoded_col].nunique()
            assert encoded_unique == original_unique, f"{encoded_col}唯一值数量应该保持一致"
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试空数据框
        empty_df = pd.DataFrame()
        
        result1 = self.preprocessor.normalize_numerical_features(empty_df, [])
        assert len(result1) == 0, "空数据框归一化应该返回空结果"
        
        result2 = self.preprocessor.encode_categorical_features(empty_df, [])
        assert len(result2) == 0, "空数据框编码应该返回空结果"
        
        # 测试只有一个唯一值的列
        constant_df = pd.DataFrame({
            'constant_num': [5, 5, 5, 5, 5],
            'constant_cat': ['A', 'A', 'A', 'A', 'A']
        })
        
        # 常数数值列的归一化
        normalized_constant = self.preprocessor.normalize_numerical_features(
            constant_df.copy(), ['constant_num']
        )
        # 标准差为0的列，归一化后应该全为0或保持原值
        assert 'constant_num_normalized' in normalized_constant.columns, "应该创建归一化列"
        
        # 常数分类列的编码
        encoded_constant = self.preprocessor.encode_categorical_features(
            constant_df.copy(), ['constant_cat']
        )
        encoded_values = encoded_constant['constant_cat_encoded']
        assert encoded_values.nunique() == 1, "常数分类列编码后应该只有一个唯一值"
        assert all(encoded_values == encoded_values.iloc[0]), "常数分类列编码后所有值应该相同"
    
    def test_comprehensive_pipeline(self):
        """测试完整的预处理流水线"""
        # 创建复杂的测试数据
        df = self.create_raw_features_data()
        
        # 添加一些缺失值和异常值
        df.loc[0:4, 'age'] = np.nan
        df.loc[5, 'income'] = -50000  # 异常的负收入
        df.loc[6, 'price'] = 10000   # 异常的高价格
        
        # 执行完整的数据清洗和预处理
        processed_df = self.preprocessor.clean_data(df.copy())
        
        # 继续执行特征工程
        numerical_columns = ['age', 'income', 'price', 'rating', 'quantity']
        categorical_columns = ['gender', 'category', 'brand']
        text_columns = ['title', 'description']
        
        # 归一化数值特征
        processed_df = self.preprocessor.normalize_numerical_features(processed_df, numerical_columns)
        
        # 编码分类特征
        processed_df = self.preprocessor.encode_categorical_features(processed_df, categorical_columns)
        
        # 处理文本特征
        processed_df = self.preprocessor.process_text_features(processed_df, text_columns)
        
        # 验证最终结果
        # 1. 无缺失值
        assert processed_df.isnull().sum().sum() == 0, "处理后不应该有缺失值"
        
        # 2. 包含归一化列
        for col in numerical_columns:
            assert f'{col}_normalized' in processed_df.columns, f"应该包含{col}_normalized列"
        
        # 3. 包含编码列
        for col in categorical_columns:
            assert f'{col}_encoded' in processed_df.columns, f"应该包含{col}_encoded列"
        
        # 4. 包含文本处理列
        for col in text_columns:
            assert f'{col}_segmented' in processed_df.columns, f"应该包含{col}_segmented列"
            assert f'{col}_cleaned' in processed_df.columns, f"应该包含{col}_cleaned列"
        
        # 5. 数据完整性
        assert len(processed_df) == len(df), "处理后行数应该保持不变"