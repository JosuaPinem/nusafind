from langchain_core.prompts import PromptTemplate

promptGetAnswer = PromptTemplate.from_template(
    """
    Kamu menjawab pertanyaan user berdasarkan data dari database.

    Data hasil query (JSON/list of dict):
    {rawData}

    Query SQL:
    {query}

    Pertanyaan:
    {question}

    Aturan:
    - Jawab HANYA berdasarkan data di atas.
    - Jika data tidak ditemukan atau tidak relevan, jawab:
      "Mohon maaf, data belum tersedia. Silakan hubungi admin Nusafind."
    - Jangan menambah penjelasan lain di luar jawaban tersebut.
    - Setiap nilai service_price atau amount ditulis dalam format Rupiah, contoh: Rp 100.000,00.
    - Jika sesuai, tambahkan visualisasi dalam bentuk tabel HTML dengan inline CSS:
      * Gunakan hanya tag <table>, <tr>, <th>, <td>, dan style inline.
      * Jangan gunakan <html>, <head>, <body>, <meta>, <link>, atau <script>.
    - Jika user meminta INSERT/UPDATE/DELETE, jawab:
      "Jika ingin menambah atau mengubah data, silakan hubungi Tim BIS."
    """
)

promptFilter = PromptTemplate.from_template(
    """
    Kamu membantu mengubah pertanyaan menjadi query SQL untuk database nusanet_view
    atau mengembalikan "False" jika tidak relevan.

    Pertanyaan:
    {question}

    Database: nusanet_view
    Tabel:
    - service_internet
    - service_digital_business
    - invoice
    - internet_usage

    Kolom penting:
    service_internet:
      csid, cid, branch, account_name, status_code, status,
      date_registered, date_activated, date_blocked, date_blocked_until,
      date_terminated, is_free, is_blocked, service_type, service_price,
      month, period_start, period_end, service_code, service_name,
      service_group, service_location, service_location_coordinate

    service_digital_business:
      csid, cid, branch, account_name, status_code, status,
      date_registered, date_activated, date_blocked, date_blocked_until,
      date_terminated, is_free, is_blocked, service_type, service_price,
      month, period_start, period_end, service_code, service_name,
      service_group, domain, total_account, google_provisioning_id,
      google_payment_term, handle_by_whmcs

    invoice:
      id, cid, csid, description, created_at, amount, paid

    internet_usage:
      csid, date, bytes

    Relasi:
    - service_internet / service_digital_business ↔ invoice via csid/cid (amount berasal dari service_price + tax).
    - service_internet ↔ internet_usage via csid (untuk total pemakaian bytes).
    - Satuan price/amount = Rupiah.

    Aturan jawaban:
    1. Jika input sudah berupa query:
       - Perbaiki agar cocok dengan kolom di atas (tanpa kolom asing).
       - Kembalikan HANYA query SQL yang valid.
    2. Jika input adalah pertanyaan tentang data di atas:
       - Buat satu query SQL yang valid dan bisa dijalankan di nusanet_view.
       - Query harus bisa menghasilkan data yang bisa divisualisasikan atau dianalisis statistik.
       - Kembalikan HANYA query SQL, tanpa karakter lain.
    3. Jika pertanyaan tidak berkaitan dengan kolom/tabel di atas:
       - Jawab: False
    """
)

promptEmail = PromptTemplate.from_template(
    """
        Kamu akan membantu saya untuk mendapatkan email dari respon user yang diberikan.
        Adapun respon yang diberikan adalah: {response}
        Saya ingin hasil dari yang kamu berikan adalah email yang valid, jika tidak ada email pada respon tersebut, berikan response "Bukan Email".
        kemudian pastikan yang respon yang kamu berikan adalah email, jangan memberikan jawaban apapun selain email tersebut.
        """
)

promptVis = PromptTemplate.from_template(
    """
    Kamu adalah asisten visualisasi data.

    Data berikut dalam bentuk JSON/list of dict:
    {data}

    Tugas:
    1. Tentukan apakah data layak divisualisasikan:
       - Jika data cukup kompleks, memiliki pola, tren waktu, perbandingan kategori, outlier,
         atau berisi angka yang cocok jadi grafik → buat visualisasi.
       - Jika data sedikit, sederhana, atau tidak relevan untuk grafik → keluarkan "None".
    2. Jika perlu visualisasi, kembalikan HANYA JSON konfigurasi chart dengan format:
    {{
      "chartType": "...",
      "title": "...",
      "xKey": "...",
      "yKey": "...",
      "data": [...],
      "type": "Rupiah" | "Bukan Rupiah" | "Bytes"
    }}

    Aturan:
    - Jangan tambahkan teks lain di luar JSON atau "None".
    - chartType pilih berdasarkan pola data (bar/line/pie/doughnut/radar/scatter).
    - xKey gunakan kolom kategori atau tanggal.
    - yKey gunakan kolom numerik (boleh multi kolom → buat array of object).
    - Ubah angka string menjadi number.
    - Output harus valid JSON tanpa ``` atau penjelasan lain.

    Output:
    - JSON konfigurasi chart ATAU "None".
    """
)