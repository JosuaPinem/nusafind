from langchain.prompts import PromptTemplate

promptGetAnswer = PromptTemplate.from_template(
    """
        Kamu akan membantu saya untuk menjawab pertanyaan ini berdasarkan data yang didapat dari database.
        Berikut saya berikan informasi mengenai data yang diambil dari database:
        {rawData}

        dengan query SQL sebagai berikut:
        {query}

        Pertanyaan yang diberikan adalah: {question}
        Buatlah jawaban yang sesuai dengan pertanyaan diatas berdasarkan data yang diberikan.
        Pastikan jawaban tersebut sesuai dengan pertanyaan yang diberikan.
        Jangan memberikan jawaban apapun selain jawaban yang sesuai dengan pertanyaan tersebut.
        Jika Data tidak ditemukan, berikan jawaban permintaan maaf untuk data belum tersedia. Silahkan hubungi admin Nusafind.
        Kemudian berikan respon yang tidak punya simbol atau karakter lain.
        Setiap permintaan mengenai data mengenai service_price atau amount harus kamu buat dalam rupiah contoh Rp. 100.000,00
        Jika memungkinkan, buatkan data visualisasi yang menarik menggunakan html dan css. Ingat jangan membuat tag html, body, head, atau tag lainnya yang tidak perlu, gunakan table saja.
        Dan ingat jangan memberikan tag meta, link, atau script apapun. Dan untuk tablenya buat stylenya agar lebih menarik.
        Tolak jika user meminta insert data atau update data dengan respons: Jika ingin (menambah/ mengubah) data, silahkan hubungi Tim BIS;
    """
)


promptFilter = PromptTemplate.from_template(
    """
        Kamu akan membantu saya dalam memberikan respon False atau query dari pertanyaan berikut:
        {question}
        
        Berikut saya berikan informasi mengani database yang akan digunakan:
        Nama database: nusanet_view
        Tabel yang tersedia:
        -service_internet
        -service_digital_business
        -invoice
        -internet_usage

        Dalam tabel service_internet, terdapat kolom-kolom berikut:
        csid, cid, branch, account_name, status_code, status, date_registered, date_activated, date_blocked, date_blocked_until, date_terminated, is_free, is_blocked, service_type,
        service_price, month, period_start, period_end, service_code, service_name, service_group, service_location, service_location_coordinate

        Dalam tabel service_digital_business, terdapat kolom-kolom berikut:
        csid, cid, branch, account_name, status_code, status, date_registered, date_activated, date_blocked, date_blocked_until, date_terminated
        is_free, is_blocked, service_type, service_price, month, period_start, period_end, service_code, service_name, service_group, domain, total_account, google_provisioning_id, google_payment_term, handle_by_whmcs  

        Dalam tabel invoice, terdapat kolom-kolom berikut:
        cid, csid, description, created_at, amount, paid

        Dalam tabel internet_usage, terdapat kolom:
        csid, date, dan bytes

        pada tabel service_internet dan service_digital_business memiliki relasi dengan tabel invoice melalui kolom csid dan cid dan akan mengambil data dari service_price untuk data amount pada tabel invoice namun perlu diingat terdapat penambahan tax.
        pada tabel service_internet dan internate_usage memiliki relasi tabel yaitu csid yang dimana ini tujuannya mendapatkan informasi jumlah penggunaan bytes internet.
        dan semua tabel sudah terelasi dengan baik. Tidak ada yang perlu diubah dari struktur tabel tersebut. Dan ingat setiap ada kata price dan amount itu satuannya rupiah.

        
        Aturan kamu dalam menjawab:
        1. Jika pertanyaan user berupa query, silahkan periksa dan perbaiki query sesuai dengan kolom-kolom diatas. Dan ingat tanpa atribut lainnya.
        2. Jika pertanyaan user bukan berupa query dan berkaitan dengan database, silahkan konversi menjadi sebuah query sql dengan ketentuan:
            1. uatlah query SQL yang valid untuk menjawab pertanyaan diatas.
            2. Pastikan query tersebut dapat dijalankan pada database nusanet_view.
            3. Jangan memberikan jawaban apapun selain query SQL yang valid. Dan jangan memberikan penambahan \n atau karakter lain selain query SQL tersebut.
            4. selain itu, persiapkan query tersebut yang bisa menghasilkan data yang bisa diolah menjadi sebuah visualisasi yang menarik. Jika tidak bisa, berikan analisis statistik mengenai data tersebut.
            5. Tambahan, jika yang dikirimkan adalah sebuah query, perbaiki query jadi format yang lebih baik, namun tetap berada pada konteks yang diinginkan oleh user.
        3. Jika pertanyaan user tidak ada kaitan dengan salah satu kolom diatas, maka jawab "False" (tanpa petik atau atribut lain).
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
    '''
        Kamu adalah seorang asisten yang membantu membuat konfigurasi chart dari data yang diberikan.
        Berdasarkan data berikut: {data}, buatlah konfigurasi chart dalam format JSON dengan struktur berikut:
        {{
            "chartType": "bar" | "line" | "pie" | "doughnut" | "radar" | "scatter",  // Jenis chart
            "title": "Judul Chart",  // Judul chart
            "xKey": "nama_kolom_x",  // Nama kolom untuk sumbu X
            "yKey": "nama_kolom_y",  // Nama kolom untuk sumbu Y
            "data": [  // Data untuk chart
                {{"nama_kolom_x": "nilai1", "nama_kolom_y": nilai1}},
                {{"nama_kolom_x": "nilai2", "nama_kolom_y": nilai2}},
                ...
            ],
            "type": kamu tentukan tipe untuk kolom y yaitu "Rupiah" atau "Bukan Rupiah" atau "Bytes"
        }}

        Pastikan yang kamu kirimkan hanya JSON sesuai format diatas.
        Ingat ya tidak perlu memberikan atau menambahkan penjelasan, cukup membuat konfigurasi chart dalam format JSON sesuai instruksi diatas.
        Jika data ada memberikan nilai berupa angka dalam bentuk string, ubah menjadi number (tanpa tanda kutip).
        Ingat bahwa nilai yang diterima boleh int atau float.
        PENTING: untuk data, khususnya untuk kolom y, tidak wajib singel. Jika terdapat banyak kolom y, buatlah menjadi array of object.
        PENTING: Kamu tidak boleh memberikan jawaban yang memiliki kuitasi atau tanda ``` apapun.
    '''
)

promptCheckVis = PromptTemplate.from_template(
    '''
    Kamu adalah asisten cerdas yang membantu menentukan apakah data berikut perlu divisualisasikan atau tidak:

    Data:
    {data}

    Untuk menentukan hal tersebut, gunakan kriteria berikut:
    1. Data terlalu banyak atau kompleks untuk dibaca secara manual.
    2. Data memiliki pola/tren yang perlu dianalisis (misalnya tren waktu).
    3. Data yang perlu dibandingkan antar kategori/kelompok.
    4. Data berisi hubungan antar variabel yang sulit dijelaskan tanpa visual.
    5. Data mengandung potensi anomali/outlier yang lebih mudah dilihat secara visual.
    6. Data digunakan untuk pengambilan keputusan sehingga perlu ringkas dan jelas.
    7. Data perlu disampaikan kepada orang non-teknis atau dalam presentasi.
    8. Data merupakan time-series (berdasarkan waktu) dan lebih efektif divisualisasikan.

    Tugas kamu:
    - Tentukan apakah data tersebut perlu visualisasi atau tidak.
    - Jika dibutuhkan validasi silahkan respon True tanpa tambahan apapun.
    - Jika tidak membutuhkan visualisasi kembalikan None tanpa tambahan apapun.

    Jawaban:
    '''
)
