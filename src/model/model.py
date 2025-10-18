from flask import Flask, jsonify
import mysql.connector
from db.connection import create_connection, create_local_connection
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from model.promptTemplate import promptConvertQuery, promptGetAnswer, promptFilter, promptEmail, promptFQ, promptVis
import os, sqlparse, json
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
# Ganti baris 11 di src/model/model.py  
os.environ["OPENAI_API_KEY"] = openai_api_key or "dummy-key-for-testing"
import re

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

def clean_sql(answer: str) -> str:
    # 1) ambil isi di dalam ```sql ... ``` atau ``` ... ```
    code = re.sub(r"```(?:sql)?\r?\n?([\s\S]*?)```", r"\1", answer).strip()

    # 2) normalisasi newline yang di-escape jadi newline beneran
    #    dan rapikan spasi ganda
    code = code.replace("\\n", "\n")
    code = re.sub(r"[ \t]+", " ", code).strip()

    # 3) format pakai sqlparse
    return sqlparse.format(
        code,
        reindent=True,           # tata letak & indentasi
        keyword_case="upper",    # SELECT, FROM, dsb jadi UPPERCASE
        strip_comments=False
    )

def fillterQuestion(question):
    reformat = promptFilter.format(question=question)
    answer = llm.invoke(
        reformat
    )
    return answer.content

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

def getMail(response):
    reformat = promptEmail.format(response=response)
    answer = llm.invoke(reformat)
    if answer.content.strip() == "Bukan Email":
        return None
    return answer.content.strip()

def saveData(session_id, question, query, rawData, answer, visualisasion):
    conn = create_local_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO log (session_id, question, query, rawData, respons, visualisasi, time) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (session_id, question, query, str(rawData), answer, visualisasion)
        )
        conn.commit()
        cursor.execute(
        "INSERT INTO history (session_id, time, question, respons, query, visualisasi) VALUES (%s, NOW(), %s, %s, %s, %s)",
            (session_id, question, answer, query, visualisasion)  
        )
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def isQuery(question):
    reformat = promptFQ.format(question = question)

    answer = llm.invoke(reformat)
    return answer.content

def Vis(data):
    reformat = promptVis.format(data = data)

    answer = llm.invoke(reformat)
    try:
        # Coba parse string JSON dari GPT
        parsed = json.loads(answer.content)
        return parsed, answer.content
    except json.JSONDecodeError as e:
        print("⚠️  Gagal parse chartConfig dari GPT:", e)
        print("Raw content:", answer.content)
        return None, None

if __name__ == "__main__":
    raw = """```sql
    SELECT i.cid, i.csid, i.description, i.created_at,
           (CASE WHEN i.paid = 1 THEN i.amount ELSE i.amount * 1.1 END) AS total_amount
    FROM invoice i JOIN service_internet si ON i.csid = si.csid
    WHERE MONTH(i.created_at) = 3 AND YEAR(i.created_at) = 2025
    ORDER BY total_amount DESC LIMIT 5;
    ```"""
    print(clean_sql(raw))