from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/ping')
def chatbot_callback():
    a = int(request.args.get('a', 0))
    return jsonify({"pong": a})


@app.route('/api/chatfuel/gencode', methods=['GET'])
def chatfuel_gencode():
    return jsonify(request.args)
