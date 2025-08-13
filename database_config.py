"""
Database configuration and setup for AI Legal Explainer
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create the database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            db_name = os.getenv('DB_NAME', 'ai_legal_explainer')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            print(f"Database '{db_name}' created successfully or already exists")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"Error: {e}")
        print("Please check your MySQL connection settings in .env file")

def test_connection():
    """Test the database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'ai_legal_explainer')
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"You're connected to database: {record[0]}")
            
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            return True
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    print("Setting up database for AI Legal Explainer...")
    create_database()
    test_connection()
