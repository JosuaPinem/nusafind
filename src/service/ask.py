from flask import Flask, jsonify
from model.model import createQuery, getRawData, createAnswer

class askService:
    def ask_service(self, question):
        query = createQuery(question)

        if query is None:
            return None
        
        rawData = getRawData(query)

        if rawData is None:
            return None
        
        answer = createAnswer(rawData, query, question)
        if answer is None:
            return None
        return answer, query
        
