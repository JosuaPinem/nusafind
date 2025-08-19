from flask import Flask, jsonify
import mysql.connector
from db.connection import create_connection
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_api_key
import re

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

def clean_sql(answer: str) -> str:
    # hapus ```sql ... ``` wrapper
    query = re.sub(r"```(?:sql)?\n?([\s\S]*?)```", r"\1", answer).strip()
    return query.replace("\\n", " ").replace("\n", " ").strip()



def createQuery(question):
    if not question:
        return None
    reformat = promptConvertQuery.format(question=question)

    answer = llm.invoke(
       reformat
    )

    return clean_sql(answer.content)

def getRawData(query):
    conn = create_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        rawData = cursor.fetchall()
        return rawData
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def createAnswer(rawData, query, question):
    reformat = promptGetAnswer.format(
        rawData=rawData,
        query=query,
        question=question
    )
    answer = llm.invoke(
        reformat
    )
    return answer.content


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
    """
)