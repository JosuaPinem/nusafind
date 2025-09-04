from flask import Flask, jsonify
from model.model import createQuery, getRawData, createAnswer, fillterQuestion, saveData, isQuery
from db.connection import create_local_connection
import mysql.connector

class askService:
    def ask_service(self, question, session_id):
        isquery = isQuery(question)
        if isquery == "Tidak":
            fillter = fillterQuestion(question)
            if fillter == "False":
                return "Mohon maaf sebelumnya, permintaan yang Anda ajukan tidak dapat diproses karena tidak sesuai dengan data yang tersedia. Untuk data yang anda butuhkan silahkan hubungi Tim BIS untuk membantu Anda!.", None

        query = createQuery(question)

        if query is None:
            return None, None
        
        rawData = getRawData(query)

        if rawData is None:
            return None, None
        
        answer = createAnswer(rawData, query, question)
        if answer is None:
            return None, None
        save = saveData(session_id, question, query, rawData, answer)
        if save is False:
            return "Mohon maaf data tidak berhasil disimpan.", ""
        return answer, query
    
    def getChatHis(self, session_id):
        conn = create_local_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM log WHERE session_id = %s ORDER BY time DESC LIMIT 4", (session_id,))
            history = cursor.fetchall()
            return history
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()
            conn.close()
        
