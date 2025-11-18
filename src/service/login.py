from db.connection import create_connection, create_local_connection
from model.model import getMail
import mysql.connector
from flask import jsonify, request, Flask
import bcrypt


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
        query = "SELECT session_id FROM users WHERE session_id = %s"
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

def login_admin(email, password):
    conn = None
    cursor = None
    try:
        conn = create_local_connection()
        if conn is None:
            print("Warning: Database connection failed")
            return False
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, email, password FROM super_admin WHERE email = %s LIMIT 1",
            (email,),
        )
        admin = cursor.fetchone()

        if not admin:
            # Email tidak ditemukan
            return False

        # Ambil hash password dari kolom `password`
        if not admin["password"]:
            # Kalau kolom kosong / NULL
            return False

        stored_hash = admin["password"].encode("utf-8")   # hash dari DB (string -> bytes)
        plain = password.encode("utf-8")                  # password input (string -> bytes)

        # cek password dengan bcrypt
        if bcrypt.checkpw(plain, stored_hash):
            # password benar
            return True
        else:
            # password salah
            return False

    except Exception as e:
        print(f"Database error in login_service: {e}")
        return False
            
    finally:
        # Pastikan cleanup selalu terjadi & tidak error kalau None
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def dataUser():
    try: 
        conn = create_local_connection()
        if conn is None:
            print("Warning: Database connection failed")
            return False
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users"
        )
        data = cursor.fetchall()
        if not data:
            return None
        return data
    except Exception as e:
            print(f"Database error in login_service: {e}")
            return False
    finally:
        # Pastikan cleanup selalu terjadi
        if cursor:
            cursor.close()
        if conn:
            conn.close() 