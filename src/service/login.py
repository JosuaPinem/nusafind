from db.connection import create_connection, create_local_connection
from model.model import getMail
import mysql.connector
from flask import jsonify, request, Flask


def login_service(email):
    get_email = getMail(email)
    if not get_email:
        return False  # email tidak valid / tidak ditemukan

    conn = None
    cursor = None
    try:
        conn = create_local_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT session_id FROM users WHERE email = %s", (get_email,))
        row = cursor.fetchone()
        if not row:
            return False
        # Ambil session_id persis dari DB (bisa string, "", atau None)
        return row.get("session_id")

    except mysql.connector.Error as e:
        print(f"Database error in login_service: {e}")
        return False

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass