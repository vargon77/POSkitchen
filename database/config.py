# database/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class DBConfig:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'pos_system') 
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'qwerty')
    DB_PORT = os.getenv('DB_PORT', '5432')