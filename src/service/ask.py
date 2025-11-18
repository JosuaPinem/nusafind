from flask import Flask, jsonify
from model.model import getRawData, createAnswer, fillterQuestion, saveData, Vis
from db.connection import create_local_connection
import mysql.connector

class askService:
    def ask_service(self, question, session_id):
        fillter = fillterQuestion(question)
        print(fillter)
        if fillter == False or fillter == 'FALSE':
            return "Mohon maaf sebelumnya, permintaan yang Anda ajukan tidak dapat diproses karena tidak sesuai dengan data yang tersedia. Untuk data yang anda butuhkan silahkan hubungi Tim BIS untuk membantu Anda!.", None, None

        if fillter is None:
            return None, None, None
        
        rawData = getRawData(fillter)
        print("sampai sini")
        print(rawData)

        if rawData is None:
            return None, None, None
        
        getchart, vis = Vis(rawData)
        if getchart is None:
            return None, None, None
        
        answer = createAnswer(rawData, fillter, question)
        if answer is None:
            return None, None, None
        save = saveData(session_id, question, fillter, rawData, answer, vis)
        if save is False:
            return "Mohon maaf data tidak berhasil disimpan.", "", ""
        return answer, fillter, getchart
    
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
        
