from db.connection import create_connection, create_local_connection
from model.model import getMail
import mysql.connector
from flask import jsonify, request, Flask


# Ganti fungsi login_service di src/service/login.py dengan ini:

def login_service(email):
    get_email = getMail(email)
    if not get_email:
        return False  # Email tidak valid / tidak ditemukan

    conn = None
    cursor = None
    try:
        conn = create_local_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT session_id FROM users WHERE email = %s", (get_email,))
        row = cursor.fetchone()
        if row is None:
            return False
        return row.get("session_id")  # bisa string, "" atau None sesuai DB

    except mysql.connector.Error as e:
        print(f"Database error in login_service: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()