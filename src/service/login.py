from db.connection import create_connection, create_local_connection
from model.model import getMail
import mysql.connector
from flask import jsonify, request, Flask


def login_service(email):
    get_email = getMail(email)
    if not get_email:
        return False  # Email tidak valid atau tidak ditemukan

    conn = create_local_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT session_id FROM users WHERE session_id = %s", (get_email,))
        user = cursor.fetchone()
        if user:
            return user['session_id']  # Hanya kirim session_id ke client
        else:
            return False
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()
