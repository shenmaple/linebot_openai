from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import requests

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text1 = event.message.text
    try:
        # 使用Ollama API调用phi4模型
        response = requests.post(
            'http://100.82.180.66:11434/api/generate',
            json={
                'model': 'phi4',
                'prompt': text1,
                'stream': False
            }
        )
        response_data = response.json()
        ret = response_data.get('response', '').strip()
        if not ret:
            ret = '发生错误：无法获取回复内容'
    except Exception as e:
        ret = f'发生错误：{str(e)}'
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
