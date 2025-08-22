from flask import Flask, jsonify, request, render_template, session, url_for
from validation.validation import check_input
from service.ask import askService
from service.login import login_service
from db.connection import create_connection

a = askService()

app = Flask(__name__)
app.secret_key = 'nusafind010'

from datetime import timedelta

@app.route("/")
def home():
    conn = create_connection()
    # Cek apakah session_id ada
    if session.get('session_id'):
        if conn is None:
            # Koneksi gagal
            connecions = "Failed"
            return render_template("chat.html", isLogin=False, session_id=None, connection=connecions, hisChat=None)

        connecions = "success"
        getHistory = a.getChatHis(session['session_id'])

        # Jika ada riwayat chat
        if getHistory:
            # Konversi timedelta ke string (HH:MM:SS) jika ada
            for chat in getHistory:
                if isinstance(chat['time'], timedelta):
                    chat['time'] = timedelta_to_string(chat['time'])  # Convert to HH:MM:SS

            return render_template("chat.html", isLogin=True, session_id=session['session_id'], connection=connecions, hisChat=getHistory)

        # Jika tidak ada riwayat chat
        return render_template("chat.html", isLogin=True, session_id=session['session_id'], connection=connecions, hisChat=None)
    
    # Jika session_id tidak ada (user belum login)
    if conn is None:
        connecions = "Failed"
        return render_template("chat.html", isLogin=False, session_id=None, connection=connecions, hisChat=None)

    conn.close()
    connecions = "success"
    return render_template("chat.html", isLogin=False, session_id=None, connection=connecions, hisChat=None)


@app.route("/ask", methods=["POST"])
def ask():
    body = request.get_json()
    session_id = session.get('session_id')
    check = check_input(body)
    if check is None:
        return jsonify({"error": "Invalid input"}), 400
    question = body['question']
    answer = a.ask_service(question, session_id)
    if answer is None:
        return jsonify({"error": "Failed to get answer"}), 500
    return jsonify({"answer": answer}), 200

@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    if not body or 'question' not in body:
        return jsonify({"error": "Input tidak valid"}), 400

    email = body['question']
    answer = login_service(email)
    if answer is False:
        return jsonify({"error": "Maaf Anda tidak terdaftar!", "isLogin": False, "session_id": None}), 200

    session['session_id'] = answer
    getHistory = a.getChatHis(session['session_id'])

    # Konversi timedelta ke string atau detik
    for chat in getHistory:
        if isinstance(chat['time'], timedelta):  # Jika time adalah timedelta
            chat['time'] = timedelta_to_string(chat['time'])  # Convert to HH:MM:SS
            # atau jika lebih suka detik
            # chat['time'] = timedelta_to_seconds(chat['time'])  # Convert to total seconds

    return jsonify({
        "answer": answer, 
        "isLogin": True, 
        "session_id": session['session_id'], 
        "hisChat": getHistory  # Kirim riwayat chat dengan time yang sudah diubah
    }), 200

# Fungsi untuk mengonversi timedelta ke string (HH:MM:SS)
def timedelta_to_string(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}"

from datetime import timedelta

def timedelta_to_seconds(timedelta_obj):
    return timedelta_obj.total_seconds()


@app.route("/logout", methods=["GET"])
def logout():
    session.pop('session_id', None)
    return jsonify({"message": "Logout successful", "isLogin": False}), 200

@app.route("/reset", methods=["GET"])
def reset():
    session.pop('session_id', None)
    return url_for('home')


if __name__ == "__main__":
    app.run(debug=True)