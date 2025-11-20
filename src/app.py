from flask import Flask, jsonify, request, render_template, session, url_for, redirect
from validation.validation import check_input
from service.ask import askService
from service.admin import addUsers, deleteUsers
from service.login import login_service, login_admin, dataUser
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

            return render_template("chat.html", isLogin=True, session_id=session['session_id'], connection=connecions, hisChat=getHistory, sql_key="data_pelanggan")

        # Jika tidak ada riwayat chat
        return render_template("chat.html", isLogin=True, session_id=session['session_id'], connection=connecions, hisChat=None, sql_key="data_pelanggan")
    
    # Jika session_id tidak ada (user belum login)
    if conn is None:
        connecions = "Failed"
        return render_template("chat.html", isLogin=False, session_id=None, connection=connecions, hisChat=None)

    conn.close()
    connecions = "success"
    return render_template("chat.html", isLogin=False, session_id=None, connection=connecions, hisChat=None)

@app.route("/admin", methods=["GET"])
def admin():
    # Cek apakah sudah login
    if session['role'] != "admin":
        return redirect(url_for('home'))

    # Ambil data user / data dashboard
    data = dataUser()  # fungsi ini kamu sudah punya

    if data is None:
        # Terserah mau apa: tampilkan error atau halaman kosong
        return render_template("admin.html", data=None, error="Data tidak dapat ditemukan")

    # Kirim data ke template
    return render_template(
        "admin.html",
        data=data,
        session_id=session["session_id"]
    )

@app.route("/ask", methods=["POST"])
def ask():
    body = request.get_json()
    session_id = session.get('session_id')
    check = check_input(body)
    if check is None:
        return jsonify({"error": "Invalid input"}), 400
    question = body['question']
    answer, query, chartConfig = a.ask_service(question, session_id)
    if answer is None:
        return jsonify({"error": "Failed to get answer"}), 500
    return jsonify({"answer": answer, "query":query, "chartConfig": chartConfig}), 200

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
    session['role'] = 'user'
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
        "hisChat": getHistory,  # Kirim riwayat chat dengan time yang sudah diubah
        'sql_key': "data_pelanggan"
    }), 200

@app.route("/login-admin", methods=['POST'])
def login_admin_route():
    if 'session_id' in session :
       return redirect(url_for('home'))
    body = request.get_json()

    # validasi input
    if not body or 'email' not in body or 'password' not in body:
        return jsonify({
            "error": "Input tidak valid",
            "isLogin": False
        }), 400

    email = body['email']
    password = body['password']

    # cek ke DB
    if not login_admin(email, password):
        return jsonify({
            "error": "Maaf Anda tidak terdaftar!",
            "isLogin": False,
            "session_id": None
        }), 200

    # set session jika berhasil
    session['session_id'] = email
    session['role'] = 'admin'

    # kalau mau ambil data user
    data = dataUser()  # pastikan fungsi ini ada & mengembalikan dict / list
    if data is None:
        return jsonify({
            "error": "Data tidak dapat ditemukan!",
            "isLogin": False
        }), 404

    # kirim response JSON, frontend yang redirect
    return jsonify({
        "message": "Login berhasil",
        "isLogin": True,
        "session_id": session['session_id'],
        "redirect": "/admin",   # sesuaikan jika beda
        "data": data            # kalau mau kirim datanya juga
    }), 200

@app.route("/add-user", methods=["POST"])
def add_user():
    body = request.get_json()

    if not body or "email" not in body or not body["email"]:
        return jsonify({
            "ok": False,
            "error": "Pastikan email valid!"
        }), 400

    email = body["email"]

    if addUsers(email):
        return jsonify({
            "ok": True,
            "email": email,
            "message": "User berhasil ditambahkan"
        }), 200
    else:
        return jsonify({
            "ok": False,
            "error": "Gagal menambahkan user"
        }), 500

@app.route("/delete-user", methods=["POST"])
def delete_user():
    body = request.get_json()

    if not body or "email" not in body or not body["email"]:
        return jsonify({
            "ok": False,
            "error": "Pastikan email valid!"
        }), 400

    email = body["email"]

    if deleteUsers(email):
        return jsonify({
            "ok": True,
            "email": email,
            "message": "User berhasil dihapus"
        }), 200
    else:
        return jsonify({
            "ok": False,
            "error": "Gagal menghapus user"
        }), 500



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
    session.clear()  # hapus semua key di session
    return jsonify({"message": "Logout successful", "isLogin": False}), 200

@app.route("/reset", methods=["GET"])
def reset():
    session.clear()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)