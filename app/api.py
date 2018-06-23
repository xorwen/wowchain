from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/ping')
def chatbot_callback():
    a = int(request.args.get('a', 0))
    return jsonify({"pong": a})


@app.route('/api/chatfuel/gencode', methods=['GET', 'POST'])
def chatfuel_gencode():
    if not request.json:
        print("received no json")
        print(request.get_data(as_text=True))
        return jsonify({})
    print("Received this json", request.json)
    return jsonify(request.json)
