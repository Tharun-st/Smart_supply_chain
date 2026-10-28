"""
Intelligent Supply Chain Management System
Configuration Settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supply_chain_academic_secret_key_2026")
    
    # MySQL Database Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")  # Enter your MySQL root password here or in .env
    MYSQL_DB = os.getenv("MYSQL_DB", "supply_chain_db")
    
    # Fallback SQLite DB path if MySQL is offline or password not configured
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "database", "supply_chain.db")
    
    # Logistics Algorithm Constants
    TRANSPORT_COST_PER_KM = float(os.getenv("TRANSPORT_COST_PER_KM", 18.0))
    BASE_HANDLING_FEE = float(os.getenv("BASE_HANDLING_FEE", 150.0))
    LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", 50))
    
    # Flask Settings
    DEBUG = True
    JSON_SORT_KEYS = False
