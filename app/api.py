from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/ping')
def chatbot_callback():
    a = int(request.args.get('a', 0))
    return jsonify({"pong": a})


@app.route('/api/chatfuel/gencode', methods=['GET', 'POST'])
def chatfuel_gencode():
    if not request.json:
        return jsonify({"error": "not a json"})
    return request.text
