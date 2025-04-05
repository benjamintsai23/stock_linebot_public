'''
Created by Tsung Yu on 17/03/2020.
Copyright © 2020 Tsung Yu. All rights reserved.
'''

import re
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

# 匯入功能模組
import EXRate
import news
import stockprice
import Institutional_Investors
import stock_compare
import new_famous_book
import kchart
import Technical_Analysis
import Technical_Analysis_test
import Fundamental_Analysis

from msg_template import Msg_Template, questionnaire, Msg_Exrate, Msg_News, Msg_diagnose, Msg_fundamental_ability

app = Flask(__name__)

# 設定 LINE CHANNEL 金鑰
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')
my_user_id = 'YOUR_USER_ID'
line_bot_api.push_message(my_user_id, TextSendMessage(text="🤖 LINE Bot 已啟動！"))

@app.route("/")
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = str(event.message.text).upper().strip()
    uid = event.source.user_id

    # 今日新聞功能
    if msg == "今日新聞":
        yahoo = Msg_News.yahoo_finance_news()
        cnyes = Msg_News.cnyes_tw_stock_news()
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text="📢 Yahoo 財經今日新聞："), yahoo])
        line_bot_api.push_message(uid, TextSendMessage(text="📢 鉅亨網台股新聞："))
        line_bot_api.push_message(uid, cnyes)
        return

    # 股票查詢 #2330
    if re.match('#[0-9]{4}', msg):
        stock_number = msg[1:]
        content_text = stockprice.getprice(stock_number, msg)
        content = Msg_Template.stock_reply(stock_number, content_text)
        line_bot_api.reply_message(event.reply_token, content)
        return

    # 股票走勢圖 P2330
    if re.match('P[0-9]{4}', msg):
        stock_number = msg[1:]
        img_url = stockprice.stock_trend(stock_number, msg)
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return

    # K 線圖查詢 K2330
    if re.match('K[0-9]{4}', msg):
        stock_number = msg[1:]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="📈 K 線圖繪製中..."))
        img_url = kchart.draw_kchart(stock_number)
        line_bot_api.push_message(uid, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return

    # 匯率查詢 外幣USD
    if re.match('外幣[A-Z]{3}', msg):
        currency = msg[2:5]
        text_message = EXRate.showCurrency(currency)
        content = Msg_Exrate.realtime_currency(text_message, currency)
        line_bot_api.reply_message(event.reply_token, content)
        return

    # 匯率圖 CTUSD
    if re.match('CT[A-Z]{3}', msg):
        currency = msg[2:5]
        cash_imgurl = EXRate.cash_exrate_sixMonth(currency)
        spot_imgurl = EXRate.spot_exrate_sixMonth(currency)
        messages = []
        if "http" in cash_imgurl:
            messages.append(ImageSendMessage(original_content_url=cash_imgurl, preview_image_url=cash_imgurl))
        if "http" in spot_imgurl:
            messages.append(ImageSendMessage(original_content_url=spot_imgurl, preview_image_url=spot_imgurl))
        if messages:
            line_bot_api.reply_message(event.reply_token, messages)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 查無匯率圖資料。"))
        return

    # 三大法人查詢 F2330
    if re.match('F[0-9]{4}', msg):
        stock_number = msg[1:]
        result = Institutional_Investors.institutional_investors(stock_number)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # 股票比較 比較2330/2317
    if msg.startswith("比較"):
        img_url = stock_compare.show_pic(msg)
        if img_url == "no":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 股票代碼錯誤"))
        else:
            line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))
        return

    # 未匹配到任何功能
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❓ 尚未讀取到，請輸入有效指令！"))

if __name__ == "__main__":
    app.run(debug=True)
