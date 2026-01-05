from flask import Flask, jsonify
from model.model import getRawData, createAnswer, fillterQuestion, saveData, Vis
from db.connection import create_local_connection
import mysql.connector, time

class askService:
    def ask_service(self, question, session_id):
        fillter = fillterQuestion(question)
        print(fillter)
        if fillter == False:
            return "Mohon maaf sebelumnya, permintaan yang Anda ajukan tidak dapat diproses karena tidak sesuai dengan data yang tersedia. Untuk data yang anda butuhkan silahkan hubungi Tim BIS untuk membantu Anda!.", None, None

        if fillter is None:
            return None, None, None
        
        rawData = getRawData(fillter)
        print("sampai sini")
        print(rawData)

        if rawData is None:
            return None, None, None
        print("masuk visualisasi")
        start_vis = time.perf_counter()

        getchart, vis = Vis(rawData)

        end_vis = time.perf_counter()
        print(f"keluar visualisasi (durasi: {end_vis - start_vis:.4f} detik)")

        print("masuk create jawaban")
        start_create = time.perf_counter()

        answer = createAnswer(rawData, fillter, question)

        end_create = time.perf_counter()
        print(f"keluar create jawaban (durasi: {end_create - start_create:.4f} detik)")

        if answer is None:
            return None, None, None

        print("masuk simpan data")
        start_save = time.perf_counter()

        save = saveData(session_id, question, fillter, rawData, answer, vis)

        end_save = time.perf_counter()
        print(f"keluar simpan data (durasi: {end_save - start_save:.4f} detik)")

        if save is False:
            return "Mohon maaf data tidak berhasil disimpan.", "", ""

        print(answer)

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
        
