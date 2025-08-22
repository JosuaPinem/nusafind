from flask import Flask, jsonify
import mysql.connector
from db.connection import create_connection, create_local_connection
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from model.promptTemplate import promptConvertQuery, promptGetAnswer, promptFilter, promptEmail, promptFQ
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

def saveData(session_id, question, query, rawData, answer):
    conn = create_local_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO log (session_id, question, query, rawData, respons, time) VALUES (%s, %s, %s, %s, %s, NOW())",
            (session_id, question, query, str(rawData), answer)
        )
        conn.commit()
        cursor.execute(
        "INSERT INTO history (session_id, time, question, respons) VALUES (%s, NOW(), %s, %s)",
            (session_id, question, answer)  
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