# 期望的缓存和数据库使用示例
import redis
import mysql.connector
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Redis缓存连接
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 2. Redis缓存操作
def cache_recommendation(user_id, recommendations):
    key = f"rec:{user_id}"
    redis_client.setex(key, 3600, str(recommendations))  # 1小时过期

def get_cached_recommendation(user_id):
    key = f"rec:{user_id}"
    return redis_client.get(key)

# 3. MySQL数据库连接
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'recommendation_db'
}
connection = mysql.connector.connect(**mysql_config)

# 4. SQLAlchemy ORM
engine = create_engine('mysql+pymysql://user:password@localhost/recommendation_db')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(100))

# 5. 数据库会话
Session = sessionmaker(bind=engine)
session = Session()

# 6. 数据持久化操作
def save_user_interaction(user_id, item_id, rating):
    query = "INSERT INTO interactions (user_id, item_id, rating) VALUES (%s, %s, %s)"
    cursor = connection.cursor()
    cursor.execute(query, (user_id, item_id, rating))
    connection.commit()