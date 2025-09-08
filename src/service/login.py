from db.connection import create_connection, create_local_connection
from model.model import getMail
import mysql.connector
from flask import jsonify, request, Flask


# Ganti fungsi login_service di src/service/login.py dengan ini:

def login_service(email):
    get_email = getMail(email)
    if not get_email:
        return False  # Email tidak valid atau tidak ditemukan
    
    conn = None
    cursor = None
    
    try:
        conn = create_local_connection()
        if conn is None:
            print("Warning: Database connection failed")
            return False
            
        cursor = conn.cursor(dictionary=True)
        
        # Query untuk mencari user dan session_id
        query = "SELECT session_id FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if user:
            # Return session_id dari database (bisa string, empty string, atau None)
            return user.get("session_id")
        else:
            # User tidak ditemukan
            return False
            
    except Exception as e:
        print(f"Database error in login_service: {e}")
        return False
        
    finally:
        # Pastikan cleanup selalu terjadi
        if cursor:
            cursor.close()
        if conn:
            conn.close()