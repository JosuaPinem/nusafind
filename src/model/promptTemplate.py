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
        csid
        cid
        branch
        account_name
        status_code
        status
        date_registered
        date_activated
        date_blocked
        date_blocked_until
        date_terminated
        is_free 
        is_blocked
        service_type
        service_price
        month
        period_start
        period_end
        service_code
        service_name
        service_group
        service_location
        service_location_coordinate

        Dalam tabel service_digital_business, terdapat kolom-kolom berikut:
        csid
        cid
        branch 
        account_name
        status_code
        status
        date_registered
        date_activated
        date_blocked
        date_blocked_until
        date_terminated
        is_free
        is_blocked
        service_type
        service_price
        month
        period_start
        period_end
        service_code 
        service_name
        service_group
        domain
        total_account
        google_provisioning_id
        google_payment_term
        handle_by_whmcs  

        Dalam tabel invoice, terdapat kolom-kolom berikut:
        cid
        csid
        description
        created_at
        amount
        paid

        pada tabel diatas, table service_internet dan service_digital_business memiliki relasi dengan tabel invoice melalui kolom csid dan cid dan akan mengambil data dari service_price untuk data amount pada tabel invoice namun perlu diingat terdapat penambahan tax.
        dan semua tabel sudah terelasi dengan baik. Tidak ada yang perlu diubah dari struktur tabel tersebut. Dan ingat setiap ada kata price dan amount itu satuannya rupiah.

        adapun pertanyaan yang diberikan adalah: {question}
        Buatlah query SQL yang valid untuk menjawab pertanyaan diatas.
        Pastikan query tersebut dapat dijalankan pada database nusanet_view.
        Jangan memberikan jawaban apapun selain query SQL yang valid. Dan jangan memberikan penambahan \n atau karakter lain selain query SQL tersebut.
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
    """
)