from db.connection import create_connection, create_local_connection
from model.model import getMail
import mysql.connector
from flask import jsonify, request, Flask


# Ganti fungsi login_service di src/service/login.py dengan ini:

def login_service(email):
    get_email = getMail(email)
    if not get_email:
        return False # Email tidak valid atau tidak ditemukan
    
    try:
        conn = create_local_connection()
        if conn is None:
            # Handle database connection failure
            print("Warning: Database connection failed, skipping database check")
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Your existing database logic here
        # Example:
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return user is not None
        
    except Exception as e:
        print(f"Database error in login_service: {e}")
        return False