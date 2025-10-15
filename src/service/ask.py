from flask import Flask, jsonify
from src.model.model import createQuery, getRawData, createAnswer, fillterQuestion, saveData, isQuery, Vis
from src.db.connection import create_local_connection
import mysql.connector

class askService:
    def ask_service(self, question, session_id):
        isquery = isQuery(question)
        if isquery == "Tidak":
            fillter = fillterQuestion(question)
            if fillter == "False":
                return "Mohon maaf sebelumnya, permintaan yang Anda ajukan tidak dapat diproses karena tidak sesuai dengan data yang tersedia. Untuk data yang anda butuhkan silahkan hubungi Tim BIS untuk membantu Anda!.", None, None

        query = createQuery(question)

        if query is None:
            return None, None, None
        
        rawData = getRawData(query)

        if rawData is None:
            return None, None, None
        
        getchart, vis = Vis(rawData)
        if getchart is None:
            return None, None, None
        
        answer = createAnswer(rawData, query, question)
        if answer is None:
            return None, None, None
        save = saveData(session_id, question, query, rawData, answer, vis)
        if save is False:
            return "Mohon maaf data tidak berhasil disimpan.", "", ""
        return answer, query, getchart
    
    def getChatHis(self, session_id):
        conn = create_local_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM log WHERE session_id = %s ORDER BY id DESC LIMIT 4", (session_id,))
            history = cursor.fetchall()
            return history
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()
            conn.close()
        
