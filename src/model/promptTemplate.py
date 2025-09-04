from langchain.prompts import PromptTemplate


promptConvertQuery =  PromptTemplate.from_template(
    """ 
        Kamu akan membantu saya untuk mengubah pertanyaan ini menjadi sebuah query SQL yang valid.
        Berikut saya berikan informasi mengani database yang akan digunakan:
        Nama database: nusanet_view
        Tabel yang tersedia:
        -service_internet
        -service_digital_business
        -invoice

        Dalam tabel service_internet, terdapat kolom-kolom berikut:
        csid, cid, branch, account_name, status_code, status, date_registered, date_activated, date_blocked, date_blocked_until, date_terminated, is_free, is_blocked, service_type,
        service_price, month, period_start, period_end, service_code, service_name, service_group, service_location, service_location_coordinate

        Dalam tabel service_digital_business, terdapat kolom-kolom berikut:
        csid, cid, branch, account_name, status_code, status, date_registered, date_activated, date_blocked, date_blocked_until, date_terminated
        is_free, is_blocked, service_type, service_price, month, period_start, period_end, service_code, service_name, service_group, domain, total_account, google_provisioning_id, google_payment_term, handle_by_whmcs  

        Dalam tabel invoice, terdapat kolom-kolom berikut:
        cid, csid, description, created_at, amount, paid

        pada tabel diatas, table service_internet dan service_digital_business memiliki relasi dengan tabel invoice melalui kolom csid dan cid dan akan mengambil data dari service_price untuk data amount pada tabel invoice namun perlu diingat terdapat penambahan tax.
        dan semua tabel sudah terelasi dengan baik. Tidak ada yang perlu diubah dari struktur tabel tersebut. Dan ingat setiap ada kata price dan amount itu satuannya rupiah.

        adapun pertanyaan yang diberikan adalah: {question}
        Buatlah query SQL yang valid untuk menjawab pertanyaan diatas.
        Pastikan query tersebut dapat dijalankan pada database nusanet_view.
        Jangan memberikan jawaban apapun selain query SQL yang valid. Dan jangan memberikan penambahan \n atau karakter lain selain query SQL tersebut.
        selain itu, persiapkan query tersebut yang bisa menghasilkan data yang bisa diolah menjadi sebuah visualisasi yang menarik. Jika tidak bisa, berikan analisis statistik mengenai data tersebut.
        Tambahan, jika yang dikirimkan adalah sebuah query, perbaiki query jadi format yang lebih baik, namun tetap berada pada konteks yang diinginkan oleh user.
    """
)


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
        Kamu akan membantu saya untuk memfilter data yang diberikan.
        {question}
        Respon dengan "True" hanya jika pertanyaan secara eksplisit menyebut kolom atau data yang ada di salah satu tabel di atas, sehingga query SQL bisa dibuat dari kolom-kolom tersebut. Jika pertanyaan tidak berkaitan dengan kolom/tabel tersebut, respon dengan "False".
        Dalam tabel service_internet, terdapat kolom-kolom berikut:
        csid, cid, branch, account_name, status_code, status, date_registered, date_activated, date_blocked, date_blocked_until, date_terminated, is_free, is_blocked, service_type,
        service_price, month, period_start, period_end, service_code, service_name, service_group, service_location, service_location_coordinate

        Dalam tabel service_digital_business, terdapat kolom-kolom berikut:
        csid, cid, branch, account_name, status_code, status, date_registered, date_activated, date_blocked, date_blocked_until, date_terminated
        is_free, is_blocked, service_type, service_price, month, period_start, period_end, service_code, service_name, service_group, domain, total_account, google_provisioning_id, google_payment_term, handle_by_whmcs  

        Dalam tabel invoice, terdapat kolom-kolom berikut:
        cid, csid, description, created_at, amount, paid

        Jika memungkinkan, anda hanya perlu merespon dengan "True" jika tidak, anda hanya perlu merespon dengan "False".
        Jangan memberikan jawaban apapun selain "True" atau "False". karena akan mengganggy proses selanjutnya.
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

promptFQ = PromptTemplate.from_template(
    """
        Kamu akan membantu saya untuk check apakah ini pesan berbentuk query atau tidak. Jika pesan yang di kirim adalah sebuah query silahkan jawab "Ya" jika tidak silahkan jawan "Tidak". 
        Jangan memberikan tambahan apapun selain jawaban yang diinstruksikan.
        adapun pesaanya adalah : {question}
    """
)