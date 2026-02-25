import pytest
import sqlite3
import os
import sys
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from database.db import DataBase


class TestDatabaseCreation:
    """测试数据库和表结构创建功能"""
    
    def test_database_table_creation(self):
        """测试数据库文件创建和表结构创建功能"""
        # 创建临时数据库文件路径
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_db_path = temp_file.name
        
        try:
            # 确保临时文件不存在（测试从零创建）
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            
            # 创建数据库实例
            db = DataBase(temp_db_path)
            
            # 验证数据库文件是否被创建
            assert os.path.exists(temp_db_path), "数据库文件应该被创建"
            
            # 创建表结构
            db.create_tables()
            
            # 验证表是否存在
            cursor = db.cursor
            
            # 检查doc表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='doc'")
            doc_table = cursor.fetchone()
            assert doc_table is not None, "doc表应该存在"
            
            # 检查word表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='word'")
            word_table = cursor.fetchone()
            assert word_table is not None, "word表应该存在"
            
            # 验证doc表结构
            cursor.execute("PRAGMA table_info(doc)")
            doc_columns = cursor.fetchall()
            doc_column_names = [col[1] for col in doc_columns]
            expected_doc_columns = ['id', 'title', 'link']
            for col in expected_doc_columns:
                assert col in doc_column_names, f"doc表应该包含{col}列"
            
            # 验证word表结构
            cursor.execute("PRAGMA table_info(word)")
            word_columns = cursor.fetchall()
            word_column_names = [col[1] for col in word_columns]
            expected_word_columns = ['term', 'list']
            for col in expected_word_columns:
                assert col in word_column_names, f"word表应该包含{col}列"
            
            # 验证主键约束
            doc_pk = [col for col in doc_columns if col[5] == 1]  # pk字段为1表示主键
            assert len(doc_pk) == 1 and doc_pk[0][1] == 'id', "doc表的id应该是主键"
            
            word_pk = [col for col in word_columns if col[5] == 1]
            assert len(word_pk) == 1 and word_pk[0][1] == 'term', "word表的term应该是主键"
            
            # 关闭数据库连接
            db.close()
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)


if __name__ == "__main__":
    pytest.main([__file__])