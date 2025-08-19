from flask import Flask, jsonify

def check_input(body):
    if not body or 'question' not in body:
        return None
    return body