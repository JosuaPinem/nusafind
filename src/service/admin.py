from db.connection import create_local_connection

def addUsers(email: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = create_local_connection()
        if conn is None:
            print("Warning: Database connection failed")
            return False

        cursor = conn.cursor()

        # INSERT data user
        sql = "INSERT INTO users (session_id) VALUES (%s)"
        cursor.execute(sql, (email,))

        # simpan perubahan
        conn.commit()

        return True

    except Exception as e:
        print(f"Database error in addUsers: {e}")
        return False

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()



def deleteUsers(email: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = create_local_connection()
        if conn is None:
            print("Warning: Database connection failed")
            return False
            
        cursor = conn.cursor()

        sql = "DELETE FROM users WHERE session_id = %s"
        cursor.execute(sql, (email,))

        conn.commit()  # penting supaya perubahan tersimpan

        return True

    except Exception as e:
        print(f"Database error in deleteUsers: {e}")
        return False

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()