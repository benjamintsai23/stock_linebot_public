'''
LINE Bot 主程式 - 可部署精簡版（v1）
僅保留 webhook 結構與基本回應，確保 LINE 驗證通過
部署成功後再逐步加回其他功能模組
'''

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# TODO: 請填入你的 LINE Bot Channel Access Token 與 Secret
LINE_CHANNEL_ACCESS_TOKEN = '你的 access token'
LINE_CHANNEL_SECRET = '你的 secret key'

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/")
def home():
    return "LINE Bot is running."

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    reply_msg = f"你說的是：{user_msg}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_msg)
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

