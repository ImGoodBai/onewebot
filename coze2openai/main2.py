from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import requests
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

coze_api_base = os.environ.get("COZE_API_BASE", "api.coze.cn")
default_bot_id = os.environ.get("BOT_ID", "")
bot_config = json.loads(os.environ.get("BOT_CONFIG", "{}"))
bot_key = os.environ.get("KEY", "")


@app.before_request
def handle_cors():
    if request.method == 'OPTIONS':
        return '', 204

@app.route("/", methods=['GET'])
def home():
    return """
    <html>
      <head>
        <title>COZE2OPENAI</title>
      </head>
      <body>
        <h1>Coze2OpenAI</h1>
        <p>Congratulations! Your project has been successfully deployed.</p>
      </body>
    </html>
    """

@app.route("/v1/chat/completions", methods=['POST'])
def chat_completions():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return jsonify({"code": 401, "errmsg": "Unauthorized."}), 401

    token = auth_header.split(" ")[1]
    if not token:
        return jsonify({"code": 401, "errmsg": "Unauthorized."}), 401
    token = bot_key
    data = request.json
    messages = data.get('messages', [])
    model = data.get('model', '')
    user = data.get('user', 'apiuser')
    chat_history = [
        {"role": msg['role'], "content": msg['content'], "content_type": "text"}
        for msg in messages[:-1]
    ]

    last_message = messages[-1]
    query_string = last_message['content']
    stream = data.get('stream', False)
    bot_id = bot_config.get(model, default_bot_id)

    request_body = {
        "query": query_string,
        "stream": False,
        "conversation_id": "",
        "user": user,
        "bot_id": bot_id,
        "chat_history": chat_history
    }
    print("##body: ")
    print(request_body)

    coze_api_url = f"https://{coze_api_base}/open_api/v2/chat"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.post(coze_api_url, headers=headers, json=request_body)
    print("##header: ")
    print(headers)

    if stream:
        def generate():
            try:
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        print("##stream line: ")
                        print(line)
                        yield line + '\n'
            except UnicodeDecodeError as e:
                print(f"Unicode decode error: {e}")
                yield 'Decoding error occurred\n'
            finally:
                print("##end of stream")
                yield 'END OF STREAM\n'  # 发送结束信号

        return Response(generate(), content_type="text/event-stream")
    else:
        print("##unstream return: ")
        try:
            data = response.json()
            print("##response json: ", data)

            if data.get('code') == 0 and data.get('msg') == "success":
                messages = data.get('messages', [])
                answer_message = next((msg for msg in messages if msg['role'] == 'assistant' and msg['type'] == 'answer'), None)

                if answer_message:
                    result = answer_message['content'].strip()
                    usage_data = {
                        "prompt_tokens": 100,
                        "completion_tokens": 10,
                        "total_tokens": 110,
                    }
                    chunk_id = f"chatcmpl-{int(time.time() * 1000)}"
                    chunk_created = int(time.time())

                    formatted_response = {
                        "id": chunk_id,
                        "object": "chat.completion",
                        "created": chunk_created,
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": result,
                                },
                                "logprobs": None,
                                "finish_reason": "stop",
                            },
                        ],
                        "usage": usage_data,
                        "system_fingerprint": "fp_2f57f81c11",
                    }
                    return jsonify(formatted_response)
                else:
                    return jsonify({"error": "No answer message found."}), 500
            else:
                print("Error:", data.get('msg'))
                return jsonify({
                    "error": "Unexpected response from Coze API.",
                    "message": data.get('msg')
                }), 500
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return jsonify({"error": "Error parsing JSON response."}), 500

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 3006)))
